# coding=utf-8
from functools import reduce
from os.path import isfile
from os.path import join
from os.path import splitext

from PIL import Image
from keras.datasets import cifar10
from keras.datasets import mnist
from numpy import asarray
from numpy import concatenate
from numpy.random import choice

from LoggerUtils import LoggerUtils
from Utils import create_cache
from Utils import load_cache
from extract.DicomLoader import slice_image_name
from extract.ImageExtractor import slices_cache_name

min_area = 100
cache_file_name = 'images.cache'
cache_file_name_ct = 'images_ct.cache'
cache_file_name_m = 'images_m.cache'
log = LoggerUtils.get_logger('Datasets')


class Dataset(object):
    _x = None
    _y = None

    # noinspection PyUnusedLocal
    def __init__(self, args):
        super().__init__()

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def bootstrap_iter(self):
        train_indexes = set(choice(self.y.shape[0],
                                   size=self.y.shape[0],
                                   replace=True))
        test_indexes = list(set(range(self.y.shape[0])) - train_indexes)
        train_indexes = list(train_indexes)

        y_train = asarray([self.y[i] for i in train_indexes])
        y_test = asarray([self.y[i] for i in test_indexes])

        x_train = asarray([self.x[i] for i in train_indexes])
        x_test = asarray([self.x[i] for i in test_indexes])

        return (x_train, y_train), (x_test, y_test)


class MNIST(Dataset):
    def __init__(self, args):
        super().__init__(args)
        (x_train, y_train), (x_test, y_test) = mnist.load_data()
        x = concatenate((x_train, x_test))
        y = concatenate((y_train, y_test))
        filtered = [(x, y) for (x, y) in zip(x, y) if y < 2]
        self._x = list(asarray([x for (x, y) in filtered]))
        self._y = asarray([y for (x, y) in filtered])
        log.info('Dataset {} successfully imported'
                 .format(MNIST.__name__))


class CIFAR10(Dataset):
    def __init__(self, args):
        super().__init__(args)
        (x_train, y_train), (x_test, y_test) = cifar10.load_data()
        x = concatenate((x_train, x_test))
        y = concatenate((y_train, y_test))
        filtered = [(x, y) for (x, y) in zip(x, y) if y < 2]
        self._x = list(asarray([x for (x, y) in filtered])
                       .transpose((0, 2, 3, 1)))
        self._y = asarray([y for (x, y) in filtered])
        log.info('Dataset {} successfully imported'
                 .format(CIFAR10.__name__))


class LIDC(Dataset):
    def __init__(self, args):
        super().__init__(args)
        self._cache_file_name = cache_file_name
        self._images_path = args.images_path

        cache_file = join(self._images_path, cache_file_name)
        slices_cache_file = join(self._images_path, slices_cache_name)

        if isfile(cache_file):
            log.info('Found cache file with LIDC images, '
                     'delete it to reload: {}. Loading...'
                     .format(cache_file))
            self._x, self._y = load_cache(cache_file)
        else:
            log.info('Loading exported slices info from cache {}'
                     .format(slices_cache_file))

            extracted_nodules = load_cache(slices_cache_file)

            log.info('Computing nodule slices with the biggest area '
                     'greater than {}'.format(min_area))

            image_files = [slice_image_name(self._images_path,
                                            nodule,
                                            biggest_slice(nodule))
                           for nodule in extracted_nodules
                           if biggest_slice(nodule).area > min_area]

            log.info('{} slices have been selected to load'
                     .format(len(image_files)))

            log.info('Loading images')

            self._x = [load_image(f) for f in image_files]
            classes = [file_suffix(file) for file in image_files]
            self._y = asarray(classes, dtype='uint8')

            log.info('Creating images cache: {}'
                     .format(cache_file))
            create_cache(cache_file, (self._x, self._y), log)

        log.info('{} images have been loaded'.format(self._y.shape[0]))

    def filter(self, classes):
        filtered = [(x, classes[y]) for (x, y)
                    in zip(self._x, self._y) if y in classes]
        self._x = list(asarray([x for (x, y) in filtered]))
        self._y = asarray([y for (x, y) in filtered])


class LIDCCancerType(LIDC):
    cache_file_name = cache_file_name_ct
    classes = {2: 0, 3: 1}

    def __init__(self, args):
        super().__init__(args)

        cache_file = join(self._images_path, cache_file_name_ct)

        if isfile(cache_file):
            log.info('Found cache file with filtered LIDC images, '
                     'delete it to reload: {}. Loading...'
                     .format(cache_file))
            self._x, self._y = load_cache(cache_file)
        else:
            log.info('Filtering images according to the class values')
            self.filter(LIDCCancerType.classes)
            log.info('Creating filtered images cache: {}'
                     .format(cache_file))
            create_cache(cache_file, (self._x, self._y), log)
        log.info('{} images left after filtering'
                 .format(self._y.shape[0]))

        log.info('Dataset {} successfully imported'
                 .format(LIDCCancerType.__name__))


class LIDCMalignancy(LIDC):
    cache_file_name = cache_file_name_m
    classes = {1: 0, 2: 1, 3: 1}

    def __init__(self, args):
        super().__init__(args)

        cache_file = join(self._images_path, cache_file_name_m)

        if isfile(cache_file):
            log.info('Found cache file with filtered LIDC images, '
                     'delete it to reload: {}. Loading...'
                     .format(cache_file))
            self._x, self._y = load_cache(cache_file)
        else:
            log.info('Filtering images according to the class values')
            self.filter(LIDCMalignancy.classes)
            log.info('Creating filtered images cache: {}'
                     .format(cache_file))
            create_cache(cache_file, (self._x, self._y), log)
        log.info('{} images left after filtering'
                 .format(self._y.shape[0]))

        log.info('Dataset {} successfully imported'
                 .format(LIDCMalignancy.__name__))


def load_image(path):
    log.debug('Loading image {}'.format(path))
    return asarray(Image.open(path).convert('L'), dtype='uint8')


def biggest_slice(nodule):
    return reduce(lambda a, b:
                  a if a.area > b.area else b,
                  nodule.slices)


def file_suffix(file_name):
    return int(splitext(file_name)[0].split('_')[-1])


supported_datasets = {
    'MNIST': MNIST,  # 0 and 1 handwritten images only
    'CIFAR10': CIFAR10,  # cats and dogs only
    'LIDC-Cancer-Type': LIDCCancerType,  # Two cancer types
    'LIDC-Malignancy': LIDCMalignancy  # Malignant or not
}
