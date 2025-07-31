import logging
import networkx as nx
import pandas as pd
from .net import IndraNet, default_sign_dict
from indra.statements import *
from indra.tools import assemble_corpus as ac
from indra.preassembler.custom_preassembly import agent_name_stmt_matches, \
    agent_name_polarity_matches
from itertools import permutations
from collections import OrderedDict, defaultdict
from functools import partial


logger = logging.getLogger(__name__)
NS_PRIORITY_LIST = (
    'FPLX', 'HGNC', 'UP', 'CHEBI', 'GO', 'MESH', 'HMDB', 'PUBCHEM')


def get_ag_ns_id(ag):
    """Return a tuple of name space, id from an Agent's db_refs."""
    for ns in NS_PRIORITY_LIST:
        if ns in ag.db_refs:
            return ns, ag.db_refs[ns]
    return 'TEXT', ag.name


class IndraNetAssembler:
    """Assembler to create an IndraNet object from a list of INDRA statements.

    Parameters
    ----------
    statements : list[indra.statements.Statement]
        A list of INDRA Statements to be assembled.

    Attributes
    ----------
    model : IndraNet
        An IndraNet graph object assembled by this class.
    """

    def __init__(self, statements=None):
        self.statements = statements if statements else []
        self.model = None

    def add_statements(self, stmts):
        """Add INDRA Statements to the assembler's list of statements.

        Parameters
        ----------
        stmts : list[indra.statements.Statement]
            A list of :py:class:`indra.statements.Statement`
            to be added to the statement list of the assembler.
        """
        self.statements += stmts

    def make_model(self, method='preassembly', exclude_stmts=None,
                   complex_members=3, graph_type='multi_graph', sign_dict=None,
                   belief_flattening=None, belief_scorer=None,
                   weight_flattening=None, extra_columns=None,
                   keep_self_loops=True):
        """Assemble an IndraNet graph object.

        Parameters
        ----------
        method : str
            Method for assembling an IndraNet graph. Accepted values: `df` and
            `preassembly`. With the `df` method, the statements are converted
            into pandas DataFrame first where each row corresponds to an edge
            in unflattened MultiDiGraph IndraNet. Then the IndraNet can be
            flattened into signed and unsigned graphs. The beliefs can be
            calculated on the new edges by providing belief_flattening
            function. With the `preassembly` option, the statements are merged
            together and the beliefs are calculated by leveraging the
            preassembly functionality with custom matches functions
            (the matches functions are applied depending on the graph type).
            This method ensures the more robust belief calculation.
        exclude_stmts : list[str]
            A list of statement type names to not include in the graph.
        complex_members : int
            Maximum allowed size of a complex to be included in the graph.
            All complexes larger than complex_members will be rejected. For
            accepted complexes, all permutations of their members will be added
            as edges. Default is `3`.
        graph_type : str
            Specify the type of graph to assemble. Chose from 'multi_graph'
            (default), 'digraph', 'signed'. Default is `multi_graph`.
        sign_dict : dict
            A dictionary mapping a Statement type to a sign to be used for
            the edge. This parameter is only used with the 'signed' option.
            See IndraNet.to_signed_graph for more info.
        belief_flattening : str or function(networkx.DiGraph, edge)
            Only needed when method is set to `df`.
            The method to use when updating the belief for the flattened edge.

            If a string is provided, it must be one of the predefined options
            'simple_scorer' or 'complementary_belief'.

            If a function is provided, it must take the flattened graph 'G'
            and an edge 'edge' to perform the belief flattening on and return
            a number:

            >>> def belief_flattening(G, edge):
            ...     # Return the average belief score of the constituent edges
            ...     all_beliefs = [s['belief']
            ...         for s in G.edges[edge]['statements']]
            ...     return sum(all_beliefs)/len(all_beliefs)

        belief_scorer : Optional[indra.belief.BeliefScorer]
            Only needed when method is set to `preassembly`.
            Instance of BeliefScorer class to use in calculating edge
            probabilities. If None is provided (default), then the default
            scorer is used.
        weight_flattening : function(networkx.DiGraph)
            A function taking at least the graph G as an argument and
            returning G after adding edge weights as an edge attribute to the
            flattened edges using the reserved keyword 'weight'.

            Example:

            >>> def weight_flattening(G):
            ...     # Sets the flattened weight to the average of the
            ...     # inverse source count
            ...     for edge in G.edges:
            ...         w = [1/s['evidence_count']
            ...             for s in G.edges[edge]['statements']]
            ...         G.edges[edge]['weight'] = sum(w)/len(w)
            ...     return G

        keep_self_loops : Optional[bool]
            Whether to keep the self-loops when constructing the graph.

        Returns
        -------
        model : IndraNet
            IndraNet graph object.
        """
        logger.info('Assembling %s model with %s method'
                    % (graph_type, method))
        if method == 'df':
            return self.make_model_from_df(
                exclude_stmts=exclude_stmts, complex_members=complex_members,
                graph_type=graph_type, sign_dict=sign_dict,
                belief_flattening=belief_flattening,
                weight_flattening=weight_flattening,
                extra_columns=extra_columns,
                keep_self_loops=keep_self_loops)
        elif method == 'preassembly':
            return self.make_model_by_preassembly(
                exclude_stmts=exclude_stmts, complex_members=complex_members,
                graph_type=graph_type, sign_dict=sign_dict,
                belief_scorer=belief_scorer,
                weight_flattening=weight_flattening,
                extra_columns=extra_columns,
                keep_self_loops=keep_self_loops)

    def make_model_from_df(self, exclude_stmts=None, complex_members=3,
                           graph_type='multi_graph', sign_dict=None,
                           belief_flattening=None, weight_flattening=None,
                           extra_columns=None, keep_self_loops=True):
        """Assemble an IndraNet graph object by constructing a pandas
        Dataframe first.

        Parameters
        ----------
        exclude_stmts : list[str]
            A list of statement type names to not include in the graph.
        complex_members : int
            Maximum allowed size of a complex to be included in the graph.
            All complexes larger than complex_members will be rejected. For
            accepted complexes, all permutations of their members will be added
            as edges. Default is `3`.
        graph_type : str
            Specify the type of graph to assemble. Chose from 'multi_graph'
            (default), 'digraph', 'signed'. Default is `multi_graph`.
        sign_dict : dict
            A dictionary mapping a Statement type to a sign to be used for
            the edge. This parameter is only used with the 'signed' option.
            See IndraNet.to_signed_graph for more info.
        belief_flattening : str or function(networkx.DiGraph, edge)
            The method to use when updating the belief for the flattened edge.

            If a string is provided, it must be one of the predefined options
            'simple_scorer' or 'complementary_belief'.

            If a function is provided, it must take the flattened graph 'G'
            and an edge 'edge' to perform the belief flattening on and return
            a number:

            >>> def belief_flattening(G, edge):
            ...     # Return the average belief score of the constituent edges
            ...     all_beliefs = [s['belief']
            ...         for s in G.edges[edge]['statements']]
            ...     return sum(all_beliefs)/len(all_beliefs)

        weight_flattening : function(networkx.DiGraph)
            A function taking at least the graph G as an argument and
            returning G after adding edge weights as an edge attribute to the
            flattened edges using the reserved keyword 'weight'.

            Example:

            >>> def weight_flattening(G):
            ...     # Sets the flattened weight to the average of the
            ...     # inverse source count
            ...     for edge in G.edges:
            ...         w = [1/s['evidence_count']
            ...             for s in G.edges[edge]['statements']]
            ...         G.edges[edge]['weight'] = sum(w)/len(w)
            ...     return G

        keep_self_loops : Optional[bool]
            Whether to keep the self-loops when constructing the graph.

        Returns
        -------
        model : IndraNet
            IndraNet graph object.
        """
        df = self.make_df(exclude_stmts, complex_members, extra_columns,
                          keep_self_loops)
        if graph_type == 'multi_graph':
            model = IndraNet.from_df(df)
        elif graph_type == 'digraph':
            model = IndraNet.digraph_from_df(
                df=df,
                flattening_method=belief_flattening,
                weight_mapping=weight_flattening
            )
        elif graph_type == 'signed':
            model = IndraNet.signed_from_df(df, sign_dict=sign_dict,
                                            flattening_method=belief_flattening,
                                            weight_mapping=weight_flattening)
        else:
            raise TypeError('Have to specify one of \'multi_graph\', '
                            '\'digraph\' or \'signed\' when providing graph '
                            'type.')
        return model

    def make_df(self, exclude_stmts=None, complex_members=3,
                extra_columns=None, keep_self_loops=True):
        """Create a dataframe containing information extracted from assembler's
        list of statements necessary to build an IndraNet.

        Parameters
        ----------
        exclude_stmts : list[str]
            A list of statement type names to not include in the dataframe.
        complex_members : int
            Maximum allowed size of a complex to be included in the
            data frame. All complexes larger than complex_members will be
            rejected. For accepted complexes, all permutations of their
            members will be added as dataframe records. Default is `3`.
        extra_columns : list[tuple(str, function)]
            A list of tuples defining columns to add to the dataframe in
            addition to the required columns. Each tuple contains the column
            name and a function to generate a value from a statement.
        keep_self_loops : Optional[bool]
            Whether to keep the self-loops when constructing the graph.

        Returns
        -------
        df : pd.DataFrame
            Pandas DataFrame object containing information extracted from
            statements. It contains the following columns:

            *agA_name*
                The first Agent's name.
            *agA_ns*
                The first Agent's identifier namespace as per `db_refs`.
            *agA_id*
                The first Agent's identifier as per `db_refs`
            *ags_ns, agB_name, agB_id*
                As above for the second agent. Note that the Agent may be None
                (and these fields left empty) if the Statement consists only
                of a single Agent (e.g., SelfModification, ActiveForm,
                or Translocation statement).
            *stmt_type*
                Statement type, given by the name of the class
                in indra.statements.
            *evidence_count*
                Number of evidences for the statement.
            *stmt_hash*
                An unique long integer hash identifying the content of the
                statement.
            *belief*
                The belief score associated with the statement.
            *source_counts*
                The number of evidences per input source for the statement.
            *residue*
                If applicable, the amino acid residue being modified. NaN if
                if it is unknown or unspecified/not applicable.
            *position*
                If applicable, the position of the modified amino acid. NaN
                if it is unknown or unspecified/not applicable.
            *initial_sign*
                The default sign (polarity) associated with the given
                statement if the statement type has implied polarity.
                To facilitate weighted path finding, the sign is represented
                as 0 for positive polarity and 1 for negative polarity.

            More columns can be added by providing the extra_columns parameter.
        """
        rows = []
        col_names = ['agA_name', 'agB_name', 'agA_ns', 'agA_id',
                     'agB_ns', 'agB_id', 'residue', 'position',
                     'stmt_type', 'evidence_count', 'stmt_hash',
                     'belief', 'source_counts', 'initial_sign'] + \
            ([col_name for col_name, _ in extra_columns] if extra_columns else [])
        for stmt in self.statements:
            rows += statement_to_rows(stmt, exclude_stmts=exclude_stmts,
                                      complex_members=complex_members,
                                      extra_columns=extra_columns,
                                      keep_self_loops=keep_self_loops)
        df = pd.DataFrame(rows, columns=col_names, dtype=object)
        df = df.where((pd.notnull(df)), None)
        return df

    def make_model_by_preassembly(self, exclude_stmts=None, complex_members=3,
                                  graph_type='multi_graph', sign_dict=None,
                                  belief_scorer=None, weight_flattening=None,
                                  extra_columns=None, keep_self_loops=True):
        """Assemble an IndraNet graph object by preassembling the statements
        according to selected graph type.

        Parameters
        ----------
        exclude_stmts : list[str]
            A list of statement type names to not include in the graph.
        complex_members : int
            Maximum allowed size of a complex to be included in the graph.
            All complexes larger than complex_members will be rejected. For
            accepted complexes, all permutations of their members will be added
            as edges. Default is `3`.
        graph_type : str
            Specify the type of graph to assemble. Chose from 'multi_graph'
            (default), 'digraph', 'signed'. Default is `multi_graph`.
        sign_dict : dict
            A dictionary mapping a Statement type to a sign to be used for
            the edge. This parameter is only used with the 'signed' option.
            See IndraNet.to_signed_graph for more info.
        belief_scorer : Optional[indra.belief.BeliefScorer]
            Instance of BeliefScorer class to use in calculating edge
            probabilities. If None is provided (default), then the default
            scorer is used.
        weight_flattening : function(networkx.DiGraph)
            A function taking at least the graph G as an argument and
            returning G after adding edge weights as an edge attribute to the
            flattened edges using the reserved keyword 'weight'.

            Example:

            >>> def weight_flattening(G):
            ...     # Sets the flattened weight to the average of the
            ...     # inverse source count
            ...     for edge in G.edges:
            ...         w = [1/s['evidence_count']
            ...             for s in G.edges[edge]['statements']]
            ...         G.edges[edge]['weight'] = sum(w)/len(w)
            ...     return G

        keep_self_loops : Optional[bool]
            Whether to keep the self-loops when constructing the graph.

        Returns
        -------
        model : IndraNet
            IndraNet graph object.
        """
        # Filter out statements with one agent or with None subject
        stmts = [stmt for stmt in self.statements
                 if len(stmt.real_agent_list()) > 1]
        if exclude_stmts:
            exclude_types = tuple(
                get_statement_by_name(st_type) for st_type in exclude_stmts)
            stmts = [stmt for stmt in stmts
                     if not isinstance(stmt, exclude_types)]
        # Store edge data in statement annotations
        stmts = _store_edge_data(stmts, extra_columns)
        if graph_type == 'signed':
            if not sign_dict:
                sign_dict = default_sign_dict
            graph_stmts = []
            # Only keep statements with explicit signs
            for stmt_type in sign_dict:
                graph_stmts += ac.filter_by_type(stmts, stmt_type)
            graph_stmts += ac.filter_by_type(stmts, Influence)
            # Conversion statements can also be turned into two types of signed
            conv_stmts = ac.filter_by_type(stmts, Conversion)
            for stmt in conv_stmts:
                if stmt.subj:
                    for obj in stmt.obj_from:
                        graph_stmts.append(
                            DecreaseAmount(stmt.subj, obj, stmt.evidence))
                    for obj in stmt.obj_to:
                        graph_stmts.append(
                            IncreaseAmount(stmt.subj, obj, stmt.evidence))
            # Merge statements by agent name and polarity
            graph_stmts = ac.run_preassembly(
                graph_stmts, return_toplevel=False,
                belief_scorer=belief_scorer,
                matches_fun=partial(agent_name_polarity_matches,
                                    sign_dict=sign_dict),
                run_refinement=False)
            G = nx.MultiDiGraph()
        elif graph_type in ['digraph', 'multi_graph']:
            # Keep Complex and Conversion aside
            complex_stmts = ac.filter_by_type(stmts, Complex)
            conv_stmts = ac.filter_by_type(stmts, Conversion)
            graph_stmts = [stmt for stmt in stmts if stmt not in complex_stmts
                           and stmt not in conv_stmts]
            for stmt in complex_stmts:
                agents = stmt.real_agent_list()
                if len(agents) > complex_members:
                    continue
                for a, b in permutations(agents, 2):
                    graph_stmts.append(IncreaseAmount(a, b, stmt.evidence))
            for stmt in conv_stmts:
                if stmt.subj:
                    for obj in stmt.obj_from:
                        graph_stmts.append(
                            DecreaseAmount(stmt.subj, obj, stmt.evidence))
                    for obj in stmt.obj_to:
                        graph_stmts.append(
                            IncreaseAmount(stmt.subj, obj, stmt.evidence))
            if graph_type == 'digraph':
                # Merge statements by agent names
                graph_stmts = ac.run_preassembly(
                    graph_stmts, return_toplevel=False,
                    belief_scorer=belief_scorer,
                    matches_fun=agent_name_stmt_matches,
                    run_refinement=False)
                G = nx.DiGraph()
            else:
                G = nx.MultiGraph()
        for stmt in graph_stmts:
            agents = stmt.agent_list()
            # Filter out self-loops
            if not keep_self_loops and agents[0].name == agents[1].name:
                continue
            for ag in agents:
                ag_ns, ag_id = get_ag_ns_id(ag)
                G.add_node(ag.name, ns=ag_ns, id=ag_id)
            # We merged some different statements together based on their
            # agent names and polarity, we can retrieve the original
            # statements data back from annotations
            unique_stmts = {}
            for evid in stmt.evidence:
                edge_data = evid.annotations['indranet_edge']
                if edge_data['stmt_hash'] not in unique_stmts:
                    unique_stmts[edge_data['stmt_hash']] = edge_data
            statement_data = list(unique_stmts.values())
            if graph_type == 'signed':
                if isinstance(stmt, Influence):
                    stmt_pol = stmt.overall_polarity()
                    if stmt_pol == 1:
                        sign = 0
                    elif stmt_pol == -1:
                        sign = 1
                    else:
                        continue
                else:
                    sign = sign_dict[type(stmt).__name__]
                G.add_edge(agents[0].name, agents[1].name, sign,
                           statements=statement_data, belief=stmt.belief,
                           sign=sign)
            elif graph_type == 'digraph':
                G.add_edge(agents[0].name, agents[1].name,
                           statements=statement_data, belief=stmt.belief)
            else:
                if statement_data:
                    edge_data = statement_data[0]
                else:
                    edge_data = _get_edge_data(stmt, extra_columns)
                G.add_edge(agents[0].name, agents[1].name, **edge_data)
        if weight_flattening:
            G = weight_flattening(G)
        return G


def _get_source_counts(stmt):
    source_counts = defaultdict(int)
    for ev in stmt.evidence:
        source_counts[ev.source_api] += 1
    return dict(source_counts)


def _get_edge_data(stmt, extra_columns=None):
    stmt_type = type(stmt).__name__
    try:
        res = stmt.residue
    except AttributeError:
        res = None
    try:
        pos = stmt.position
    except AttributeError:
        pos = None
    edge_data = {
        'residue': res,
        'position': pos,
        'stmt_type': stmt_type,
        'evidence_count': len(stmt.evidence),
        'stmt_hash': stmt.get_hash(refresh=True),
        'belief': stmt.belief,
        'source_counts': _get_source_counts(stmt)
    }
    if extra_columns:
        for col_name, func in extra_columns:
            edge_data[col_name] = func(stmt)
    return edge_data


def _store_edge_data(stmts, extra_columns=None):
    for stmt in stmts:
        edge_data = _get_edge_data(stmt, extra_columns)
        for evid in stmt.evidence:
            evid.annotations['indranet_edge'] = edge_data
    return stmts


def statement_to_rows(stmt, exclude_stmts=None, complex_members=3,
                      extra_columns=None, keep_self_loops=True):
    rows = []
    if exclude_stmts:
        exclude_types = tuple(
            get_statement_by_name(st_type) for st_type in exclude_stmts)
    else:
        exclude_types = ()
    # Exclude statements from given exclude list
    if isinstance(stmt, exclude_types):
        logger.debug('Skipping a statement of a type %s.'
                     % type(stmt).__name__)
        return []
    not_none_agents = stmt.real_agent_list()

    # Exclude statements with less than 2 agents
    if len(not_none_agents) < 2:
        return []
    # Special handling for Influences and Associations
    if isinstance(stmt, (Influence, Association)):
        stmt_pol = stmt.overall_polarity()
        if stmt_pol == 1:
            sign = 0
        elif stmt_pol == -1:
            sign = 1
        else:
            sign = None
        if isinstance(stmt, Influence):
            edges = [(stmt.subj.concept, stmt.obj.concept, sign)]
        else:
            edges = [(a, b, sign) for a, b in
                     permutations(not_none_agents, 2)]
    # Handle complexes by creating pairs of their
    # not-none-agents.
    elif isinstance(stmt, Complex):
        # Do not add complexes with more members than complex_members
        if len(not_none_agents) > complex_members:
            logger.debug('Skipping a complex with %d members.'
                         % len(not_none_agents))
            return []
        else:
            # add every permutation with a neutral polarity
            edges = [(a, b, None) for a, b in
                     permutations(not_none_agents, 2)]
    elif isinstance(stmt, Conversion):
        edges = []
        if stmt.subj:
            for obj in stmt.obj_from:
                edges.append((stmt.subj, obj, 1))
            for obj in stmt.obj_to:
                edges.append((stmt.subj, obj, 0))
    # This is for any remaining statement type that may not be
    # handled above explicitly but somehow has more than two
    # not-none-agents at this point
    elif len(not_none_agents) > 2:
        return []
    else:
        edges = [(not_none_agents[0], not_none_agents[1], None)]
    for (agA, agB, sign) in edges:
        # Filter out self-loops
        if not keep_self_loops and agA.name == agB.name:
            continue
        agA_ns, agA_id = get_ag_ns_id(agA)
        agB_ns, agB_id = get_ag_ns_id(agB)
        stmt_type = type(stmt).__name__
        try:
            res = stmt.residue
        except AttributeError:
            res = None
        try:
            pos = stmt.position
        except AttributeError:
            pos = None
        # Create a simple flat list of just the values instead
        # of a dict with keys
        row = [
            agA.name,
            agB.name,
            agA_ns,
            agA_id,
            agB_ns,
            agB_id,
            res,
            pos,
            stmt_type,
            len(stmt.evidence),
            stmt.get_hash(refresh=True),
            stmt.belief,
            _get_source_counts(stmt),
            sign
        ]
        if extra_columns:
            for _, func in extra_columns:
                row.append(func(stmt))
        rows.append(row)
    return rows
