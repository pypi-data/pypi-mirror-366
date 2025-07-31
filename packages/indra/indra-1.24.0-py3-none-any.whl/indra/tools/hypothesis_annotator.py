"""This module exposes functions that annotate websites (including
PubMed and PubMedCentral pages, or any other text-based website) with INDRA
Statements through hypothes.is. Features include reading the content of the
website 'de-novo', and generating new INDRA Statements for annotation, and
fetching existing statements for a paper from the INDRA DB and using
those for annotation."""
import logging
import requests
from indra.sources import indra_db_rest
from indra.literature import pubmed_client
from indra.pipeline import AssemblyPipeline
from indra.statements import stmts_from_json
from indra.sources.hypothesis import upload_statement_annotation

logger = logging.getLogger(__name__)


def annotate_paper_from_db(text_refs, assembly_pipeline=None):
    """Upload INDRA Statements as annotations for a given paper based on content
    for that paper in the INDRA DB.

    Parameters
    ----------
    text_refs : dict
        A dict of text references, following the same format as
        the INDRA Evidence text_refs attribute.
    assembly_pipeline : Optional[json]
        A list of pipeline steps (typically filters) that are applied
        before uploading statements to hypothes.is as annotations.
    """
    ref_priority = ['TRID', 'PMCID', 'PMID']
    for ref_ns in ref_priority:
        ref_id = text_refs.get(ref_ns)
        if ref_id:
            break
    else:
        logger.info('Could not find appropriate text refs')
        return
    ip = indra_db_rest.get_statements_for_paper([(ref_ns.lower(), ref_id)])
    stmts = ip.statements
    # Cut down evidences to ones just from this paper
    for stmt in stmts:
        stmt.evidence = [ev for ev in stmt.evidence if
                         ev.text_refs.get(ref_ns) == ref_id]
    if assembly_pipeline:
        ap = AssemblyPipeline(assembly_pipeline)
        stmts = ap.run(stmts)

    logger.info('Uploading %d statements to hypothes.is' % len(stmts))
    for stmt in stmts:
        upload_statement_annotation(stmt, annotate_agents=True)


def read_and_annotate(text_refs, text_extractor=None,
                      text_reader=None, assembly_pipeline=None):
    """Read a paper/website and upload annotations derived from it to
    hypothes.is.

    Parameters
    ----------
    text_refs : dict
        A dict of text references, following the same format as
        the INDRA Evidence text_refs attribute.
    text_extractor : Optional[function]
        A function which takes the raw content of a website (e.g., HTML)
        and extracts clean text from it to prepare for machine reading.
        This is only used if the text_refs is a URL (e.g., a Wikipedia page),
        it is not used for PMID or PMCID text_refs where content can be
        pre-processed and machine read directly. Default: None
        Example: html2text.HTML2Text().handle
    text_reader : Optional[function]
        A function which takes a single text string argument (the
        text extracted from a given resource), runs reading on it, and
        returns a list of INDRA Statement objects. Due to complications with
        the PMC NXML format, this option only supports URL or PMID resources
        as input in text_refs. Default: None. In the
        default case, the INDRA REST API is called with an appropriate
        endpoint that runs Reach and processes its output into INDRA
        Statements.
    assembly_pipeline : Optional[json]
        A list of assembly pipeline steps that are applied before uploading
        statements to hypothes.is as annotations.
        Example: [{'function': 'map_grounding'}]
    """
    api_url = 'http://api.indra.bio:8000/reach/'
    ref_priority = ['PMCID', 'PMID', 'URL'] if not text_reader \
        else ['PMID', 'URL']
    for ref_ns in ref_priority:
        ref_id = text_refs.get(ref_ns)
        if ref_id:
            break
    else:
        logger.info('Could not find appropriate text refs')
        return
    logger.info('Selected the following paper ID: %s:%s' % (ref_ns, ref_id))
    # Get text content and the read the text
    if ref_ns == 'PMCID':
        res = requests.post(api_url + 'process_pmc', json={'pmc_id': ref_id})
        stmts = stmts_from_json(res.json().get('statements'))
    elif ref_ns == 'PMID':
        abstract = pubmed_client.get_abstract(ref_id)
        if not abstract:
            logger.info('Could not get abstract from PubMed')
            return
        logger.info('Got abstract')
        if text_reader:
            stmts = text_reader(abstract)
        else:
            res = requests.post(api_url + 'process_text', json={'text': abstract})
            stmts = stmts_from_json(res.json().get('statements'))
    elif ref_ns == 'URL':
        site_content = requests.get(ref_id).text
        if not site_content:
            logger.info('Could not get content from website')
            return
        if text_extractor:
            text = text_extractor(site_content)
            logger.info('Extracted text of length %d from site content' %
                        len(text))
        else:
            text = site_content
        if text_reader:
            stmts = text_reader(text)
        else:
            res = requests.post(api_url + 'process_text', json={'text': text})
            stmts = stmts_from_json(res.json().get('statements'))
    else:
        return

    logger.info('Got %d statements from reading' % len(stmts))
    if not stmts:
        return

    if assembly_pipeline:
        ap = AssemblyPipeline(assembly_pipeline)
        stmts = ap.run(stmts)

    logger.info('Uploading %d statements to hypothes.is' % len(stmts))
    for stmt in stmts:
        for ev in stmt.evidence:
            if ref_ns == 'PMID':
                ev.pmid = ref_id
            ev.text_refs[ref_ns] = ref_id
        upload_statement_annotation(stmt, annotate_agents=True)
