from keras.layers.convolutional import Convolution2D
from keras.layers.convolutional import MaxPooling2D
from keras.layers.core import Activation
from keras.layers.core import Dense
from keras.layers.core import Flatten
from keras.models import Sequential

from lungcancer.LoggerUtils import LoggerUtils


class Net:
    _depth = 3  # RGB

    def __init__(self, base_images_path, mode):
        self._base_images_path = base_images_path
        self._mode = mode
        self._classes = len(mode.value)

    def build(self):
        raise NotImplementedError("You have to override this method into your model!")


class ResNet:
    _log = LoggerUtils.get_logger('ResNet')
    # TODO
    pass


class GoogLeNet:
    _log = LoggerUtils.get_logger('GoogLeNet')
    # TODO
    pass


class OxfordNet:
    _log = LoggerUtils.get_logger('OxfordNet')
    # TODO
    pass


class ZFNet:
    _log = LoggerUtils.get_logger('ZFNet')
    # TODO
    pass


class AlexNet:
    _log = LoggerUtils.get_logger('AlexNet')
    # TODO
    pass


class NIN:
    _log = LoggerUtils.get_logger('NIN')
    # TODO
    pass


class Overfeat:
    _log = LoggerUtils.get_logger('Overfeat')
    # TODO
    pass


class SPPNet:
    _log = LoggerUtils.get_logger('SPPNet')
    # TODO
    pass


class RCNN:
    _log = LoggerUtils.get_logger('RCNN')
    # TODO
    pass


class STN:
    _log = LoggerUtils.get_logger('STN')
    # TODO
    pass


class RSTN:
    _log = LoggerUtils.get_logger('RSTN')
    # TODO
    pass


class FMP:
    _log = LoggerUtils.get_logger('FMP')
    # TODO
    pass


class LeNet(Net):
    _log = LoggerUtils.get_logger('LeNet')

    def __init__(self, base_images_path, mode):
        super().__init__(base_images_path, mode)
        self._width = 28
        self._height = 28
        self._log.info('initialized')

    # INPUT => CONV => RELU => POOL => CONV => RELU => POOL => FC => RELU => FC
    def build(self):
        # initialize the model
        model = Sequential()
        # first set of CONV => RELU => POOL
        model.add(Convolution2D(20, 5, 5, border_mode="same",
                                input_shape=(self._depth, self._height, self._width)))
        model.add(Activation("relu"))
        model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
        # second set of CONV => RELU => POOL
        model.add(Convolution2D(50, 5, 5, border_mode="same"))
        model.add(Activation("relu"))
        model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
        # set of FC => RELU layers
        model.add(Flatten())
        model.add(Dense(500))
        model.add(Activation("relu"))

        # softmax classifier
        model.add(Dense(self._classes))
        model.add(Activation("softmax"))

        # return the constructed network architecture
        return model
