"""This module contains a library of functions that are
useful for building custom preassembly logic for some applications.
They are typically used as matches_fun or refinement_fun arguments
to the Preassembler and other modules."""
import logging
from indra.statements import *
from indra.pipeline import register_pipeline


logger = logging.getLogger(__name__)


@register_pipeline
def agent_grounding_matches(agent):
    """Return an Agent matches key just based on grounding, not state."""
    if agent is None:
        return None
    return str(agent.entity_matches_key())


@register_pipeline
def agents_stmt_type_matches(stmt):
    """Return a matches key just based on Agent grounding and Stmt type."""
    agents = [agent_grounding_matches(a) for a in stmt.agent_list()]
    key = str((stmt.__class__.__name__, agents))
    return key


@register_pipeline
def agent_name_matches(agent):
    """Return a sorted, normalized bag of words as the name."""
    if agent is None:
        return None
    bw = '_'.join(sorted(list(set(agent.name.lower().split()))))
    return bw


@register_pipeline
def agent_name_stmt_type_matches(stmt):
    """Return True if the statement type and normalized agent name matches."""
    agents = [agent_name_matches(a) for a in stmt.agent_list()]
    key = str((stmt.__class__.__name__, agents))
    return key


@register_pipeline
def agent_name_stmt_matches(stmt):
    """Return the normalized agent names."""
    agents = [ag.name for ag in stmt.real_agent_list()]
    key = str(agents)
    return key


@register_pipeline
def agent_name_polarity_matches(stmt, sign_dict):
    """Return a key for normalized agent names and polarity."""
    agents = [ag.name for ag in stmt.real_agent_list()]
    if isinstance(stmt, Influence):
        stmt_pol = stmt.overall_polarity()
        if stmt_pol == 1:
            pol = 0
        elif stmt_pol == -1:
            pol = 1
        else:
            pol = None
    else:
        pol = sign_dict.get(type(stmt).__name__)
    if not pol:
        logger.debug('Unknown polarity for %s' % type(stmt).__name__)
    key = str((agents, pol))
    return key
