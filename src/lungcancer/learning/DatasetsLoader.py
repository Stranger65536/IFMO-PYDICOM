import imghdr
import ntpath
import os
from enum import Enum

from lungcancer.LoggerUtils import LoggerUtils


class ClassificationType(Enum):
    malignancy = (['1'], ['2', '3'])
    cancer_type = (['2'], ['3'])


class DatasetsLoader:
    _log = LoggerUtils.get_logger('DatasetsLoader')

    def __init__(self, working_dir, mode, models):
        self._working_dir = working_dir
        self._classes = mode.value
        self._filtered_data = None
        # noinspection PyUnusedLocal
        self._models = models
        self._log.info('Configured to work with classes: {} and models: {}'.format(self._classes, self._models))

    def filter_data(self):
        files = [os.path.join(self._working_dir, file) for file in os.listdir(self._working_dir)]
        image_files = [ntpath.basename(f) for f in list(filter(lambda f: os.path.isfile(f) and imghdr.what(f), files))]
        self._filtered_data = [list(filter(lambda f: self._get_file_suffix(f) in class_values, image_files))
                               for class_values in self._classes]

    @staticmethod
    def _get_file_suffix(file_name):
        return os.path.splitext(file_name)[0].split('_')[-1]


def perform_bootstrap(self):
    pass
