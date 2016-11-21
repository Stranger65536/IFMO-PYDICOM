import csv
import logging
import os
from logging.handlers import RotatingFileHandler


class PatientDiagnosisLoader:
    _DiagnosisExtension = '.csv'

    @staticmethod
    def _configure_logger():
        logger = logging.getLogger('PatientDiagnosisLoader')
        logger.setLevel(logging.DEBUG)
        fh = RotatingFileHandler('PatientDiagnosisLoader.log', mode='a', maxBytes=50 * 1024 * 1024,
                                 backupCount=2, encoding=None, delay=0)
        fh.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger

    # noinspection PyUnresolvedReferences
    _log = _configure_logger.__func__()

    def __init__(self, diagnosis_path):
        self._log.info('Patient diagnosis directory: {}'.format(diagnosis_path))
        self._diagnosis_path = diagnosis_path

    def load_dicoms_metadata(self):
        file_counter = 1
        diagnosis = {}
        for dir_name, sub_dirs, file_list in os.walk(self._diagnosis_path):
            for file in file_list:
                if self._DiagnosisExtension in file.lower():
                    file_path = os.path.join(dir_name, file)
                    try:
                        self._log.debug('Found diagnosis file #{} {}, loading'.format(file_counter, file_path))
                        file_counter += 1
                        with open(file_path, newline='') as csvfile:
                            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
                            for row in csvreader:
                                if len(row) is not 2:
                                    raise ValueError('Expected csv with structure ["PatientID" '
                                                     '(LIDC-IDRI-####), "Diagnose" (0-3)]')
                                if row[0] in diagnosis:
                                    self._log.warn('Duplicate diagnose found for patient {}'.format(row[0]))
                                diagnosis[row[0]] = row[1]
                    except Exception as e:
                        self._log.error('Can\'t load diagnosis file: {} due an error'.format(file_path), e,
                                        exc_info=True)
        return diagnosis
