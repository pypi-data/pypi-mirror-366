import logging
from indra.ontology.standardize import get_standard_name
from indra.ontology.bio import bio_ontology
from indra.statements import *
from .minerva_client import get_ids_to_refs, default_map_name
from .id_mapping import indra_db_refs_from_minerva_refs


logger = logging.getLogger(__name__)


class SifProcessor:
    """Processor that extracts INDRA Statements from SIF strings.

    Parameters
    ----------
    model_id_to_sif_strs : dict
        A dictionary mapping a model ID (int) to a list of strings in SIF
        format. Example: {799: ['csa2 POSITIVE sa9', 'csa11 NEGATIVE sa30']}
    map_name : str
        A name of a disease map to process.

    Attributes
    ----------
    statements : list[indra.statements.Statement]
        A list of INDRA Statements extracted from the SIF strings.
    """
    def __init__(self, model_id_to_sif_strs, map_name=default_map_name):
        self.model_id_to_sif_strs = model_id_to_sif_strs
        self.map_name = map_name
        self.statements = []

    def extract_statements(self):
        for model_id, sif_strs in self.model_id_to_sif_strs.items():
            self.statements += self.process_model(model_id, sif_strs)
        logger.info('Got %d total statements from %d models'
                    % (len(self.statements), len(self.model_id_to_sif_strs)))

    def process_model(self, model_id, sif_strs):
        logger.info('Processing model %d' % model_id)
        ids_to_refs, complex_members = get_ids_to_refs(model_id, self.map_name)
        stmts = []
        for sif_str in sif_strs:
            stmt = self.get_stmt(sif_str, ids_to_refs, complex_members,
                                 model_id)
            if stmt:
                stmts.append(stmt)
        logger.info('Got %d statements from model %d' % (len(stmts), model_id))
        return stmts

    def get_stmt(self, sif_str, ids_to_refs, complex_members, model_id):
        if sif_str.startswith('#') or sif_str == '':
            return
        clean_str = sif_str.strip('\n')
        subj_id, rel_type, obj_id = clean_str.split(' ')
        subj = get_agent(subj_id, ids_to_refs, complex_members)
        obj = get_agent(obj_id, ids_to_refs, complex_members)
        if rel_type == 'POSITIVE':
            stmt = Activation(subj, obj)
        elif rel_type == 'NEGATIVE':
            stmt = Inhibition(subj, obj)
        else:
            raise ValueError('Unknown relation type: %s' % rel_type)
        evid = Evidence(source_api='minerva',
                        annotations={'sif_str': sif_str,
                                     'minerva_model_id': model_id})
        stmt.evidence = [evid]
        return stmt


def get_agent(element_id, ids_to_refs, complex_members):
    """Get an agent for a MINERVA element.

    Parameters
    ----------
    element_id : str
        ID of an element used in MINERVA API and raw SIF files.
    ids_to_refs : dict
        A dictionary mapping element IDs to MINERVA provided references. Note
        that this mapping is unique per model (same IDs can be mapped to
        different refs in different models).
    complex_members : dict
        A dictionary mapping element ID of a complex element to element IDs of
        its members.

    Returns
    -------
    agent : indra.statements.agent.Agent
        INDRA agent created from given refs.
    """
    # Get references from MINERVA and filter to accepted namespaces
    exclude_ns = {'WIKIPATHWAYS', 'PUBMED', 'HGNC_SYMBOL', 'INTACT', 'PDB',
                  'DOI'}
    refs = ids_to_refs.get(element_id)
    db_refs = indra_db_refs_from_minerva_refs(refs)
    filtered_refs = {db_ns: db_id for (db_ns, db_id) in db_refs.items()
                     if db_ns not in exclude_ns}
    # If it's a complex and doesn't have complex level grounding
    if element_id in complex_members and len(filtered_refs) == 1:
        # Sort to always have the same main agent
        member_ids = complex_members[element_id]
        agents = [get_agent(member_id, ids_to_refs, complex_members)
                  for member_id in member_ids]
        agents = sorted(agents, key=lambda ag: ag.name)
        # Try to get a FamPlex family
        fam = get_family(agents)
        if fam:
            # Combine TEXT from MINERVA and found FPLX ID
            filtered_refs['FPLX'] = fam
            return get_agent_from_refs(filtered_refs)
        # Otherwise treat a list of agents as an agent with bound conditions
        else:
            main_agent = agents[0]
            if len(agents) > 1:
                for ag in agents[1:]:
                    main_agent.bound_conditions.append(BoundCondition(ag))
            return main_agent
    # Now we have either individual agents or complexes with complex level
    # grounding (e.g. from GO, MESH, UNIPROT)
    else:
        return get_agent_from_refs(filtered_refs)


def get_family(agents):
    """Get a FamPlex family if all of its members are given."""
    family_sets = []
    ag_groundings = []
    for ag in agents:
        gr = ag.get_grounding()
        ag_groundings.append(gr)
        parents = bio_ontology.get_parents(*gr)
        families = {p for p in parents if p[0] == 'FPLX'}
        family_sets.append(families)
    common_families = family_sets[0].intersection(*family_sets)
    if not common_families:
        return
    for fam in common_families:
        children = bio_ontology.get_children(*fam)
        # Check if all family members are present
        if set(children) == set(ag_groundings):
            return fam[1]


def get_agent_from_refs(db_refs):
    """Get an agent given its db_refs."""
    name = get_standard_name(db_refs)
    if not name:
        name = db_refs.get('TEXT')
    if name and db_refs:
        return Agent(name, db_refs=db_refs)
