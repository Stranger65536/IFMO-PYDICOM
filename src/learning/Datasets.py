# coding=utf-8
from imghdr import what
from os import listdir
from os.path import isfile, splitext
from os.path import join

from PIL import Image
from PIL.Image import ANTIALIAS
from PIL.Image import new
from keras.datasets import cifar10
from keras.datasets import mnist
from numpy import asarray
from numpy import concatenate

from LoggerUtils import LoggerUtils
from Utils import load_cache, create_cache

cache_file_name = 'images.cache'
cache_file_name_ct = 'images_ct.cache'
cache_file_name_m = 'images_m.cache'
log = LoggerUtils.get_logger('Datasets')


class Dataset(object):
    _x = None
    _y = None

    def __init__(self, args):
        super().__init__()

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y


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
                 .format(type(MNIST).__name__))


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
                 .format(type(CIFAR10).__name__))


class LIDC(Dataset):
    def __init__(self, args):
        super().__init__(args)
        self._cache_file_name = cache_file_name
        self._images_path = args.images_path

        cache_file = join(self._images_path, cache_file_name)

        if isfile(cache_file):
            log.info('Found cache file with LIDC images, '
                     'delete it to reload: {}. Loading...'
                     .format(cache_file))
            self._x, self._y = load_cache(cache_file)
        else:
            log.info('Scanning image files')

            image_files = [join(self._images_path, file) for file
                           in listdir(self._images_path)
                           if isfile(join(self._images_path, file))
                           and what(join(self._images_path, file))]

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
                 .format(type(LIDCCancerType).__name__))


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
                 .format(type(LIDCMalignancy).__name__))


def load_image(path):
    log.debug('Loading image {}'.format(path))
    return asarray(Image.open(path).convert('L'), dtype='uint8')


def scale_image(im, size):
    if im.width < im.height:
        width, height = (round(im.width * size / im.height), size)
        offset = round((size - width) / 2), 0
    else:
        width, height = (size, round(im.height * size / im.width))
        offset = 0, round((size - height) / 2)

    background = new('L', (size, size))
    scaled = im.resize((width, height), ANTIALIAS)
    background.paste(scaled, offset)

    return background


def file_suffix(file_name):
    return int(splitext(file_name)[0].split('_')[-1])


supported_datasets = {
    'MNIST': type(MNIST),  # 0 and 1 handwritten images only
    'CIFAR10': type(CIFAR10),  # cats and dogs only
    'LIDC-Cancer-Type': type(LIDCCancerType),  # Two cancer types
    'LIDC-Malignancy': type(LIDCMalignancy)  # Malignant or not
}
