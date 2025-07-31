from __future__ import absolute_import, print_function, unicode_literals
from builtins import dict, str
import sys
import logging
import requests
from io import StringIO, BytesIO
from collections import namedtuple
from .processor import SignorProcessor
from indra.util import read_unicode_csv, read_unicode_csv_fileobj

logger = logging.getLogger(__name__)

_signor_fields = [
    'ENTITYA',
    'TYPEA',
    'IDA',
    'DATABASEA',
    'ENTITYB',
    'TYPEB',
    'IDB',
    'DATABASEB',
    'EFFECT',
    'MECHANISM',
    'RESIDUE',
    'SEQUENCE',
    'TAX_ID',
    'CELL_DATA',
    'TISSUE_DATA',
    'MODULATOR_COMPLEX',
    'TARGET_COMPLEX',
    'MODIFICATIONA',
    'MODASEQ',
    'MODIFICATIONB',
    'MODBSEQ',
    'PMID',
    'DIRECT',
    'NOTES',
    'ANNOTATOR',
    'SENTENCE',
    'SCORE',
    'SIGNOR_ID',
]


_SignorRow_ = namedtuple('SignorRow', _signor_fields)


def process_from_file(signor_data_file, signor_complexes_file=None,
                      delimiter='\t'):
    """Process Signor interaction data from CSV files.

    Parameters
    ----------
    signor_data_file : str
        Path to the Signor interaction data file in CSV format.
    signor_complexes_file : Optional[str]
        Path to the Signor complexes data in CSV format. If specified,
        Signor complexes will not be expanded to their constitutents.
    delimiter : Optional[str]
        The delimiter used in the data file. Older data files use ;
        as a delimiter whereas more recent ones use tabs.

    Returns
    -------
    indra.sources.signor.SignorProcessor
        SignorProcessor containing Statements extracted from the Signor data.
    """
    # Get generator over the CSV file
    data_iter = read_unicode_csv(signor_data_file, delimiter=delimiter,
                                 skiprows=1)
    complexes_iter = None
    if signor_complexes_file:
        complexes_iter = read_unicode_csv(signor_complexes_file, delimiter=';',
                                          skiprows=1)
    else:
        logger.warning('Signor complex mapping file not provided, Statements '
                       'involving complexes will not be expanded to members.')
    return _processor_from_data(data_iter, complexes_iter)


def process_from_web(signor_data_file=None, signor_complexes_file=None):
    """Process Signor interaction data from the web.

    This downloads the latest interaction data directly from the Signor
    website without an intermediate local file.

    Parameters
    ----------
    signor_data_file : Optional[str]
        If specified, the interaction data will be written to this file.
    signor_complexes_file : Optional[str]
        If specified, the complex data will be written to this file.

    Returns
    -------
    indra.sources.signor.SignorProcessor
        SignorProcessor containing Statements extracted from the Signor data.
    """
    # Get interaction data
    data_url = 'https://signor.uniroma2.it/download_entity.php'
    res = requests.post(data_url, data={'organism': 'human', 'format': 'csv',
                                        'submit': 'Download'})
    data_iter = _handle_response(res, '\t', fname=signor_data_file)
    # Get complexes
    complexes_url = 'https://signor.uniroma2.it/download_complexes.php'
    res = requests.post(complexes_url,
                        data={'submit': 'Download complex data'})
    complexes_iter = _handle_response(res, ';', fname=signor_complexes_file)
    return _processor_from_data(data_iter, complexes_iter)


def _handle_response(res, delimiter, fname=None):
    """Get an iterator over the CSV data from the response."""
    if res.status_code == 200:
        # Python 2 -- csv.reader will need bytes
        if sys.version_info[0] < 3:
            csv_io = BytesIO(res.content)
            # Optionally write to file
            if fname:
                with open(fname, 'wb') as fh:
                    fh.write(res.content)
        # Python 3 -- csv.reader needs str
        else:
            csv_io = StringIO(res.text)
            # Optionally write to file
            if fname:
                with open(fname, 'wt') as fh:
                    fh.write(res.text)
        data_iter = read_unicode_csv_fileobj(csv_io, delimiter=delimiter,
                                             skiprows=1)
    else:
        raise Exception('Could not download Signor data.')
    return data_iter


def _processor_from_data(data_iter, complexes_iter):
    # Process into a list of SignorRow namedtuples
    # Strip off any funky \xa0 whitespace characters
    data = [_SignorRow_(*[f.strip() for f in r]) for r in data_iter]
    complex_map = {}
    if complexes_iter:
        for crow in complexes_iter:
            complex_map[crow[0]] = [c for c in crow[2].split(',  ') if c]
    return SignorProcessor(data, complex_map)
