import logging
import os

import dicom


class DicomLoader:
    _DicomExtension = '.dcm'

    @staticmethod
    def _configure_logger():
        logger = logging.getLogger('DicomLoader')
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler('DicomLoader.log')
        fh.setLevel(logging.INFO)
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

    def index_dicoms(self):
        for dir_name, sub_dirs, file_list in os.walk(self._dicom_path):
            for file in file_list:
                if '.dcm' in file.lower():
                    file_path = os.path.join(dir_name, file)
                    try:
                        self._log.info('Found dicom file {}, loading'.format(file_path))
                        ds = dicom.read_file(file_path, stop_before_pixels=True)
                    except Exception as e:
                        self._log.error('Can\'t load dicom file: {} due an error'.format(file_path), e, exc_info=True)
