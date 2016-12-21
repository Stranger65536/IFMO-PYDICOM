import getopt
import importlib
import logging
import sys

import numpy
from keras.utils.np_utils import to_categorical

from lungcancer.learning.DatasetsLoader import ClassificationType, DatasetsLoader
from lungcancer.learning.Models import *

importlib.reload(logging)

numpy.random.seed(172488)

supported_models = {
    'LeNet': type(LeNet),
    'ResNet': type(ResNet),
    'GoogLeNet': type(GoogLeNet),
    'OxfordNet': type(OxfordNet),
    'ZFNet': type(ZFNet),
    'AlexNet': type(AlexNet),
    'NIN': type(NIN),
    'Overfeat': type(Overfeat),
    'SPPNet': type(SPPNet),
    'RCNN': type(RCNN),
    'STN': type(STN),
    'RSTN': type(RSTN),
    'FMP': type(FMP)
}

_log = LoggerUtils.get_logger('Learn')


def main(argv=None):
    if argv is None:
        argv = sys.argv
    opts, args = getopt.getopt(argv[1:], [])
    if len(args) < 2:
        raise ValueError()
    else:
        base_images_path = args[0]
        arg_nets = args[2:]
        mode = parse_mode(args)
        models = parse_models(arg_nets, base_images_path, mode)
        loader = DatasetsLoader(base_images_path, mode, models)
        loader.load_data()

        for i in range(100):
            _log.info('Bootstrap iteration {}'.format(i))
            (X_train_models, y_train), (X_test_models, y_test) = loader.perform_bootstrap()
            for model in models:
                _log.debug('Model {}'.format(str(type(model))))
                classifier = model.build()
                X_test, X_train, y_test, y_train = prepare_data(X_test_models, X_train_models,
                                                                mode, model,
                                                                y_test, y_train)
                classifier.compile(loss='binary_crossentropy',
                                   optimizer='rmsprop',
                                   metrics=['precision', 'recall', 'fmeasure', 'fbeta_score', 'matthews_correlation',
                                            'binary_crossentropy', 'binary_accuracy'])
                classifier.fit(X_train, y_train, batch_size=128, nb_epoch=1, validation_data=(X_test, y_test))
                classifier.evaluate(X_test, y_test)
                pass
        return 0


def prepare_data(x_test_models, x_train_models, mode, model, y_test, y_train):
    X_train = x_train_models[model]
    X_test = x_test_models[model]
    X_train /= 255
    X_test /= 255
    n_classes = len(mode.value)
    y_train = to_categorical(y_train, n_classes)
    y_test = to_categorical(y_test, n_classes)
    return X_test, X_train, y_test, y_train


def parse_models(arg_nets, base_images_path, mode):
    models = []
    for arg_net in arg_nets:
        if arg_net not in supported_models:
            raise ValueError(arg_net + ' is not supported!')
        else:
            models.append(create_model(base_images_path, mode, arg_net))
    return models


def parse_mode(args):
    if args[1] not in ClassificationType.__members__.keys():
        raise ValueError(args[1] + ' learning mode is not supported!')
    mode = getattr(ClassificationType, args[1])
    return mode


def create_model(base_images_path, mode, model_name):
    model_class = getattr(importlib.import_module('lungcancer.learning.Models'), model_name)
    return model_class(base_images_path, mode)


def print_help():
    print('Usage: __init__.py <base images directory> <learning mode>\n' +
          ' '.join(['[' + key + ']' for key in sorted(supported_models.keys())]) + '\n' +
          'learning mode - ' + ' / '.join(sorted(ClassificationType.__members__.keys())) +
          ' - defines which classification will be performed')


if __name__ == '__main__':
    sys.exit(main())
