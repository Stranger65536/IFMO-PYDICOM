# coding=utf-8
from csv import reader
from os.path import isfile
from os.path import join

from LoggerUtils import LoggerUtils
from Utils import create_cache
from Utils import list_files
from Utils import load_cache

csv_ext = '.csv'
log = LoggerUtils.get_logger('PatientDiagnosisLoader')
cache_file_name = 'diagnosis.cache'


def parse_file(csvfile, diagnosis):
    csvreader = reader(csvfile,
                       delimiter=',',
                       quotechar='"')
    for row in csvreader:
        if len(row) is not 2:
            raise ValueError(
                'Expected csv with structure '
                '["PatientID (LIDC-IDRI-####)", '
                '"Diagnose (0-3)" ], row {}'.format(row))
        if row[0] in diagnosis:
            log.warn('Duplicate diagnose found '
                     'for patient {}'.format(row[0]))
        diagnosis[row[0]] = row[1]


class PatientDiagnosisLoader(object):
    def __init__(self, diagnosis_path):
        log.info('Patient diagnosis directory: {}'
                 .format(diagnosis_path))
        self._diagnosis_path = diagnosis_path

    def load_dicoms_metadata(self):
        cache_file = join(self._diagnosis_path, cache_file_name)

        if isfile(cache_file):
            log.info('Found cache file with diagnosis, '
                     'delete it to reload: {}. Loading...'
                     .format(cache_file))
            return load_cache(cache_file)

        diagnosis = {}
        files = list_files(self._diagnosis_path, csv_ext)
        error_files = []
        file_counter = 1

        for file in files:
            try:
                log.info('Parsing diagnosis file {} of {}: {}'
                         .format(file_counter, len(files), file))
                with open(file, newline='') as csvfile:
                    parse_file(csvfile, diagnosis)
            except ValueError:
                error_files.append(file)
                log.error('Can\'t load diagnosis file {}'
                          .format(file), exc_info=True)
            finally:
                file_counter += 1

        log.info('Creating diagnosis cache: {}'
                 .format(cache_file))
        create_cache(cache_file, diagnosis, log)

        return diagnosis
