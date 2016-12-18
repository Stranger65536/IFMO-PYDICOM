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
    try:
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
                    models[arg_net] = None
            build_models(base_images_path, mode, models)
            loader = prepare_loader(base_images_path, mode, models)
            return 0
    except ValueError as e:
        if e:
            print(e)
        print_help()
        return 1


def build_models(base_images_path, mode, models):
    for model in sorted(models.keys()):
        model_class = getattr(importlib.import_module('lungcancer.learning.Models'), model)
        instance = model_class(base_images_path, mode)
        models[model] = instance


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
