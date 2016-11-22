import logging
import os
from logging.handlers import RotatingFileHandler

import dicom
import numpy
from PIL import Image


class DicomLoader:
    _DicomExtension = '.dcm'

    @staticmethod
    def _configure_logger():
        logger = logging.getLogger('DicomLoader')
        logger.setLevel(logging.DEBUG)
        fh = RotatingFileHandler('DicomLoader.log', mode='a', maxBytes=10 * 1024 * 1024,
                                 backupCount=0, encoding=None, delay=0)
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger

    # noinspection PyUnresolvedReferences
    _log = _configure_logger.__func__()

    def __init__(self, dicom_path):
        self._log.info('Dicoms directory: {}'.format(dicom_path))
        self._dicom_path = dicom_path

    def load_dicoms_metadata(self):
        file_counter = 1
        study_data = {}
        for dir_name, sub_dirs, file_list in os.walk(self._dicom_path):
            for file in file_list:
                if self._DicomExtension in file.lower():
                    file_path = os.path.join(dir_name, file)
                    try:
                        self._log.debug('Found dicom file #{} {}, loading'.format(file_counter, file_path))
                        file_counter += 1
                        ds = dicom.read_file(file_path, stop_before_pixels=True)
                        image_uid = ds["0008", "0018"].value
                        self._check_initialized(image_uid, 'image_uid')
                        study = ds["0020", "000d"].value
                        self._check_initialized(image_uid, 'study_id')
                        series = ds["0020", "000e"].value
                        self._check_initialized(image_uid, 'series_id')
                        series_data = study_data.get(study, {})
                        image_data = series_data.get(series, {})
                        if image_uid in image_data:
                            self._log.warn('Found duplicate image_uid in files: {}; {}'
                                           .format(image_data[image_uid], file_path))
                        image_data[image_uid] = file_path
                        series_data[series] = image_data
                        study_data[study] = series_data
                    except Exception as e:
                        self._log.error('Can\'t load dicom file: {} due an error'.format(file_path), e, exc_info=True)
        return study_data

    @staticmethod
    def extract_images(dicom_path, nodule, output_path):
        file_counter = 1
        try:
            DicomLoader._log.debug('Loading dicom file #{} {}'.format(file_counter, dicom_path))
            file_counter += 1
            ds = dicom.read_file(dicom_path)
            height, width = (int(ds.Rows), int(ds.Columns))
            x = numpy.arange(0.0, (height + 1) * height, height)
            y = numpy.arange(0.0, (width + 1) * width, width)
            image = ds.pixel_array
            mask = numpy.zeros_like(img)
            im = Image.fromarray(image).convert('RGB')
            im.save(os.path.join(output_path, DicomLoader._get_original_image_file_name(nodule)))
        except Exception as e:
            DicomLoader._log.error('Can\'t load dicom file: {} due an error'.format(dicom_path), e, exc_info=True)

    @staticmethod
    def _get_original_image_file_name(nodule):
        study = nodule.get_study()
        series = nodule.get_series()
        image_uid = nodule.get_image_uid()
        nodule_uid = format(int(nodule.get_nodule_id()), '010d')
        return study + '_' + series + '_' + image_uid + '_' + nodule_uid + '_full.bmp'

    @staticmethod
    def _get_nodule_image_file_name(nodule):
        study = nodule.get_study()
        series = nodule.get_series()
        image_uid = nodule.get_image_uid()
        nodule_uid = format(int(nodule.get_nodule_id()), '010d')
        return study + '_' + series + '_' + image_uid + '_' + nodule_uid + '.bmp'

    @staticmethod
    def _check_initialized(value, error_smg):
        if not value:
            raise ValueError('{} must be present in dicom file!'.format(error_smg))
