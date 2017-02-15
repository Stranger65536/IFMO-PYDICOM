# coding=utf-8
import logging
from argparse import ArgumentParser
from importlib import reload

from learning.Datasets import supported_datasets, LIDCCancerType, \
    LIDCMalignancy
from learning.LearningExecutor import execute_learning
from learning.Models import supported_models

reload(logging)


def main():
    parser = ArgumentParser(
        description='Performs learning using '
                    'specified datasets and model')
    parser.add_argument('-d', '--dataset',
                        dest='dataset',
                        metavar='DATASET',
                        required=True,
                        help='Dataset to perform learning. '
                             'Supported datasets: {}'
                        .format(
                            sorted(list(supported_datasets.keys()))))
    parser.add_argument('-m', '--models',
                        dest='models',
                        metavar='MODELS',
                        nargs='+',
                        required=True,
                        help='List of models to perform learning.'
                             'Supported models: {}'
                        .format(sorted(list(supported_models.keys()))))
    parser.add_argument('-i', '--iterations',
                        dest='iterations',
                        metavar='ITERATION_NUMBER',
                        type=int,
                        required=True,
                        help='Number of bootstrap iterations')
    parser.add_argument('-o', '--output_file',
                        dest='output_file',
                        metavar='OUTPUT_FILE',
                        required=True,
                        help='Path to file to write results to')
    parser.add_argument('-I', '--images_path',
                        dest='images_path',
                        metavar='IMAGES_PATH',
                        required=False,
                        help='Specified path to extracted nodule '
                             'images with extracted nodules '
                             'info cache for LIDC models')
    args = parser.parse_args()

    for model in args.models:
        if model not in supported_models:
            print('Model is not supported: {}!'.format(model))
            parser.print_help()
            exit(-1)

    models = [supported_models[i]() for i in args.models]

    if args.dataset not in supported_datasets:
        print('Dataset is not supported: {}!'.format(args.dataset))
        parser.print_help()
        exit(-1)
    if supported_datasets[args.dataset] \
            in [LIDCCancerType, LIDCMalignancy] \
            and not args.images_path:
        print('images_path must be specified for LIDC datasets!')
        parser.print_help()
        exit(-1)

    dataset = supported_datasets[args.dataset](args)

    execute_learning(dataset,
                     models,
                     args.iterations,
                     args.output_file)


if __name__ == '__main__':
    main()
