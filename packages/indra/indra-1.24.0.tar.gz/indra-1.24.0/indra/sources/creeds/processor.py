# -*- coding: utf-8 -*-

"""Processors for CREEDS data."""

from copy import copy
import logging
from typing import (
    Any,
    ClassVar,
    Iterable,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
)

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from indra import statements
from indra.databases import hgnc_client
from indra.ontology.bio import bio_ontology
from indra.ontology.standardize import get_standard_agent
from indra.sources.utils import Processor
from indra.statements import Agent, BioContext, Evidence, RefContext, Statement
from protmapper import uniprot_client
from protmapper.uniprot_client import get_id_from_mgi_name, get_id_from_rgd_name


logger = logging.getLogger(__name__)

__all__ = [
    "CREEDSGeneProcessor",
    "CREEDSChemicalProcessor",
    "CREEDSDiseaseProcessor",
]


#: Organism label to NCBI Taxonomy Identifier
ORGANISMS = {
    "mouse": "10090",
    "human": "9606",
    "rat": "10116",
}
#: A mapping from labels used in CREEDS for species to their
#: organism-specific nomenclature name
ORGANISMS_TO_NS = {
    "mouse": "MGI",
    "human": "HGNC",
    "rat": "RGD",
}
#: A mapping of strings used in the "pert_type" entries in
#: CREEDS data to normalized keys. Several are not curated
#: because they do not readily map to an INDRA statement
PERTURBATIONS = {
    # knockout
    "ko": "knockout",
    "deletion": "knockout",
    "null mutation": "knockout",
    # knockdown
    "kd": "knockdown",
    "deficiency (mutation)": "knockdown",
    "silencing": "knockdown",
    "heterozygotic knockout (nf1+/-)": "knockout",
    "shrna": "knockdown",
    # increase
    "induction": "increase",
    "knock-in": "increase",
    "oe": "increase",
    "overexpression": "increase",
    "stimulation of gene product": "increase",
    # activation
    "agonist activation": "activation",
    "drugactivation": "activation",
    "activemutant": "activation",
    "activation (deltanb-cateniner transgenics)": "activation",
    # inhibition
    "druginhibition": "inhibition",
    "drug inhibition": "inhibition",
    "inhibition": "inhibition",
    "inactivation  (ikk inhibition)": "inhibition",
    "deficiency": "inhibition",
    "depletion": "inhibition",
    "depletion - sirna simut12": "inhibition",
    "small molecule inhibition": "inhibition",
    "defectivemutant": "inhibition",
    "inactivation": "inhibition",
    "drug": "inhibition",
    # misc
    "mutant": "mutation",
    "rd1 mutation": "mutation",
    "natural variation": "mutation",
    "mutation (htt exon1  142q)": "mutation",
    "g93a mutation": "mutation",
}

#: A mapping of perturbation types to statement types for the target
#: genes whose gene expression increases from the given perturbation
#: of the subject gene
UP_MAP: Mapping[str, Type[statements.RegulateAmount]] = {
    "knockout": statements.DecreaseAmount,
    "knockdown": statements.DecreaseAmount,
    "inhibition": statements.DecreaseAmount,
    "increase": statements.IncreaseAmount,
    "activation": statements.IncreaseAmount,
}
#: A mapping of perturbation types to statement types for the target
#: genes whose gene expression decreases from the given perturbation
#: of the subject gene
DOWN_MAP: Mapping[str, Type[statements.RegulateAmount]] = {
    "knockout": statements.IncreaseAmount,
    "knockdown": statements.IncreaseAmount,
    "inhibition": statements.IncreaseAmount,
    "increase": statements.DecreaseAmount,
    "activation": statements.DecreaseAmount,
}


def _process_pert_type(s: str) -> str:
    x = s.strip().lower()
    return PERTURBATIONS.get(x, x)


MISSING_NAMES = set()


def _get_genes(
    record: Mapping[str, Any],
    prefix: str,
    key: str,
) -> List[Tuple[str, str, str]]:
    rv = []
    #: A list of 2-tuples with the gene symbol then the expression value
    expressions = record[key]
    for symbol, _ in expressions:
        if prefix == "HGNC":
            current_id = hgnc_client.get_current_hgnc_id(symbol)
            # We may get no current IDs or more than one current IDs
            # in which case we skip this gene
            if not current_id or isinstance(current_id, list):
                identifier = None
            else:
                identifier = current_id
            _prefix = "HGNC"
        elif prefix == "MGI":
            _prefix, identifier = "UP", get_id_from_mgi_name(symbol)
        elif prefix == "RGD":
            _prefix, identifier = "UP", get_id_from_rgd_name(symbol)
        else:
            raise ValueError(f"Invalid prefix: {prefix} ! {symbol}")
        if identifier is None:
            if (prefix, symbol) not in MISSING_NAMES:
                logger.debug(
                    f"Could not look up {symbol} by name in {prefix}",
                )
                MISSING_NAMES.add((prefix, symbol))
            continue
        rv.append((_prefix, identifier, symbol))
    return rv


def _get_evidence(record: Mapping[str, Any]) -> Evidence:
    # TODO how to use the following metadata?
    geo_id = record["geo_id"]
    cell_type = record["cell_type"]
    organism = record["organism"]
    return Evidence(
        source_api="creeds",
        annotations={
            # TODO use Gilda for grounding and put in BioContext?
            "cell_type": cell_type,
            "geo": geo_id,
        },
        context=BioContext(
            species=RefContext(
                name=organism,
                db_refs={"TAXONOMY": ORGANISMS[organism]},
            )
        ),
    )


def _get_regulations(
    record: Mapping[str, Any],
) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str, str]]]:
    organism = record["organism"]
    prefix = ORGANISMS_TO_NS[organism]
    up_genes = _get_genes(record, prefix, "up_genes")
    down_genes = _get_genes(record, prefix, "down_genes")
    return up_genes, down_genes


def _process_record_helper(
    record, subject, up_stmt_cls, down_stmt_cls
) -> Iterable[Statement]:
    up_genes, down_genes = _get_regulations(record)
    evidence = _get_evidence(record)
    for prefix, identifier, name in up_genes:
        target = get_standard_agent(name, {prefix: identifier})
        yield up_stmt_cls(subject, target, copy(evidence))
    for prefix, identifier, name in down_genes:
        target = get_standard_agent(name, {prefix: identifier})
        yield down_stmt_cls(subject, target, copy(evidence))


class CREEDSProcessor(Processor):
    """A base processor for CREEDS, which takes records as input."""

    #: The processed statements (after ``extract_statements()`` is run)
    statements: List[Statement]

    def __init__(self, records: List[Mapping[str, Any]]):
        self.records = records
        self.statements = []

    def extract_statements(self) -> List[Statement]:
        """Generate/store statements if not pre-cached, then return then."""
        if not self.statements:
            self.statements = list(self.iter_statements())
        return self.statements

    def iter_statements(self) -> Iterable[Statement]:
        for record in tqdm(self.records, desc=f"Processing {self.name}"):
            yield from self.process_record(record)

    @classmethod
    def process_record(cls, record: Mapping[str, Any]) -> Iterable[Statement]:
        raise NotImplementedError


LOGGED_MISSING_PART = set()


class CREEDSGeneProcessor(CREEDSProcessor):
    """A processor for single gene perturbation experiments in CREEDS."""

    name = "creeds_gene"

    @staticmethod
    def get_subject(record) -> Optional[Agent]:
        ncbigene_id = record["id"][len("gene:") :]
        uniprot_id = uniprot_client.get_id_from_entrez(ncbigene_id)
        if uniprot_id is None:
            logger.debug(f"Could not convert ncbigene:{ncbigene_id} to UniProt")
            return None
        name = uniprot_client.get_gene_name(uniprot_id)
        return get_standard_agent(
            name,
            {
                "EGID": ncbigene_id,
                "UP": uniprot_id,
            },
        )

    @classmethod
    def process_record(cls, record: Mapping[str, Any]) -> Iterable[Statement]:
        subject = cls.get_subject(record)
        if subject is None:
            return

        pert_type = _process_pert_type(record["pert_type"])
        up_stmt_cls = UP_MAP.get(pert_type)
        down_stmt_cls = DOWN_MAP.get(pert_type)
        if up_stmt_cls is None or down_stmt_cls is None:
            if pert_type not in LOGGED_MISSING_PART:
                logger.debug(f"Could not look up pert_type {record['pert_type']}")
                LOGGED_MISSING_PART.add(pert_type)
            return

        yield from _process_record_helper(
            record,
            subject,
            up_stmt_cls,
            down_stmt_cls,
        )


class CREEDSDiseaseProcessor(CREEDSProcessor):
    """A processor for disease perturbation experiments in CREEDS."""

    name = "creeds_disease"

    @staticmethod
    def get_subject(record) -> Agent:
        db_refs = {}
        doid = record["do_id"]
        if doid:
            db_refs["DOID"] = doid
        umls_id = record["umls_cui"]
        if umls_id:
            db_refs["UMLS"] = umls_id
        name = record["disease_name"]
        return get_standard_agent(name, db_refs)

    @classmethod
    def process_record(cls, record) -> Iterable[Statement]:
        subject = cls.get_subject(record)
        yield from _process_record_helper(
            record,
            subject,
            up_stmt_cls=statements.IncreaseAmount,
            down_stmt_cls=statements.DecreaseAmount,
        )


class CREEDSChemicalProcessor(CREEDSProcessor):
    """A processor for chemical perturbation experiments in CREEDS."""

    name = "creeds_chemical"

    @staticmethod
    def get_subject(record) -> Agent:
        db_refs = {}
        smiles = record["smiles"]
        if smiles:
            db_refs["SMILES"] = smiles
        pubchem_compound_id = record["pubchem_cid"]
        if pubchem_compound_id:
            db_refs["PUBCHEM"] = str(pubchem_compound_id)
        drugbank_id = record["drugbank_id"]
        if drugbank_id:
            db_refs["DRUGBANK"] = drugbank_id
        name = record["drug_name"]
        return get_standard_agent(name, db_refs)

    @classmethod
    def process_record(cls, record) -> Iterable[Statement]:
        subject = cls.get_subject(record)
        yield from _process_record_helper(
            record,
            subject,
            up_stmt_cls=statements.IncreaseAmount,
            down_stmt_cls=statements.DecreaseAmount,
        )
