import getopt
import importlib
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from lungcancer.AnnotationsLoader import AnnotationsLoader
from lungcancer.DicomLoader import DicomLoader
from lungcancer.PatientDiagnosisLoader import PatientDiagnosisLoader

importlib.reload(logging)


def configure_logger():
    logger = logging.getLogger('__init__')

    logger.setLevel(logging.DEBUG)
    fh = RotatingFileHandler('__init__.log', mode='a', maxBytes=10 * 1024 * 1024,
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


log = configure_logger()


def main(argv=None):
    if argv is None:
        argv = sys.argv
    opts, args = getopt.getopt(argv[1:], [])
    if len(args) < 3:
        log.error('Usage: __init__.py <annotations directory> '
                  '<diagnosis directory> <dicom_directory> <output_directory>\n'
                  'annotations directory - all *.xml files from the '
                  'specified directory will be treated as annotations\n'
                  'diagnosis directory - all *.csv files from the '
                  'specified directory will be treated as patients '
                  'diagnosis and will override corresponding '
                  'malignancy characteristic from annotations\n'
                  'dicom_directory - all *.dcm files from the '
                  'specified directory will be treated as dicom files and '
                  'parsed for nodule images extraction '
                  'according to the loaded annotations\n'
                  'output_directory - all nodule images will '
                  'be stored in the specified directory')
        return 1
    else:
        log.info('Loading nodule annotations....')
        nodules = read_annotations(args[0])
        log.info('{} nodules loaded'.format(len(nodules)))
        log.info('Loading diagnosis....')
        diagnosis = read_diagnosis(args[1])
        log.info('{} diagnoses loaded'.format(len(diagnosis)))
        log.info('Loading dicoms metadata....')
        metadata = read_dicoms_metadata(args[2])
        log.info('Dicoms metadata loaded')
        output_path = args[3]
        os.makedirs(output_path, exist_ok=True)

        for nodule in nodules:
            study = nodule.get_study()
            series = nodule.get_series()
            image_uid = nodule.get_image_uid()
            if study not in metadata:
                log.error('No dicom file found for nodule with study id {}!'.format(study))
            if series not in metadata[study]:
                log.error('No dicom file found for nodule with series id {}!'.format(series))
            if image_uid not in metadata[study][series]:
                log.error('No dicom file found for nodule with image id {}!'.format(image_uid))
            DicomLoader.extract_images(metadata[study][series][image_uid], nodule, output_path)
        return 0


def read_dicoms_metadata(path):
    dicom_loader = DicomLoader(path)
    metadata = dicom_loader.load_dicoms_metadata()
    return metadata


def read_diagnosis(path):
    diagnosis_loader = PatientDiagnosisLoader(path)
    diagnosis = diagnosis_loader.load_dicoms_metadata()
    return diagnosis


def read_annotations(path):
    annotations_loader = AnnotationsLoader(path)
    nodules = annotations_loader.load_nodules_annotations()
    return nodules


if __name__ == '__main__':
    sys.exit(main())
