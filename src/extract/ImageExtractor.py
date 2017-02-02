# coding=utf-8
from os import makedirs
from os.path import join

from LoggerUtils import LoggerUtils
from extract.AnnotationsLoader import AnnotationsLoader
from extract.DicomLoader import DicomLoader
from extract.DicomLoader import extract_image
from extract.PatientDiagnosisLoader import PatientDiagnosisLoader

log = LoggerUtils.get_logger('ImageExtractor')


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


def extract_images(dicoms_path,
                   annotations_path,
                   diagnosis_path,
                   output_path):
    log.info('Loading nodule annotations....')
    nodules = read_annotations(annotations_path)
    log.info('Loading diagnosis....')
    diagnosis = read_diagnosis(diagnosis_path)
    log.info('Loading dicoms metadata....')
    metadata = read_dicoms_metadata(dicoms_path)
    log.info('Dicoms metadata loaded')

    makedirs(output_path, exist_ok=True)
    makedirs(join(output_path, 'nodules'), exist_ok=True)
    makedirs(join(output_path, 'full'), exist_ok=True)

    log.info('Extracting images')

    nodule_count = 0
    extracted_slices_count = 0

    for nodule in nodules:
        log.info('Processing nodule {} of {}'
                 .format(nodule_count, len(nodules)))
        study = nodule.study
        series = nodule.series

        if study not in metadata:
            log.error('No dicom file found for nodule '
                      'with study id {}!'.format(study))
        elif series not in metadata[study]:
            log.error('No dicom file found for nodule '
                      'with series id {}!'.format(series))
        else:
            slice_count = 1
            for nodule_slice in nodule.slices:
                log.debug('Processing slice {} of {}'
                          .format(slice_count, len(nodule.slices)))
                image_uid = nodule_slice.image_uid
                if image_uid not in metadata[study][series]:
                    log.error('No dicom file found for nodule '
                              'with image id {}!'.format(image_uid))
                else:
                    dicom_path = metadata[study][series][image_uid]
                    extracted = extract_image(dicom_path,
                                              nodule,
                                              nodule_slice,
                                              diagnosis,
                                              output_path)
                    slice_count += 1
                    extracted_slices_count += int(extracted)
        nodule_count += 1

    log.info('{} nodule slices of extracted successfully'
             .format(extracted_slices_count))
