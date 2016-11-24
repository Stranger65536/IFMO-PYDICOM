import os

from lungcancer.LoggerUtils import LoggerUtils
from lungcancer.extract.AnnotationsLoader import AnnotationsLoader
from lungcancer.extract.DicomLoader import DicomLoader
from lungcancer.extract.PatientDiagnosisLoader import PatientDiagnosisLoader


class ImageExtractor:
    _log = LoggerUtils.get_logger('ImageExtractor')

    @staticmethod
    def extract(annotations_path, diagnosis_path, dicoms_path, output_path):
        ImageExtractor._log.info('Loading nodule annotations....')
        nodules = ImageExtractor._read_annotations(annotations_path)
        ImageExtractor._log.info('{} nodules loaded'.format(len(nodules)))
        ImageExtractor._log.info('Loading diagnosis....')
        diagnosis = ImageExtractor._read_diagnosis(diagnosis_path)
        ImageExtractor._log.info('{} diagnoses loaded'.format(len(diagnosis)))
        ImageExtractor._log.info('Loading dicoms metadata....')
        metadata = ImageExtractor._read_dicoms_metadata(dicoms_path)
        ImageExtractor._log.info('Dicoms metadata loaded')

        os.makedirs(output_path, exist_ok=True)
        os.makedirs(os.path.join(output_path, 'nodules'), exist_ok=True)
        os.makedirs(os.path.join(output_path, 'full'), exist_ok=True)

        ImageExtractor._log.info('Extracting images')

        processed_count = 0
        extracted_count = 0
        for nodule in nodules:
            ImageExtractor._log.debug('Processing nodule extraction {} of {}'.format(processed_count, len(nodules)))
            study = nodule.get_study()
            series = nodule.get_series()
            image_uid = nodule.get_image_uid()
            if study not in metadata:
                ImageExtractor._log.error('No dicom file found for nodule with study id {}!'.format(study))
            elif series not in metadata[study]:
                ImageExtractor._log.error('No dicom file found for nodule with series id {}!'.format(series))
            elif image_uid not in metadata[study][series]:
                ImageExtractor._log.error('No dicom file found for nodule with image id {}!'.format(image_uid))
            else:
                extracted = DicomLoader.extract_images(metadata[study][series][image_uid],
                                                       nodule, diagnosis, output_path)
                extracted_count += int(extracted)
            processed_count += 1
            ImageExtractor._log.debug('{} nodules of {} processed'.format(processed_count, len(nodules)))
        ImageExtractor._log.info('{} nodule images extracted'.format(extracted_count))

    @staticmethod
    def _read_dicoms_metadata(path):
        dicom_loader = DicomLoader(path)
        metadata = dicom_loader.load_dicoms_metadata()
        return metadata

    @staticmethod
    def _read_diagnosis(path):
        diagnosis_loader = PatientDiagnosisLoader(path)
        diagnosis = diagnosis_loader.load_dicoms_metadata()
        return diagnosis

    @staticmethod
    def _read_annotations(path):
        annotations_loader = AnnotationsLoader(path)
        nodules = annotations_loader.load_nodules_annotations()
        return nodules
