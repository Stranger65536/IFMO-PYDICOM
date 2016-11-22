import logging
import os
from logging.handlers import RotatingFileHandler

import dicom


class DicomLoader:
    _DicomExtension = '.dcm'

    @staticmethod
    def _configure_logger():
        logger = logging.getLogger('DicomLoader')
        logger.setLevel(logging.DEBUG)
        fh = RotatingFileHandler('DicomLoader.log', mode='a', maxBytes=10 * 1024 * 1024,
                                 backupCount=2, encoding=None, delay=0)
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
    def _check_initialized(value, error_smg):
        if not value:
            raise ValueError('{} must be present in dicom file!'.format(error_smg))
