__all__ = ['process_annotations', 'get_annotations', 'upload_annotation',
           'upload_statement_annotation', 'statement_to_annotations']

import logging
import requests
from indra.config import get_config
from .processor import HypothesisProcessor
from .annotator import statement_to_annotations

logger = logging.getLogger(__name__)

base_url = 'https://api.hypothes.is/api/'
api_key = get_config('HYPOTHESIS_API_KEY')
headers = {'Authorization': 'Bearer %s' % api_key,
           'Accept': 'application/vnd.hypothesis.v1+json',
           'content-type': 'application/json'}
indra_group = get_config('HYPOTHESIS_GROUP')


def send_get_request(endpoint, **params):
    """Send a request to the hypothes.is web service and return JSON response.

    Note that it is assumed that `HYPOTHESIS_API_KEY` is set either as a
    configuration entry or as an environmental variable.

    Parameters
    ----------
    endpoint : str
        The endpoint to call, e.g., `search`.
    params : kwargs
        A set of keyword arguments that are passed to the `requests.get` call
        as `params`.
    """
    if api_key is None:
        return ValueError('No API key set in HYPOTHESIS_API_KEY')
    res = requests.get(base_url + endpoint, headers=headers,
                       params=params)
    res.raise_for_status()
    return res.json()


def send_post_request(endpoint, **params):
    """Send a post request to the hypothes.is web service and return JSON
    response.

    Note that it is assumed that `HYPOTHESIS_API_KEY` is set either as a
    configuration entry or as an environmental variable.

    Parameters
    ----------
    endpoint : str
        The endpoint to call, e.g., `search`.
    params : kwargs
        A set of keyword arguments that are passed to the `requests.post` call
        as `json`.
    """
    if api_key is None:
        return ValueError('No API key set in HYPOTHESIS_API_KEY')
    res = requests.post(base_url + endpoint, headers=headers,
                        json=params)
    res.raise_for_status()
    return res.json()


def upload_annotation(url, annotation, target_text=None, tags=None,
                      group=None):
    """Upload an annotation to hypothes.is.

    Parameters
    ----------
    url : str
        The URL of the resource being annotated.
    annotation : str
        The text content of the annotation itself.
    target_text : Optional[str]
        The specific span of text that the annotation applies to.
    tags : list[str]
        A list of tags to apply to the annotation.
    group : Optional[str]
        The hypothesi.is key of the group (not its name). If not given, the
        HYPOTHESIS_GROUP configuration in the config file or an environmental
        variable is used.

    Returns
    -------
    json
        The full response JSON from the web service.
    """
    if group is None:
        if indra_group:
            group = indra_group
        else:
            raise ValueError('No group provided and HYPOTHESIS_GROUP '
                             'is not set.')
    params = {
        'uri': url,
        'group': group,
        'text': annotation,
    }
    if target_text:
        params['target'] = [{
            'source': [url],
            'selector': [
                {'type': 'TextQuoteSelector',
                 'exact': target_text}
            ]
        }]
    if tags:
        params['tags'] = tags
    permissions = {'read': ['group:%s' % group]}
    params['permissions'] = permissions
    res = send_post_request('annotations', **params)
    return res


def upload_statement_annotation(stmt, annotate_agents=True):
    """Construct and upload all annotations for a given INDRA Statement.

    Parameters
    ----------
    stmt : indra.statements.Statement
        An INDRA Statement.
    annotate_agents : Optional[bool]
        If True, the agents in the annotation text are linked to outside
        databases based on their grounding. Default: True

    Returns
    -------
    list of dict
        A list of annotation structures that were uploaded to hypothes.is.
    """
    annotations = statement_to_annotations(stmt,
                                           annotate_agents=annotate_agents)
    for annotation in annotations:
        annotation['tags'].append('indra_upload')
        upload_annotation(**annotation)
    return annotations


def get_annotations(group=None):
    """Return annotations in hypothes.is in a given group.

    Parameters
    ----------
    group : Optional[str]
        The hypothesi.is key of the group (not its name). If not given, the
        HYPOTHESIS_GROUP configuration in the config file or an environmental
        variable is used.
    """
    if group is None:
        if indra_group:
            group = indra_group
        else:
            raise ValueError('No group provided and HYPOTHESIS_GROUP '
                             'is not set.')
    # Note that this batch size is the maximum that the API allows, therefore
    # it makes sense to run queries with this fixed limit.
    limit = 200
    offset = 0
    annotations = []
    while True:
        logger.info('Getting up to %d annotations from offset %d' %
                    (limit, offset))
        res = send_get_request('search', group=group, limit=limit, offset=offset)
        rows = res.get('rows', [])
        if not rows:
            break
        annotations += rows
        offset += len(rows)
    logger.info('Got a total of %d annotations' % len(annotations))
    return annotations


def process_annotations(group=None, reader=None, grounder=None):
    """Process annotations in hypothes.is in a given group.

    Parameters
    ----------
    group : Optional[str]
        The hypothesi.is key of the group (not its name). If not given, the
        HYPOTHESIS_GROUP configuration in the config file or an environmental
        variable is used.
    reader : Optional[None, str, Callable[[str], Processor]]
        A handle for a function which takes a single str argument
        (text to process) and returns a processor object with a statements
        attribute containing INDRA Statements. By default, the REACH reader's
        process_text function is used with default parameters. Note that
        if the function requires extra parameters other than the input text,
        functools.partial can be used to set those. Can be alternatively
        set to :func:`indra.sources.bel.process_text` by using the string
        "bel".
    grounder : Optional[function]
        A handle for a function which takes a positional str argument (entity
        text to ground) and an optional context key word argument and returns
        a list of objects matching the structure of gilda.grounder.ScoredMatch.
        By default, Gilda's ground function is used for grounding.

    Returns
    -------
    HypothesisProcessor
        A HypothesisProcessor object which contains a list of extracted
        INDRA Statements in its statements attribute, and a list of extracted
        grounding curations in its groundings attribute.

    Example
    -------
    Process all annotations that have been written in BEL with:

    .. code-block:: python

        from indra.sources import hypothesis
        processor = hypothesis.process_annotations(group='Z8RNqokY', reader='bel')
        processor.statements
        # returns: [Phosphorylation(AKT(), PCGF2(), T, 334)]

    If this example doesn't work, try joining the group with this link:
    https://hypothes.is/groups/Z8RNqokY/cthoyt-bel.
    """
    annotations = get_annotations(group=group)
    hp = HypothesisProcessor(annotations, reader=reader, grounder=grounder)
    hp.extract_statements()
    hp.extract_groundings()
    return hp
