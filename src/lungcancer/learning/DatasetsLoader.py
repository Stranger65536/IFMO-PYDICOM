import imghdr
import ntpath
import os
from enum import Enum

import numpy

from lungcancer.LoggerUtils import LoggerUtils


class ClassificationType(Enum):
    malignancy = {0: ['1'], 1: ['2', '3']}
    cancer_type = {0: ['2'], 1: ['3']}


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
        filtered_by_class = [DatasetsLoader._filter_by_name_suffix(class_values, image_files, class_name)
                             for (class_name, class_values) in self._classes.items()]
        self._filtered_data = {k: v for d in filtered_by_class for k, v in d.items()}

    @staticmethod
    def _filter_by_name_suffix(class_values, image_files, class_name):
        return {file: class_name for file in
                filter(lambda f: DatasetsLoader._get_file_suffix(f) in class_values, image_files)}

    @staticmethod
    def _get_file_suffix(file_name):
        return os.path.splitext(file_name)[0].split('_')[-1]

    # (X_train, y_train), (X_test, y_test)
    # y_test[0][0] - sample, result int32
    # X_test[0][0][0][0] - sample, channel, row, column uint8
    def perform_bootstrap(self, iterations):
        all_samples = list(self._filtered_data.items())
        all_samples_set = set(all_samples)
        train_samples = [set([all_samples[i] for i in sample])
                         for sample in numpy.random.choice(len(all_samples),
                                                           size=(iterations, len(all_samples)),
                                                           replace=True)]
        test_samples = [all_samples_set - train_sample for train_sample in train_samples]
        return train_samples, test_samples

    def convert_to_dataset(self, train_samples, test_samples, model):
        pass
