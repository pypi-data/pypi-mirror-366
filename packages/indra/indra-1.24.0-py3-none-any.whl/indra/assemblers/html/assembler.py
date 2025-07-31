"""
Format a set of INDRA Statements into an HTML-formatted report which also
supports curation.
"""
import re
import uuid
import logging
import itertools
from html import escape
from typing import Union, Dict, Optional
from collections import OrderedDict, defaultdict
from os.path import abspath, dirname, join

from jinja2 import Environment, FileSystemLoader

from indra.statements import *
from indra.sources import SOURCE_INFO
from indra.statements.agent import default_ns_order
from indra.statements.validate import validate_id
from indra.databases.identifiers import get_identifiers_url, ensure_prefix
from indra.assemblers.english import EnglishAssembler, AgentWithCoordinates
from indra.util.statement_presentation import group_and_sort_statements, \
    make_top_level_label_from_names_key, make_stmt_from_relation_key, \
    all_sources, get_available_source_counts, \
    get_available_ev_counts, standardize_counts, get_available_beliefs, \
    make_standard_stats, internal_source_mappings, available_sources_stmts,\
    available_sources_src_counts, reverse_source_mappings, \
    SourceColors
from indra.literature import id_lookup

logger = logging.getLogger(__name__)
HERE = dirname(abspath(__file__))

# Derived types
SourceInfo = Dict[str, Dict[str, Union[str, Dict[str, str]]]]


loader = FileSystemLoader(join(HERE, 'templates'))
env = Environment(loader=loader)

default_template = env.get_template('indra/statements_view.html')

DB_TEXT_COLOR = 'black'
"""The text color for database sources when shown as source count badges"""

READER_TEXT_COLOR = 'white'
"""The text color for reader sources when shown as source count badges"""


def _source_info_to_source_colors(
        source_info: Optional[SourceInfo] = None
) -> SourceColors:
    """Returns a source color data structure with source names as they
    appear in INDRA DB
    """
    if source_info is None:
        source_info = SOURCE_INFO
        every_source = all_sources
    else:
        every_source = []
        for source in source_info:
            every_source.append(source)

    # Initialize dicts for source: background-color for readers and databases
    database_colors = {}
    reader_colors = {}
    for source in every_source:
        # Get name as it is registered in source_info.json and get info
        src_info_name = reverse_source_mappings.get(source, source)
        info = source_info.get(src_info_name)
        if not info:
            logger.error('Source info missing for %s' % source)
            continue
        # Get color from info
        color = info['default_style']['background-color']

        # Map back to db name, use original name from all_sources as default
        mapped_source = internal_source_mappings.get(src_info_name, source)
        if info['type'] == 'reader':
            reader_colors[mapped_source] = color
        else:
            database_colors[mapped_source] = color

    return [('databases', {'color': DB_TEXT_COLOR,
                           'sources': database_colors}),
            ('reading', {'color': READER_TEXT_COLOR,
                         'sources': reader_colors})]


DEFAULT_SOURCE_COLORS = _source_info_to_source_colors(SOURCE_INFO)


def generate_source_css(fname: str,
                        source_colors: SourceColors = None):
    """Save a stylesheet defining color, background-color for the given sources

    Parameters
    ----------
    fname :
        Where to save the stylesheet
    source_colors :
        Colors defining the styles. Default: DEFAULT_SOURCE_COLORS.
    """
    if source_colors is None:
        source_colors = DEFAULT_SOURCE_COLORS

    rule_string = '.source-{src} {{\n    background-color: {src_bg};\n    ' \
                  'color: {src_txt};\n}}\n\n'

    stylesheet_str = ''
    for _, info in source_colors:
        text_color = info['color']
        for source_name, bg_color in info['sources'].items():
            stylesheet_str += rule_string.format(src=source_name,
                                                 src_bg=bg_color,
                                                 src_txt=text_color)

    with open(fname, 'w') as fh:
        fh.write(stylesheet_str)


class HtmlAssembler(object):
    """Generates an HTML-formatted report from INDRA Statements.

    The HTML report format includes statements formatted in English
    (by the EnglishAssembler), text and metadata for the Evidence
    object associated with each Statement, and a Javascript-based curation
    interface linked to the INDRA database (access permitting). The interface
    allows for curation of statements at the evidence level by letting the
    user specify type of error and (optionally) provide a short description of
    of the error.

    Parameters
    ----------
    statements : Optional[list[indra.statements.Statement]]
        A list of INDRA Statements to be added to the assembler. Statements
        can also be added using the add_statements method after the assembler
        has been instantiated.
    summary_metadata : Optional[dict]
        Dictionary of statement corpus metadata such as that provided by the
        INDRA REST API. Default is None. Each value should be a concise
        summary of O(1), not of order the length of the list, such as the
        evidence totals. The keys should be informative human-readable strings.
        This information is displayed as a tooltip when hovering over the
        page title.
    ev_counts : Optional[dict]
        A dictionary of the total evidence available for each
        statement indexed by hash. If not provided, the statements that are
        passed to the constructor are used to determine these, with whatever
        evidences these statements carry.
    beliefs : Optional[dict]
        A dictionary of the belief of each statement indexed by hash. If not
        provided, the beliefs of the statements passed to the constructor are
        used.
    source_counts : Optional[dict]
        A dictionary of the itemized evidence counts, by source, available for
        each statement, indexed by hash. If not provided, the statements
        that are passed to the constructor are used to determine these, with
        whatever evidences these statements carry.
    title : str
        The title to be printed at the top of the page.
    db_rest_url : Optional[str]
        The URL to a DB REST API to use for links out to further evidence.
        If given, this URL will be prepended to links that load additional
        evidence for a given Statement. One way to obtain this value is from
        the configuration entry indra.config.get_config('INDRA_DB_REST_URL').
        If None, the URLs are constructed as relative links.
        Default: None
    sort_by : str or function or None
        If str, it indicates which parameter to sort by, such as 'belief' or
        'ev_count', or 'ag_count'. Those are the default options because they
        can be derived from a list of statements, however if you give a custom
        list of stats with the `custom_stats` argument, you may use any of the
        parameters used to build it. The default, 'default', is mostly a sort
        by ev_count but also favors statements with fewer agents.

        Alternatively, you may give a function that takes a dict as its single
        argument, a dictionary of metrics. The contents of this dictionary
        always include "belief", "ev_count", and "ag_count". If source_counts
        are given, each source will also be available as an entry (e.g. "reach"
        and "sparser"). As with string values, you may also add your own custom
        stats using the `custom_stats` argument.

        The value may also be None, in which case the sort function will return
        the same value for all elements, and thus the original order of elements
        will be preserved. This could have strange effects when statements are
        grouped (i.e. when `grouping_level` is not 'statement'); such
        functionality is untested.
    custom_stats : Optional[list]
        A list of StmtStat objects containing custom statement statistics to be
        used in sorting of statements and statement groups.
    custom_sources : SourceInfo
        Use this if the sources in the statements are from sources other than
        the default ones present in indra/resources/source_info.json
        The structure of the input must conform to:

        .. code-block:: json

          {

            "source_key": {
                "name": "Source Name",
                "link": "<url>",
                "type": "reader|database",
                "domain": "<domain>",
                "default_style": {
                    "color": "<text color>",
                    "background-color": "<badge color>"
                }
            },
            ...
          }

        Where <text color> and <badge color> must be color names or color
        codes allowed in an html document per the CSS3 specification:
        https://www.w3.org/TR/css-color-3/#svg-color

    Attributes
    ----------
    statements : list[indra.statements.Statement]
        A list of INDRA Statements to assemble.
    model : str
        The HTML report formatted as a single string.
    metadata : dict
        Dictionary of statement list metadata such as that provided by the
        INDRA REST API.
    ev_counts : dict
        A dictionary of the total evidence available for each
        statement indexed by hash.
    beliefs : dict
        A dictionary of the belief score of each statement, indexed by hash.
    db_rest_url : str
        The URL to a DB REST API.
    """

    def __init__(self, statements=None, summary_metadata=None,
                 ev_counts=None, beliefs=None, source_counts=None,
                 curation_dict=None, title='INDRA Results', db_rest_url=None,
                 sort_by='default', custom_stats=None,
                 custom_sources: Optional[SourceInfo] = None):
        if custom_sources is not None:
            custom_source_list = list(custom_sources)
        else:
            custom_source_list = None
        self.custom_sources = custom_sources
        self.title = title
        self.statements = [] if statements is None else statements
        self.metadata = {} if summary_metadata is None \
            else summary_metadata
        self.ev_counts = get_available_ev_counts(self.statements) \
            if ev_counts is None else standardize_counts(ev_counts)
        self.beliefs = get_available_beliefs(self.statements) \
            if not beliefs else standardize_counts(beliefs)
        self.source_counts = get_available_source_counts(self.statements,
                                                         custom_source_list) \
            if source_counts is None \
            else complete_source_counts(standardize_counts(source_counts))
        self.available_sources = available_sources_stmts(self.statements,
                                                         custom_source_list) if \
            source_counts is None else available_sources_src_counts(
                source_counts, custom_source_list)
        self.sort_by = sort_by
        self.curation_dict = {} if curation_dict is None else curation_dict
        self.db_rest_url = db_rest_url
        self.model = None
        self.custom_stats = [] if custom_stats is None else custom_stats
        self.source_colors: Optional[SourceColors] = \
            _source_info_to_source_colors(custom_sources)

    def add_statements(self, statements):
        """Add a list of Statements to the assembler.

        Parameters
        ----------
        statements : list[indra.statements.Statement]
            A list of INDRA Statements to be added to the assembler.
        """
        self.statements += statements

    def make_json_model(self, grouping_level='agent-pair', no_redundancy=False,
                        **kwargs):
        """Return the JSON used to create the HTML display.

        Parameters
        ----------
        grouping_level : Optional[str]
            Statements can be grouped at three levels, 'statement' (ungrouped),
            'relation' (grouped by agents and type), and 'agent-pair' (grouped
            by ordered pairs of agents). Default: 'agent-pair'.
        no_redundancy : Optional[bool]
            If True, any group of statements that was already presented under
            a previous heading will be skipped. This is typically the case
            for complexes where different permutations of complex members
            are presented. By setting this argument to True, these can be
            eliminated. Default: False

        Returns
        -------
        json : dict
            A complexly structured JSON dict containing grouped statements and
            various metadata.
        """
        # Check args
        if grouping_level not in ('agent-pair', 'relation', 'statement'):
            raise ValueError("grouping_level must be one of 'agent-pair',"
                             "'relation', or 'statement'.")
        # Get an iterator over the statements, carefully grouped.
        normal_stats = make_standard_stats(ev_counts=self.ev_counts,
                                           beliefs=self.beliefs,
                                           source_counts=self.source_counts)
        stats = normal_stats + self.custom_stats
        stmt_rows = group_and_sort_statements(self.statements,
                                              custom_stats=stats,
                                              sort_by=self.sort_by,
                                              grouping_level=grouping_level)

        # Set up some data structures to gather results.
        agents = {}
        source_count_keys = set() if not self.source_counts \
            else {k for k in next(iter(self.source_counts.values())).keys()}

        # Loop through the sorted and grouped statements.
        all_hashes = set()

        # Used by the handle_* functions below to distinguish between cases
        # with source counts and without
        def _get_src_counts(metrics):
            if self.source_counts:
                src_counts = {k: metrics[k] for k in source_count_keys}
            else:
                src_counts = None
            return src_counts

        # AGENT PAIR LEVEL
        def handle_ag_pairs(rows):
            ret = OrderedDict()
            prev_hashes = set()
            all_level_hashes = set()
            for _, key, contents, metrics in rows:
                src_counts = _get_src_counts(metrics)
                # Create the agent key.
                if len(key) > 1 and isinstance(key[1], tuple):
                    agp_names = [key[0]] + [*key[1]] + [*key[2]]
                else:
                    agp_names = key[:]

                # Make string key
                agp_key_str = '-'.join([str(name) for name in agp_names])
                agp_agents = {name: Agent(name) for name in agp_names
                              if name is not None}
                agents[agp_key_str] = agp_agents

                # Determine if we are including this row or not.
                relations, stmt_hashes = \
                    handle_relations(contents, agent_key=agp_key_str,
                                     agp_agents=agp_agents)
                if stmt_hashes <= prev_hashes or not relations:
                    continue
                prev_hashes = stmt_hashes

                # Update the top level grouping.
                ret[agp_key_str] = {'html_key': str(uuid.uuid4()),
                                    'source_counts': src_counts,
                                    'stmts_formatted': relations,
                                    'names': agp_names,
                                    'label': None}
            return ret, all_level_hashes

        # RELATION LEVEL
        def handle_relations(rows, agent_key=None, agp_agents=None):
            ret = []
            all_level_hashes = set()
            for _, key, contents, metrics in rows:
                src_counts = _get_src_counts(metrics)
                # We will keep track of the meta data for this stmt group.
                # NOTE: The code relies on the fact that the Agent objects
                # in `meta_agents` are references to the Agents in the
                # Statement object `meta_stmts`.
                meta_agents = []
                meta_stmt = make_stmt_from_relation_key(key, meta_agents)
                meta_ag_dict = {ag.name: ag for ag in meta_agents
                                if ag is not None}

                # Generate the statement data.
                stmt_list, stmt_hashes = \
                    handle_statements(contents, meta_ag_dict=meta_ag_dict)
                all_level_hashes |= stmt_hashes
                if not stmt_list:
                    continue

                # Clean out invalid fields from the meta agents.
                for ag in meta_agents:
                    if ag is None:
                        continue
                    for dbn, dbid in list(ag.db_refs.items()):
                        if isinstance(dbid, set):
                            logger.info(
                                "Removing %s from refs due to too many "
                                "matches: %s" % (dbn, dbid))
                            del ag.db_refs[dbn]

                # Merge agent refs.
                if agent_key is not None:
                    assert agp_agents is not None, \
                        "agp_agents must be included along with agent_key."

                    for ag in agp_agents.values():
                        meta_ag = meta_ag_dict.get(ag.name)
                        if meta_ag is None:
                            continue
                        ag.db_refs.update(meta_ag.db_refs)

                    for name, ag in agents[agent_key].items():
                        new_ag = agp_agents.get(name)
                        if new_ag is None:
                            continue
                        _cautiously_merge_refs(new_ag, ag)

                # See note above: this is where the work on meta_agents is
                # applied because the agents are references.
                short_name = _format_stmt_text(meta_stmt)
                short_name_key = str(uuid.uuid4())

                ret.append({'short_name': short_name,
                            'short_name_key': short_name_key,
                            'stmt_info_list': stmt_list,
                            'src_counts': src_counts})
            return ret, all_level_hashes

        # STATEMENT LEVEL
        def handle_statements(rows, meta_ag_dict=None):
            ret = []
            all_level_hashes = set()
            for _, key, contents, metrics in rows:
                src_counts = _get_src_counts(metrics)
                stmt = contents
                # Check to see if we are doing this statement or not.
                if no_redundancy and key in all_hashes:
                    continue
                all_hashes.add(key)
                all_level_hashes.add(key)

                # Try to accumulate db refs in the meta agents.
                if meta_ag_dict is not None:
                    for ag in stmt.agent_list():
                        if ag is None:
                            continue
                        # Get the corresponding meta-agent
                        meta_ag = meta_ag_dict.get(ag.name)
                        if not meta_ag:
                            continue
                        _cautiously_merge_refs(ag, meta_ag)

                # Format some strings nicely.
                ev_list = _format_evidence_text(stmt, self.curation_dict)
                english = _format_stmt_text(stmt)
                if self.ev_counts:
                    tot_ev = self.ev_counts.get(int(key), '?')
                    if tot_ev == '?':
                        logger.warning(f'The hash {key} was not found in '
                                       f'the evidence totals dict.')
                    evidence_count_str = f'{len(ev_list)} / {tot_ev}'
                else:
                    evidence_count_str = str(len(ev_list))

                ret.append({'hash': str(key), 'english': english,
                            'evidence': ev_list,
                            'belief': float('%.4f' % stmt.belief),  # => 0.1234
                            'evidence_count': evidence_count_str,
                            'source_count': src_counts})
            return ret, all_level_hashes

        # Call the appropriate method depending on our top grouping level.
        if grouping_level == 'agent-pair':
            output, _ = handle_ag_pairs(stmt_rows)
        elif grouping_level == 'relation':
            output, _ = handle_relations(stmt_rows)
        elif grouping_level == 'statement':
            output, _ = handle_statements(stmt_rows)
        else:
            assert False, f"Grouping level enforcement failed: {grouping_level}"

        # Massage the output into the expected format.
        stmts = {}
        if grouping_level == 'statement':
            summed_sources = defaultdict(lambda: 0)
            for stmt_info in output:
                for k, v in stmt_info['source_count'].items():
                    summed_sources[k] += v
                summed_sources = dict(summed_sources)
            stmts['all-statements'] = {
                'html_key': str(uuid.uuid4()),
                'source_counts': summed_sources,
                'stmts_formatted': [
                    {'short_name': 'All Statements Sub Group',
                     'short_name_key': 'all-statements-sub-group',
                     'stmt_info_list': output,
                     'src_counts': summed_sources}
                ],
                'names': 'All Statements',
                'label': 'All Statements'
            }
        elif grouping_level == 'relation':
            summed_sources = defaultdict(lambda: 0)
            for rel in output:
                for k, v in rel['src_counts'].items():
                    summed_sources[k] += v
                summed_sources = dict(summed_sources)
            stmts['all-relations'] = {
                'html_key': str(uuid.uuid4()),
                'source_counts': summed_sources,
                'stmts_formatted': output,
                'names': 'All Relations',
                'label': 'All Relations'
            }
        else:
            stmts = output

        # Add labels for each top level group (tlg).
        if grouping_level == 'agent-pair':
            for agp_key, tlg in stmts.items():
                agent_pair_agents = list(agents[agp_key].values())
                for ag in agent_pair_agents:
                    for dbn, dbid in list(ag.db_refs.items()):
                        if isinstance(dbid, set):
                            logger.info("Removing %s from top level refs "
                                        "due to multiple matches: %s"
                                        % (dbn, dbid))
                            del ag.db_refs[dbn]
                agp_label = make_top_level_label_from_names_key(tlg['names'])
                agp_label = re.sub("<b>(.*?)</b>", r"\1", agp_label)
                agp_label = tag_agents(agp_label, agent_pair_agents)
                tlg['label'] = agp_label

        return stmts

    def make_model(self, template=None, grouping_level='agent-pair',
                   add_full_text_search_link=False, no_redundancy=False,
                   **template_kwargs):
        """Return the assembled HTML content as a string.

        Parameters
        ----------
        template : a Template object
            Manually pass a Jinja template to be used in generating the HTML.
            The template is responsible for rendering essentially the output of
            `make_json_model`.
        grouping_level : Optional[str]
            Statements can be grouped under sub-headings at three levels,
            'statement' (ungrouped), 'relation' (grouped by agents and type),
            and 'agent-pair' (grouped by ordered pairs of agents).
            Default: 'agent-pair'.
        add_full_text_search_link : bool
            If True, link with Text fragment search in PMC journal will be
            added for the statements.  
        no_redundancy : Optional[bool]
            If True, any group of statements that was already presented under
            a previous heading will be skipped. This is typically the case
            for complexes where different permutations of complex members
            are presented. By setting this argument to True, these can be
            eliminated. Default: False

            All other keyword arguments are passed along to the template. If you
            are using a custom template with args that are not passed below, this
            is how you pass them.

        Returns
        -------
        str
            The assembled HTML as a string.
        """
        # Make the JSON model.
        tl_stmts = self.make_json_model(grouping_level=grouping_level,
                                        no_redundancy=no_redundancy)

        if add_full_text_search_link:
            for statement in tl_stmts:
                statement = tl_stmts[statement]
                for stmt_formatted in statement["stmts_formatted"]:
                    for stmt_info in stmt_formatted["stmt_info_list"]:
                        for evidence in stmt_info["evidence"]:
                            if 'PMCID' not in evidence.get('text_refs', {}):
                                if evidence.get('pmid'):
                                    ev_pmcid = id_lookup(
                                        evidence['pmid'], 'pmid') \
                                        .get('pmcid', None)
                                    if ev_pmcid:
                                        evidence['pmcid'] = ev_pmcid
                            else:
                                evidence['pmcid'] = \
                                    evidence['text_refs']['PMCID']

        metadata = {k.replace('_', ' ').title(): v
                    for k, v in self.metadata.items()
                    if not isinstance(v, list) and not isinstance(v, dict)}
        if self.db_rest_url and not self.db_rest_url.endswith('statements'):
            db_rest_url = self.db_rest_url + '/statements'
        else:
            db_rest_url = None

        # Fill the template.
        if template is None:
            template = default_template
        if self.source_counts and 'source_key_dict' not in template_kwargs:
            if self.custom_sources is not None:
                sources = list(self.custom_sources)
            else:
                sources = all_sources
            template_kwargs['source_key_dict'] = {src: src for src in sources}
        if 'source_colors' not in template_kwargs:
            if self.source_colors is not None:
                template_kwargs['source_colors'] = self.source_colors
            else:
                template_kwargs['source_colors'] = DEFAULT_SOURCE_COLORS
        if 'source_info' not in template_kwargs:
            if self.custom_sources:
                template_kwargs['source_info'] = self.custom_sources
            else:
                template_kwargs['source_info'] = SOURCE_INFO.copy()
        if 'simple' not in template_kwargs:
            template_kwargs['simple'] = True
        if 'available_sources' not in template_kwargs:
            template_kwargs['available_sources'] = list(self.available_sources)
        if 'show_only_available' not in template_kwargs:
            template_kwargs['show_only_available'] = False
        template_kwargs['reverse_source_mapping'] = \
            {v: k for k, v in internal_source_mappings.items()}

        self.model = template.render(stmt_data=tl_stmts,
                  metadata=metadata, title=self.title,
                  db_rest_url=db_rest_url,
                  add_full_text_search_link=add_full_text_search_link,  # noqa
                  **template_kwargs)
        return self.model

    def append_warning(self, msg):
        """Append a warning message to the model to expose issues."""
        assert self.model is not None, "You must already have run make_model!"
        addendum = ('\t<span style="color:red;">(CAUTION: %s occurred when '
                    'creating this page.)</span>' % msg)
        self.model = self.model.replace(self.title, self.title + addendum)
        return self.model

    def save_model(self, fname, **kwargs):
        """Save the assembled HTML into a file.

        Other kwargs are passed directly to `make_model`.

        Parameters
        ----------
        fname : str | Path
            The path to the file to save the HTML into.
        """
        if self.model is None:
            self.make_model(**kwargs)

        with open(fname, 'wb') as fh:
            fh.write(self.model.encode('utf-8'))


def _format_evidence_text(stmt, curation_dict=None, correct_tags=None):
    """Returns evidence metadata with highlighted evidence text.

    Parameters
    ----------
    stmt : indra.Statement
        The Statement with Evidence to be formatted.

    Returns
    -------
    list of dicts
        List of dictionaries corresponding to each Evidence object in the
        Statement's evidence list. Each dictionary has keys 'source_api',
        'pmid' and 'text', drawn from the corresponding fields in the
        Evidence objects. The text entry of the dict includes
        `<span>` tags identifying the agents referenced by the Statement.
    """
    if curation_dict is None:
        curation_dict = {}
    if correct_tags is None:
        correct_tags = ['correct']

    def get_role(ag_ix):
        if isinstance(stmt, Complex) or \
           isinstance(stmt, SelfModification) or \
           isinstance(stmt, ActiveForm) or isinstance(stmt, Conversion) or\
           isinstance(stmt, Translocation):
            return 'other'
        else:
            assert len(stmt.agent_list()) == 2, (len(stmt.agent_list()),
                                                 type(stmt))
            return 'subject' if ag_ix == 0 else 'object'

    ev_list = []
    for ix, ev in enumerate(stmt.evidence):
        # Expand the source api to include the sub-database
        if ev.source_api == 'biopax' and \
                'source_sub_id' in ev.annotations and \
                ev.annotations['source_sub_id']:
            source_api = '%s:%s' % (ev.source_api,
                                    ev.annotations['source_sub_id'])
        else:
            source_api = ev.source_api
        # Prepare the evidence text
        if ev.text is None:
            format_text = None
        else:
            ev_text = escape(ev.text)
            indices = []
            for ix, ag in enumerate(stmt.agent_list()):
                if ag is None:
                    continue
                # If the statement has been preassembled, it will have
                # this entry in annotations
                try:
                    ag_text = ev.annotations['agents']['raw_text'][ix]
                    if ag_text is None:
                        raise KeyError
                # Otherwise we try to get the agent text from db_refs
                except KeyError:
                    ag_text = ag.db_refs.get('TEXT')
                if ag_text is None:
                    continue
                ag_text = escape(ag_text)
                role = get_role(ix)
                # Get the tag with the correct badge
                tag_start = '<span class="badge badge-%s">' % role
                tag_close = '</span>'
                # Build up a set of indices
                indices += [(m.start(), m.start() + len(ag_text),
                             ag_text, tag_start, tag_close)
                            for m in re.finditer(re.escape(ag_text), ev_text)]
            format_text = tag_text(ev_text, indices)

        curation_key = (stmt.get_hash(), ev.source_hash)
        curations = curation_dict.get(curation_key, [])
        num_curations = len(curations)
        num_correct = len(
            [cur for cur in curations if cur['error_type'] in correct_tags])
        num_incorrect = num_curations - num_correct
        text_refs = {k.upper(): v for k, v in ev.text_refs.items()}
        source_url = src_url(ev)
        ev_list.append({'source_api': source_api,
                        'pmid': ev.pmid,
                        'text_refs': text_refs,
                        'text': format_text,
                        'source_hash': str(ev.source_hash),
                        'original_json': ev.to_json(),
                        'num_curations': num_curations,
                        'num_correct': num_correct,
                        'num_incorrect': num_incorrect,
                        'source_url': source_url
                        })

    return ev_list


def _format_stmt_text(stmt):
    # Get the English assembled statement
    ea = EnglishAssembler([stmt])
    english = ea.make_model()
    if not english:
        english = str(stmt)
        return tag_agents(english, stmt.agent_list())
    return tag_agents(english, ea.stmt_agents[0])


def _cautiously_merge_refs(from_ag, to_ag):
    # Check the db refs for this agent against the meta agent
    for dbn, dbid in from_ag.db_refs.items():
        if dbn == 'TEXT':
            continue
        meta_dbid = to_ag.db_refs.get(dbn)
        if isinstance(meta_dbid, set):
            # If we've already marked this one add to the set.
            to_ag.db_refs[dbn].add(dbid)
        elif meta_dbid is not None and meta_dbid != dbid:
            # If we've seen it before and don't agree, mark it.
            to_ag.db_refs[dbn] = {to_ag.db_refs[dbn], dbid}
        elif meta_dbid is None:
            # Otherwise, add it.
            to_ag.db_refs[dbn] = dbid


def tag_agents(english, agents):
    # Agents can be AgentWithCoordinates (preferred) or regular Agent objects
    indices = []
    for ag in agents:
        if ag is None or not ag.name:
            continue
        url = id_url(ag)
        if url is None:
            tag_start = '<b>'
            tag_close = '</b>'
        else:
            tag_start = "<a href='%s' target='_blank'>" % url
            tag_close = "</a>"
        # If coordinates are passed, use them. Otherwise, try to find agent
        # names in english text
        if isinstance(ag, AgentWithCoordinates):
            index = (ag.coords[0], ag.coords[1], ag.name, tag_start, tag_close)
            indices.append(index)
        elif isinstance(ag, Agent):
            found = False
            for m in re.finditer(re.escape(ag.name), english):
                index = (m.start(), m.start() + len(ag.name), ag.name,
                         tag_start, tag_close)
                indices.append(index)
                found = True
            if not found and \
                    english.startswith(re.escape(ag.name).capitalize()):
                index = (0, len(ag.name), ag.name, tag_start, tag_close)
                indices.append(index)
    return tag_text(english, indices)


link_namespace_order = default_ns_order + \
    ['CHEMBL', 'DRUGBANK', 'PUBCHEM', 'HMDB', 'HMS-LINCS', 'CAS',
     'IP', 'PF', 'NXPFA', 'MIRBASEM', 'NCIT', 'WM']


def id_url(ag):
    # Return identifier URLs in a prioritized order
    # TODO: we should add handling for UPPRO here, however, that would require
    # access to UniProt client resources in the context of the DB REST API
    # which could be problematic
    for db_name in link_namespace_order:
        if db_name in ag.db_refs:
            # Handle a special case where a list of IDs is given
            if isinstance(ag.db_refs[db_name], list):
                db_id = ag.db_refs[db_name][0]
                if db_name == 'WM':
                    db_id = db_id[0]
            else:
                db_id = ag.db_refs[db_name]
            # We can add more name spaces here if there are issues
            if db_name in {'CHEBI'}:
                db_id = ensure_prefix('CHEBI', db_id)
            # Here we validate IDs to make sure we don't surface invalid
            # links.
            if not validate_id(db_name, db_id):
                logger.debug('Invalid grounding encountered: %s:%s' %
                             (db_name, db_id))
                continue
            # Finally, we return a valid identifiers.org URL
            return get_identifiers_url(db_name, db_id)


def src_url(ev: Evidence) -> str:
    """Given an Evidence object, provide the URL for the source"""
    # Get source url from evidence or from SOURCE_INFO as backup if source
    # is a database.
    # SOURCE_INFO contains the names as they are in INDRA,
    # while source_api is as the source name appear in the database

    url = ev.annotations.get('source_url')
    if not url:
        rev_src = reverse_source_mappings.get(ev.source_api, ev.source_api)
        if SOURCE_INFO.get(rev_src, {}).get('type', '') == 'database':
            url = SOURCE_INFO[rev_src]['link']
        else:
            url = ''
    return url


def tag_text(text, tag_info_list):
    """Apply start/end tags to spans of the given text.


    Parameters
    ----------
    text : str
        Text to be tagged
    tag_info_list : list of tuples
        Each tuple refers to a span of the given text. Fields are `(start_ix,
        end_ix, substring, start_tag, close_tag)`, where substring, start_tag,
        and close_tag are strings. If any of the given spans of text overlap,
        the longest span is used.

    Returns
    -------
    str
        String where the specified substrings have been surrounded by the
        given start and close tags.
    """
    # Check to tags for overlap and if there is any, return the subsumed
    # range. Return None if no overlap.
    def overlap(t1, t2):
        if range(max(t1[0], t2[0]), min(t1[1]-1, t2[1]-1)+1):
            if t1[1] - t1[0] >= t2[1] - t2[0]:
                return t2
            else:
                return t1
        else:
            return None

    # Remove subsumed tags
    for t1, t2 in list(itertools.combinations(tag_info_list, 2)):
        subsumed_tag = overlap(t1, t2)
        if subsumed_tag is not None:
            # Delete the subsumed tag from the list
            try:
                tag_ix = tag_info_list.index(subsumed_tag)
                del tag_info_list[tag_ix]
            # Ignore case where tag has already been deleted
            except ValueError:
                pass
    # Sort the indices by their start position
    tag_info_list.sort(key=lambda x: x[0])
    # Now, add the marker text for each occurrence of the strings
    format_text = ''
    start_pos = 0
    for i, j, ag_text, tag_start, tag_close in tag_info_list:
        # Capitalize if it's the beginning of a sentence
        if i == 0:
            ag_text = ag_text[0].upper() + ag_text[1:]
        # Add the text before this agent, if any
        format_text += text[start_pos:i]
        # Add wrapper for this entity
        format_text += tag_start + ag_text + tag_close
        # Now set the next start position
        start_pos = j
    # Add the last section of text
    format_text += text[start_pos:]
    return format_text


def complete_source_counts(source_counts):
    """Return source counts that are complete with respect to all sources.

    This is necessary because the statement presentation module expects
    that all sources that appear in any statement source count appear
    in all statement source counts (even if the count is 0).
    """
    all_sources = set()
    for stmt_source_counts in source_counts.values():
        all_sources |= set(stmt_source_counts)
    for stmt_source_counts in source_counts.values():
        missing_sources = all_sources - set(stmt_source_counts)
        for source in missing_sources:
            stmt_source_counts[source] = 0
    return source_counts
