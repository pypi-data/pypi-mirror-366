from typing import Union

from indra.statements import *
from indra.ontology.bio import bio_ontology
from indra.databases.hgnc_client import get_hgnc_id
from indra.ontology.standardize import get_standard_agent

rel_mapping = {
    'CATALYSIS': Activation,
    'INHIBITION': Inhibition,
    'HETERODIMER_ASSOCIATION': Complex,
    'CATALYSIS;HETERODIMER_ASSOCIATION': Complex
}


class AcsnProcessor:
    """Processes Atlas of cancer signalling network (ACSN) relationships
    into INDRA statements

    Attributes
    ----------
    relations_df : pandas.DataFrame
        A tab-separated data frame which consists of binary relationship between
        proteins with PMIDs.
    correspondence_dict : dict
        A dictionary with correspondences between ACSN entities and their
        HGNC symbols.
    """
    def __init__(self, relations_df, correspondence_dict):
        """Constructor for AcsnProcessor class"""
        self.relations_df = relations_df
        self.correspondence_dict = correspondence_dict
        self.fplx_lookup = _make_famplex_lookup()
        self.statements = []

    def extract_statements(self):
        """Return INDRA Statements Extracted from ACSN relations."""
        for _, row in self.relations_df.iterrows():
            acsn_agent_a, stmt_types, acsn_agent_b, pmids = list(row)
            stmt_type = get_stmt_type(stmt_types)
            if stmt_type:
                agent_a = self.get_agent(acsn_agent_a)
                agent_b = self.get_agent(acsn_agent_b)
                if agent_a and agent_b:
                    if str(pmids) == 'nan':
                        evs = [Evidence(source_api='acsn')]

                    else:
                        evs = [Evidence(source_api='acsn', pmid=pmid)
                               for pmid in pmids.split(';')]

                    if stmt_type == Complex:
                        stmt = stmt_type([agent_a, agent_b], evidence=evs)
                    else:
                        stmt = stmt_type(agent_a, agent_b, evidence=evs)

                    self.statements.append(stmt)

    def get_agent(self, acsn_agent: str) -> Union[Agent, None]:
        """Return an INDRA Agent corresponding to an ACSN agent.

        Parameters
        ----------
        acsn_agent :
            Agent extracted from the relations statement data frame

        Returns
        -------
        :
            Returns INDRA agent with HGNC or FamPlex ID in db_refs. If there
            are no groundings available, we return None.
        """
        mapping = self.correspondence_dict.get(acsn_agent)
        if not mapping:
            return None
        if len(mapping) == 1:
            hgnc_id = get_hgnc_id(mapping[0])
            if hgnc_id:
                db_refs = {'HGNC': hgnc_id}
                return get_standard_agent(mapping[0], db_refs=db_refs)
        else:
            fplx_rel = self.fplx_lookup.get(tuple(sorted(
                self.correspondence_dict[acsn_agent])))
            if fplx_rel:
                db_refs = {'FPLX': fplx_rel}
                return get_standard_agent(fplx_rel, db_refs=db_refs)
        return None


def get_stmt_type(stmt_type: str) -> Union[None, Statement]:
    """Return INDRA statement type from ACSN relation.

    Parameters
    ----------
    stmt_type :
        An ACSN relationship type

    Returns
    -------
    :
        INDRA equivalent of the ACSN relation type or None if a mappings
        is not available.
    """
    if stmt_type in rel_mapping:
        mapped_stmt_type = rel_mapping[stmt_type]
        return mapped_stmt_type


def _make_famplex_lookup():
    """Create a famplex lookup dictionary.

    Keys are sorted tuples of HGNC gene names and values are
    the corresponding FamPlex ID.
    """

    fplx_lookup = {}
    bio_ontology.initialize()
    for node in bio_ontology.nodes:
        ns, id = bio_ontology.get_ns_id(node)
        if ns == 'FPLX':
            children = bio_ontology.get_children(ns, id)
            hgnc_children = [bio_ontology.get_name(*c)
                             for c in children if c[0] == 'HGNC']
            fplx_lookup[tuple(sorted(hgnc_children))] = id
    return fplx_lookup
