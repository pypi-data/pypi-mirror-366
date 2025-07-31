__all__ = ['fix_invalidities', 'fix_invalidities_db_refs',
           'fix_invalidities_agent', 'fix_invalidities_context',
           'fix_invalidities_stmt', 'fix_invalidities_evidence']

import re
import copy
from typing import List, Mapping
from indra.databases.identifiers import ensure_prefix_if_needed as \
    ensure_prefix_if_needed_identifiers
from indra.databases.identifiers import identifiers_registry
from indra.databases.bioregistry_client import ensure_prefix_if_needed as \
    ensure_prefix_if_needed_bioregistry
from indra.statements.validate import text_ref_patterns
from indra.statements import Evidence, Statement, Agent, BioContext, \
    Translocation


def fix_invalidities(stmts: List[Statement]) -> List[Statement]:
    """Fix invalidities in a list of Statements.

    Note that in some cases statements can be filtered out if there is a known
    issue to which there is no fix, e.g., a Translocation statements
    missing both location parameters.

    Parameters
    ----------
    stmts :
        A list of INDRA Statements.

    Returns
    -------
    :
        The list of statements with invalidities fixed.
    """
    new_stmts = []
    for stmt in stmts:
        if isinstance(stmt, Translocation) and not stmt.from_location and \
                not stmt.to_location:
            continue
        fix_invalidities_stmt(stmt)
        new_stmts.append(stmt)
    return new_stmts


def fix_invalidities_stmt(stmt: Statement):
    """Fix invalidities of a single INDRA Statement in place."""
    for ev in stmt.evidence:
        fix_invalidities_evidence(ev)
    for agent in stmt.real_agent_list():
        fix_invalidities_agent(agent)


def fix_invalidities_evidence(ev: Evidence):
    """Fix invalidities of a single INDRA Evidence in place."""
    for k, v in copy.deepcopy(ev.text_refs).items():
        if v is None:
            ev.text_refs.pop(k, None)
        elif not k.isupper():
            ev.text_refs.pop(k)
            ev.text_refs[k.upper()] = v

    if ev.pmid and not re.match(text_ref_patterns['PMID'], ev.pmid):
        ev.pmid = None
    if ev.text_refs.get('PMID') and not re.match(text_ref_patterns['PMID'],
                                                 ev.text_refs['PMID']):
        ev.text_refs.pop('PMID', None)

    if ev.pmid is None and ev.text_refs.get('PMID') is not None:
        ev.pmid = ev.text_refs['PMID']
    elif ev.text_refs.get('PMID') is None and ev.pmid is not None:
        ev.text_refs['PMID'] = ev.pmid

    if 'DOI' in ev.text_refs and not re.match(text_ref_patterns['DOI'],
                                              ev.text_refs['DOI']):
        ev.text_refs.pop('DOI', None)
    if 'PMC' in ev.text_refs and not re.match(text_ref_patterns['PMC'],
                                              ev.text_refs['PMC']):
        ev.text_refs.pop('PMC', None)

    if ev.context is not None:
        fix_invalidities_context(ev.context)


def fix_invalidities_agent(agent: Agent):
    """Fix invalidities of a single INDRA Agent in place."""
    agent.db_refs = fix_invalidities_db_refs(agent.db_refs)


def fix_invalidities_db_refs(db_refs: Mapping[str, str]) -> Mapping[str, str]:
    """Return a fixed version of a db_refs grounding dict."""
    if 'PUBCHEM' in db_refs and \
            db_refs['PUBCHEM'].startswith('CID'):
        db_refs['PUBCHEM'] = \
            db_refs['PUBCHEM'].replace('CID:', '').strip()

    db_refs = {k: v for k, v in db_refs.items()
               if v is not None}

    for k, v in copy.deepcopy(db_refs).items():
        if k == 'CHEMBL' and not v.startswith('CHEMBL'):
            db_refs[k] = 'CHEMBL%s' % v
        elif k == 'ECCODE':
            db_refs['ECCODE'] = db_refs['ECCODE'].replace('.-', '')
        elif k == 'UNIPROT':
            db_refs.pop(k)
            # This is really a location
            if v.startswith('SL-'):
                db_refs['UPLOC'] = v
            # Otherwise we just fix the invalid key
            else:
                db_refs['UP'] = v
        elif k == 'UP':
            # There are cases where this is an empty string
            if not v.strip():
                db_refs.pop('UP', None)
            # Sometimes we have two IDs separated by a comma
            if ',' in v:
                db_refs['UP'] = v.split(',')[0]
            if v.startswith('SL-'):
                db_refs['UPLOC'] = db_refs.pop('UP')
            # There are cases where an isoform is under the UP key, we
            # standardize these. Note that the elif here is important to
            # avoid matching SL- here
            elif '-' in v:
                parts = v.split('-')
                db_refs['UP'] = parts[0]
                db_refs['UPISO'] = v
        elif k == 'UAZ':
            db_refs.pop('UAZ')
            if v.startswith('CVCL'):
                db_refs['CVCL'] = v
        elif k == 'TAXONOMY' and v == '-1':
            db_refs.pop('TAXONOMY', None)
        elif k == 'LINCS' and re.match(r'\d+-\d+', v):
            db_refs['HMS-LINCS'] = db_refs.pop('LINCS')
        elif k == 'CVCL' and re.match(r'^[A-Z0-9]{4}$', v):
            db_refs['CVCL'] = 'CVCL_%s' % v
        elif k == 'CO':
            db_refs['CL'] = 'CL:%s' % db_refs.pop('CO')
        elif k == 'FPLX' and '-' in v:
            db_refs['FPLX'] = v.replace('-', '_')
        elif k == 'DRUGBANK' and v.startswith('DBSALT'):
            db_refs['DRUGBANK.SALT'] = db_refs.pop('DRUGBANK')
        # For MGI and RGD some sources added names as IDs that are invalid
        # and not easily fixable without reverse lookups so we rather
        # remove these.
        elif k == 'MGI' and not re.match(
                identifiers_registry['mgi']['pattern'], v):
            db_refs.pop('MGI', None)
        elif k == 'RGD' and not re.match(
                identifiers_registry['rgd']['pattern'], v):
            db_refs.pop('RGD', None)
        # These were left over from RLIMS-P where they denote MESH IDs so
        # we can remove and replace these.
        elif k == 'CTD':
            if 'MESH' in db_refs:
                db_refs.pop('CTD')
            else:
                db_refs['MESH'] = db_refs.pop('CTD')
        else:
            # Since
            new_val = ensure_prefix_if_needed_identifiers(k, v)
            new_val = ensure_prefix_if_needed_bioregistry(k, new_val)
            db_refs[k] = new_val
    return db_refs


def fix_invalidities_context(context: BioContext):
    """Fix invalidities of a single INDRA BioContext in place."""
    entries = [context.species, context.cell_line, context.disease,
               context.cell_type, context.organ, context.location]
    for entry in entries:
        if entry is not None:
            entry.db_refs = fix_invalidities_db_refs(entry.db_refs)