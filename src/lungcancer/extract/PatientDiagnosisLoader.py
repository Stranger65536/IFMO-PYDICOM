import csv
import os

from lungcancer.LoggerUtils import LoggerUtils


class PatientDiagnosisLoader:
    _DiagnosisExtension = '.csv'

    _log = LoggerUtils.get_logger('PatientDiagnosisLoader')

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
                        self._log.debug('Found diagnosis file #{} {}, loading'
                                        .format(file_counter, file_path))
                        file_counter += 1
                        with open(file_path, newline='') as csvfile:
                            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
                            for row in csvreader:
                                if len(row) is not 2:
                                    raise ValueError('Expected csv with structure ["PatientID" '
                                                     '(LIDC-IDRI-####), "Diagnose" (0-3)]')
                                if row[0] in diagnosis:
                                    self._log.warn('Duplicate diagnose found for patient {}'
                                                   .format(row[0]))
                                diagnosis[row[0]] = row[1]
                    except Exception as e:
                        self._log.error('Can\'t load diagnosis file: {} due an error'
                                        .format(file_path), e, exc_info=True)
        return diagnosis
