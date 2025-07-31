__all__ = ['path_sign_to_signed_nodes', 'signed_nodes_to_signed_edge',
           'get_sorted_neighbors', 'get_subgraph', 'Node', 'Edge',
           'EdgeFilter', 'SendType']
import logging
import networkx as nx
import functools

from typing import List, Tuple, Union, Optional, Callable, Set

logger = logging.getLogger(__name__)


# Derived type hints
Node = Union[str, Tuple[str, int]]
Edge = Tuple[Node, Node]
EdgeFilter = Callable[[nx.DiGraph, Node, Node], bool]
SendType = Tuple[Optional[Set[Node]], Optional[Set[Edge]]]


def path_sign_to_signed_nodes(source, target, edge_sign):
    """Translates a signed edge or path to valid signed nodes

    Pairs with a negative source node are filtered out.

    Parameters
    ----------
    source : str|int
        The source node
    target : str|int
        The target node
    edge_sign : int
        The sign of the edge

    Returns
    -------
    sign_tuple : (a, sign), (b, sign)
        Tuple of tuples of the valid combination of signed nodes
    """
    # Sign definitions: + == 0, - == 1
    # + path -> (a+, b+)
    # - path -> (a+, b-)
    # (a-, b-) and (a-, b+) are also technically valid but not in this context
    try:
        if int(edge_sign) == 0:
            return (source, 0), (target, 0)
        else:
            return (source, 1), (target, 0)
    except ValueError:
        logger.warning('Invalid sign %s when translating edge sign to int'
                       % edge_sign)
        return (None, None), (None, None)


def signed_nodes_to_signed_edge(source, target):
    """Create the triple (node, node, sign) from a pair of signed nodes

    Assuming source, target forms an edge of signed nodes:
    edge = (a, sign), (b, sign), return the corresponding signed edge triple

    Parameters
    ----------
    source : tuple(str|int, sign)
        A valid signed node
    target : tuple(str|int, sign)
        A valid signed node

    Returns
    -------
    tuple
        A tuple, (source, target, sign), representing the corresponding
        signed edge.
    """
    # Sign definitions: + == 0, - == 1
    # + edge/path -> (a+, b+) and (a-, b-)
    # - edge/path -> (a-, b+) and (a+, b-)
    source_name, source_sign = source
    target_name, target_sign = target
    try:
        if int(source_sign) == int(target_sign):
            return source_name, target_name, 0
        else:
            return source_name, target_name, 1
    except ValueError:
        logger.warning('Error translating signed nodes to signed edge using '
                       '(%s, %s)' % (source, target))
        return None, None, None


def get_sorted_neighbors(
        G: nx.DiGraph,
        node: Node,
        reverse: bool,
        force_edges: Optional[List[Edge]] = None,
        edge_filter: Optional[EdgeFilter] = None
) -> List[Node]:
    """Filter and sort neighbors of a node in descending order by belief

    Parameters
    ----------
    G
        A networkx DiGraph
    node
        A valid node name or signed node name
    reverse
        Indicates direction of search. Neighbors are either successors
        (downstream search) or predecessors (reverse search).
    force_edges
        A list of allowed edges. If provided, only allow neighbors that
        can be reached by the allowed edges.
    edge_filter
        If provided, must be a function that takes three arguments: a graph
        g, and the nodes u, v of the edge between u and v. The function must
        return a boolean. The function must return True if the edge is
        allowed, otherwise False.

    Returns
    -------
    List[Node]
        A list of nodes representing the filtered and sorted neighbors
    """
    # Check for edge filtering
    if force_edges or edge_filter:
        neigh_edges = G.in_edges if reverse else G.out_edges
        ix = 0 if reverse else 1
        edges = set(neigh_edges(node))
        if force_edges:
            edges = edges.intersection(set(force_edges))

        if edge_filter:
            neighbors = (e[ix] for e in edges if edge_filter(G, *e))
        else:
            neighbors = (e[ix] for e in edges)

    # No edge filtering applied
    else:
        neighbors = G.predecessors(node) if reverse else G.successors(node)

    # Return neighbors sorted by the edge belief
    if reverse:
        return sorted(neighbors,
                      key=lambda n: G.edges[n, node].get('belief', 0),
                      reverse=True)
    else:
        return sorted(neighbors,
                      key=lambda n: G.edges[node, n].get('belief', 0),
                      reverse=True)


def get_subgraph(g, edge_filter_func):
    """Get a subgraph of original graph filtered by a provided function."""
    logger.info('Getting subgraph with %s function' % edge_filter_func)
    view = nx.subgraph_view(
        g, filter_edge=functools.partial(edge_filter_func, g))
    # Copying to get a graph object instead of view
    new_g = view.copy()
    return new_g
