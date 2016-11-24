import os

import dicom
import numpy
from PIL import Image
from matplotlib.path import Path

from lungcancer.LoggerUtils import LoggerUtils


class DicomLoader:
    _DicomExtension = '.dcm'
    _DiagnosisUnknown = '0'

    _log = LoggerUtils.get_logger('DicomLoader')

    def __init__(self, dicom_path):
        self._log.info('Dicoms directory: {}'.format(dicom_path))
        self._dicom_path = dicom_path

    # noinspection PyBroadException
    def load_dicoms_metadata(self):
        file_counter = 1
        study_data = {}
        for dir_name, sub_dirs, file_list in os.walk(self._dicom_path):
            for file in file_list:
                if self._DicomExtension in file.lower():
                    file_path = os.path.join(dir_name, file)
                    try:
                        self._log.debug('Found dicom file #{} {}, loading'
                                        .format(file_counter, file_path))
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
                    except Exception:
                        self._log.error('Can\'t load dicom file: {} due an error'
                                        .format(file_path), exc_info=True)
        return study_data

    # noinspection PyBroadException
    @staticmethod
    def extract_images(dicom_path, nodule, diagnosis, output_path):
        try:
            DicomLoader._log.debug('Loading dicom file {}'.format(dicom_path))
            ds = dicom.read_file(dicom_path)
            patient = ds['0010', '0020'].value
            if patient not in diagnosis:
                DicomLoader._log.warn('Diagnosis not found for patient {}'.format(patient))
                nodule.get_annotations()['malignancy'] = DicomLoader._DiagnosisUnknown
            else:
                nodule.get_annotations()['malignancy'] = diagnosis[patient]
            image = Image.fromarray(ds.pixel_array.astype('int16')).convert('I;16')
            cropped = Image.fromarray(DicomLoader._crop_by_nodule(image, nodule), 'I;16')
            if cropped.height is not 0 and cropped.width is not 0:
                cropped_path = os.path.join(output_path, 'nodules')
                full_path = os.path.join(output_path, 'full')
                cropped.convert('RGB').save(os.path.join(cropped_path,
                                                         DicomLoader._get_nodule_image_file_name(nodule)))
                image.convert('RGB').save(os.path.join(full_path,
                                                       DicomLoader._get_original_image_file_name(nodule)))
                return True
            else:
                DicomLoader._log.debug('Too small contour for nodule {}!'.format(nodule))
                return False
        except Exception:
            DicomLoader._log.error('Can\'t extract image of nodule {} from dicom file {} due an error'
                                   .format(nodule, dicom_path), exc_info=True)
            return False

    @staticmethod
    def _crop_by_nodule(image, nodule):
        image = numpy.array(image)
        xc = numpy.array([point.x() for point in nodule.get_points()])
        yc = numpy.array([point.y() for point in nodule.get_points()])
        xy_crop = numpy.vstack((xc, yc)).T
        nr, nc = image.shape
        y_grid, x_grid = numpy.mgrid[:nr, :nc]
        xy_pix = numpy.vstack((x_grid.ravel(), y_grid.ravel())).T
        pth = Path(xy_crop, closed=False)
        mask = pth.contains_points(xy_pix)
        mask = mask.reshape(image.shape)
        masked = numpy.ma.masked_array(image, ~mask)
        x_min, x_max = int(xc.min()), int(numpy.ceil(xc.max()))
        y_min, y_max = int(yc.min()), int(numpy.ceil(yc.max()))
        return masked[y_min:y_max, x_min:x_max].filled(fill_value=0)

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
        malignancy = nodule.get_annotations()['malignancy']
        return study + '_' + series + '_' + image_uid + '_' + nodule_uid + '_' + malignancy + '.bmp'

    @staticmethod
    def _check_initialized(value, error_smg):
        if not value:
            raise ValueError('{} must be present in dicom file!'.format(error_smg))
