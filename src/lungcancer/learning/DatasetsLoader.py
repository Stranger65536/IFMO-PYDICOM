import imghdr
import ntpath
import os
from enum import Enum
from functools import reduce

import numpy
from PIL import Image

from lungcancer.LoggerUtils import LoggerUtils


class ClassificationType(Enum):
    malignancy = {0: ['1'], 1: ['2', '3']}
    cancer_type = {0: ['2'], 1: ['3']}


class DatasetsLoader:
    _log = LoggerUtils.get_logger('DatasetsLoader')

    def __init__(self, working_dir, mode, models):
        self._working_dir = working_dir
        self._classes = mode.value
        self._model_images = None
        self._class_values = None
        # noinspection PyUnusedLocal
        self._models = models
        self._size = None
        self._log.info('Configured to work with classes: {} and models: {}'.format(self._classes, self._models))

    def load_data(self):
        files = [os.path.join(self._working_dir, file) for file in os.listdir(self._working_dir)]
        image_files = [ntpath.basename(f) for f in list(filter(lambda f: os.path.isfile(f) and imghdr.what(f), files))]
        filtered_by_class = [DatasetsLoader._filter_by_name_suffix(class_values, image_files, class_name)
                             for (class_name, class_values) in self._classes.items()]
        self._size = reduce(lambda x, y: len(x) + len(y), filtered_by_class)
        filtered_data = {model: [(DatasetsLoader.load_image(self._get_model_image_path(k, model)), v)
                                 for d in filtered_by_class for k, v in d.items()] for model in self._models}
        self._model_images = {model: [sample[0] for sample in filtered_data[model]] for model in self._models}
        self._class_values = [sample[1] for sample in next(iter(filtered_data.values()))] if filtered_data else []

    def _get_model_image_path(self, image_name, model):
        model_image_dir = os.path.join(self._working_dir, model.get_images_dir())
        return os.path.join(model_image_dir, image_name)

    @staticmethod
    def _filter_by_name_suffix(class_values, image_files, class_name):
        return {file: class_name for file in
                filter(lambda f: DatasetsLoader._get_file_suffix(f) in class_values, image_files)}

    @staticmethod
    def _get_file_suffix(file_name):
        return os.path.splitext(file_name)[0].split('_')[-1]

    def perform_bootstrap(self):
        train_indexes = set(numpy.random.choice(self._size, size=self._size, replace=True))
        test_indexes = list(set(range(self._size)) - train_indexes)
        train_indexes = list(train_indexes)
        y_train = numpy.asarray([self._class_values[i] for i in train_indexes]).reshape(len(train_indexes), 1)
        y_test = numpy.asarray([self._class_values[i] for i in test_indexes]).reshape(len(test_indexes), 1)

        x_train = {model: numpy.asarray([self._model_images[model][i] for i in train_indexes])
                   for model in self._models}
        x_test = {model: numpy.asarray([self._model_images[model][i] for i in test_indexes])
                  for model in self._models}

        return (x_train, y_train), (x_test, y_test)

    @staticmethod
    def load_image(path):
        DatasetsLoader._log.debug('Loading image {}'.format(path))
        img = Image.open(path).convert('RGB')
        # noinspection PyTypeChecker
        return numpy.asarray(img, dtype='float32').transpose(2, 0, 1)
