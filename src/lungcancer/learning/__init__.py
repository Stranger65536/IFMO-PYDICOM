import getopt
import importlib
import logging
import sys

import numpy

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


def main(argv=None):
    if argv is None:
        argv = sys.argv
    opts, args = getopt.getopt(argv[1:], [])
    if len(args) < 2:
        raise ValueError()
    else:
        base_images_path = args[0]
        arg_nets = args[2:]
        if args[1] not in ClassificationType.__members__.keys():
            raise ValueError(args[1] + ' learning mode is not supported!')
        mode = getattr(ClassificationType, args[1])
        models = {}

        for arg_net in arg_nets:
            if arg_net not in supported_models:
                raise ValueError(arg_net + ' is not supported!')
            else:
                models[arg_net] = create_model(base_images_path, mode, arg_net)

        loader = prepare_loader(base_images_path, mode, models)
        # (X_train, y_train), (X_test, y_test) = cifar10.load_data()
        train_samples, test_samples = loader.perform_bootstrap(iterations=100)
        loader.convert_to_dataset(train_samples, test_samples)
        return 0


def create_model(base_images_path, mode, model_name):
    model_class = getattr(importlib.import_module('lungcancer.learning.Models'), model_name)
    return model_class(base_images_path, mode)


def prepare_loader(base_images_path, mode, models):
    loader = DatasetsLoader(base_images_path, mode, models)
    loader.filter_data()
    return loader


def print_help():
    print('Usage: __init__.py <base images directory> <learning mode>\n' +
          ' '.join(['[' + key + ']' for key in sorted(supported_models.keys())]) + '\n' +
          'learning mode - ' + ' / '.join(sorted(ClassificationType.__members__.keys())) +
          ' - defines which classification will be performed')


if __name__ == '__main__':
    sys.exit(main())
