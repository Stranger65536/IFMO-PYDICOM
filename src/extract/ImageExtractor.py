# coding=utf-8
from os import makedirs
from os.path import join

from LoggerUtils import LoggerUtils
from Utils import create_cache
from extract.AnnotationsLoader import AnnotationsLoader
from extract.DicomLoader import DicomLoader
from extract.DicomLoader import extract_image
from extract.PatientDiagnosisLoader import PatientDiagnosisLoader

log = LoggerUtils.get_logger('ImageExtractor')
slices_cache_name = 'extracted_slices.cache'


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
                   output_path,
                   export_all_images,
                   export_full_images):
    log.info('Loading nodule annotations....')
    nodules = read_annotations(annotations_path)
    log.info('Loading diagnosis....')
    diagnosis = read_diagnosis(diagnosis_path)
    log.info('Loading dicoms metadata....')
    metadata = read_dicoms_metadata(dicoms_path)
    log.info('Dicoms metadata loaded')

    makedirs(output_path, exist_ok=True)

    if export_full_images:
        makedirs(join(output_path, 'full'), exist_ok=True)

    log.info('Extracting images')

    nodule_count = 1
    extracted_nodules = set()

    for nodule in nodules:
        log.info('Processing nodule {} of {}'
                 .format(nodule_count, len(nodules)))
        nodule_count += 1
        process_nodule(nodule,
                       metadata,
                       diagnosis,
                       export_all_images,
                       export_full_images,
                       output_path,
                       extracted_nodules)

    log.info('{} nodule slices extracted successfully'
             .format(sum([len(i.slices) for i in extracted_nodules])))

    cache_file = join(output_path, slices_cache_name)

    log.info('Creating cache with extracted slices info: {}'
             .format(cache_file))
    create_cache(cache_file, extracted_nodules, log)


def process_nodule(nodule,
                   metadata,
                   diagnosis,
                   export_all_images,
                   export_full_images,
                   output_path,
                   extracted_nodules):
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
        extracted_slices = set()

        for nodule_slice in nodule.slices:
            log.debug('Processing slice {} of {}'
                      .format(slice_count, len(nodule.slices)))
            slice_count += 1
            image_uid = nodule_slice.image_uid
            if image_uid not in metadata[study][series]:
                log.error('No dicom file found for nodule '
                          'with image id {}!'.format(image_uid))
            else:
                dicom_path = metadata[study][series][image_uid]
                extracted = extract_image(dicom_path,
                                          nodule,
                                          nodule_slice,
                                          export_all_images,
                                          export_full_images,
                                          diagnosis,
                                          output_path)
                if extracted:
                    extracted_slices.add(nodule_slice)

        if extracted_slices:
            # update nodule with exported slices only
            nodule.slices.clear()
            nodule.slices.update(extracted_slices)
            extracted_nodules.add(nodule)
