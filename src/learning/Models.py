# coding=utf-8
from keras.layers import Activation
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers.convolutional import Convolution2D
from keras.layers.convolutional import MaxPooling2D
from keras.models import Sequential
from keras.regularizers import l2

depth = 1  # Grayscale


class Net(object):
    _size = None

    def __init__(self):
        super().__init__()

    def build(self):
        raise NotImplementedError(
            "You have to override this method into your model!")

    @property
    def size(self):
        return self._size


class GoogLeNet:
    # TODO
    pass


class VGG16:
    # TODO
    pass


class ZFNet:
    # TODO
    pass


class AlexNet:
    # TODO
    pass


class NIN:
    # TODO
    pass


class Overfeat:
    # TODO
    pass


class SPPNet:
    # TODO
    pass


class RCNN:
    # TODO
    pass


class STN:
    # TODO
    pass


class RSTN:
    # TODO
    pass


class FMP:
    # TODO
    pass


class LeNet(Net):
    def __init__(self):
        super().__init__()
        self._size = 28

    def build(self):
        model = Sequential(name='LeNet')

        model.add(Convolution2D(20, 5, 5,
                                border_mode='same',
                                input_shape=(depth,
                                             self.size,
                                             self.size)))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2),
                               strides=(2, 2)))
        model.add(Convolution2D(20, 5, 5,
                                border_mode='same'))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2),
                               strides=(2, 2)))
        model.add(Flatten())
        model.add(Dense(500))
        model.add(Activation('relu'))

        model.add(Dense(2, W_regularizer=l2(0.001)))
        model.add(Activation('softmax'))

        return model


class ResNet(Net):
    def __init__(self):
        super().__init__()
        self._size = 224

    def build(self):
        model = Sequential(name='ResNet')

        model.add(Convolution2D(64, 3, 3,
                                activation='relu',
                                border_mode='same',
                                name='block1_conv1',
                                input_shape=(depth,
                                             self._size,
                                             self._size)))
        model.add(Convolution2D(64, 3, 3,
                                activation='relu',
                                border_mode='same',
                                name='block1_conv2'))
        model.add(MaxPooling2D(pool_size=(2, 2),
                               strides=(2, 2),
                               name='block1_pool'))
        model.add(Convolution2D(128, 3, 3,
                                activation='relu',
                                border_mode='same',
                                name='block2_conv1'))
        model.add(Convolution2D(128, 3, 3,
                                activation='relu',
                                border_mode='same',
                                name='block2_conv2'))
        model.add(MaxPooling2D(pool_size=(2, 2),
                               strides=(2, 2),
                               name='block2_pool'))
        model.add(Convolution2D(256, 3, 3,
                                activation='relu',
                                border_mode='same',
                                name='block3_conv1'))
        model.add(Convolution2D(256, 3, 3,
                                activation='relu',
                                border_mode='same',
                                name='block3_conv2'))
        model.add(Convolution2D(256, 3, 3,
                                activation='relu',
                                border_mode='same',
                                name='block3_conv3'))
        model.add(MaxPooling2D(pool_size=(2, 2),
                               strides=(2, 2),
                               name='block3_pool'))
        model.add(Convolution2D(512, 3, 3,
                                activation='relu',
                                border_mode='same',
                                name='block4_conv1'))
        model.add(Convolution2D(512, 3, 3,
                                activation='relu',
                                border_mode='same',
                                name='block4_conv2'))
        model.add(Convolution2D(512, 3, 3,
                                activation='relu',
                                border_mode='same',
                                name='block4_conv3'))
        model.add(MaxPooling2D(pool_size=(2, 2),
                               strides=(2, 2),
                               name='block4_pool'))
        model.add(Convolution2D(512, 3, 3,
                                activation='relu',
                                border_mode='same',
                                name='block5_conv1'))
        model.add(Convolution2D(512, 3, 3,
                                activation='relu',
                                border_mode='same',
                                name='block5_conv2'))
        model.add(Convolution2D(512, 3, 3,
                                activation='relu',
                                border_mode='same',
                                name='block5_conv3'))
        model.add(MaxPooling2D(pool_size=(2, 2),
                               strides=(2, 2),
                               name='block5_pool'))

        model.add(Flatten(name='flatten'))
        model.add(Dense(2, activation='relu', name='fc1'))
        model.add(Dense(2, activation='relu', name='fc2'))
        model.add(Dense(2, activation='softmax', name='predictions'))

        return model


supported_models = {
    'LeNet': LeNet,
    'ResNet': ResNet,
    'GoogLeNet': GoogLeNet,
    'VGG16': VGG16,
    'ZFNet': ZFNet,
    'AlexNet': AlexNet,
    'NIN': NIN,
    'Overfeat': Overfeat,
    'SPPNet': SPPNet,
    'RCNN': RCNN,
    'STN': STN,
    'RSTN': RSTN,
    'FMP': FMP
}
