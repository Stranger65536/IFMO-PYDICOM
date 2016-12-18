import imghdr
import os

from PIL import Image

from lungcancer.LoggerUtils import LoggerUtils


class ImageScaler:
    _log = LoggerUtils.get_logger('ImageScaler')

    def __init__(self, images_path):
        self._log.info('Images directory: {}'.format(images_path))
        self._images_path = images_path

    def scale_images(self, size):
        image_counter = 1
        target_dir = os.path.join(self._images_path, str(size) + 'x' + str(size))
        os.makedirs(target_dir, exist_ok=True)
        for file in os.listdir(self._images_path):
            file_path = os.path.join(self._images_path, file)
            if os.path.isfile(file_path) and imghdr.what(file_path):
                try:
                    self._log.debug('Found image file #{} {}, scaling'.format(image_counter, file_path))
                    image_counter += 1
                    im = Image.open(file_path)

                    if im.width < im.height:
                        new_width, new_height = (round(im.width * size / im.height), size)
                        offset = round((size - new_width) / 2), 0
                    else:
                        new_width, new_height = (size, round(im.height * size / im.width))
                        offset = 0, round((size - new_height) / 2)

                    background = Image.new('RGB', (size, size), (0, 0, 0))
                    scaled = im.resize((new_width, new_height), Image.ANTIALIAS)
                    background.paste(scaled, offset)
                    background.save(os.path.join(target_dir, file))
                except IOError:
                    self._log.error('Can\'t load image {} due an error'.format(file_path), exc_info=True)
