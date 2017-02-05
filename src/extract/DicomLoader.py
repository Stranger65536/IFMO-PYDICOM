# coding=utf-8
from os import walk
from os.path import isfile
from os.path import join

from PIL import Image
from dicom import read_file
from matplotlib.path import Path
from numpy import array
from numpy import ceil
from numpy import mgrid
from numpy import vstack
from numpy.ma import masked_array

from LoggerUtils import LoggerUtils
from Utils import create_cache
from Utils import load_cache

dic_ext = '.dcm'
diagnosis_unknown = '0'
log = LoggerUtils.get_logger('DicomLoader')
cache_file_name = 'dicom.cache'

unclassified_patients = set()


def extract_image(dicom_path,
                  nodule,
                  nodule_slice,
                  diagnosis,
                  output_path):
    try:
        log.debug('Loading dicom file {}'.format(dicom_path))
        ds = read_file(dicom_path)
        patient = ds['0010', '0020'].value

        if patient not in diagnosis:
            if patient not in unclassified_patients:
                unclassified_patients.add(patient)
                log.warn('Diagnosis not found for patient {}'
                         .format(patient))
            nodule.malignancy = diagnosis_unknown
        else:
            nodule.malignancy = diagnosis[patient]

        image = Image \
            .fromarray(ds.pixel_array.astype('int16')) \
            .convert('I;16')
        cropped = Image.fromarray(contour(image, nodule_slice), 'I;16')

        if cropped.height is not 0 and cropped.width is not 0:
            full_path = join(output_path, 'full')
            full_file = original_file_name(full_path,
                                           nodule,
                                           nodule_slice)
            image.convert('L').save(full_file)
            cropped_path = join(output_path, 'nodules')
            slice_file = slice_image_name(cropped_path,
                                          nodule,
                                          nodule_slice)
            cropped.convert('L').save(slice_file)
            return True
        else:
            log.error('Too small contour for slice {}!'
                      .format(nodule_slice))
            return False
    except ValueError:
        log.error('Can\'t extract slice image {} from file {}'
                  .format(nodule, dicom_path), exc_info=True)
        return False


def contour(image, nodule_slice):
    image = array(image)

    xc = array([point.x for point in nodule_slice.points])
    yc = array([point.y for point in nodule_slice.points])

    xy_crop = vstack((xc, yc)).T

    nr, nc = image.shape
    y_grid, x_grid = mgrid[:nr, :nc]
    xy_pix = vstack((x_grid.ravel(), y_grid.ravel())).T
    pth = Path(xy_crop, closed=True)

    mask = pth.contains_points(xy_pix, radius=-1) \
        .reshape(image.shape)
    masked = masked_array(image, ~mask)

    x_min, x_max = int(xc.min()), int(ceil(xc.max()))
    y_min, y_max = int(yc.min()), int(ceil(yc.max()))

    return masked[y_min:y_max, x_min:x_max].filled(fill_value=0)


def original_file_name(base_dir, nodule, nodule_slice):
    return join(base_dir,
                nodule.study + '_' +
                nodule.series + '_' +
                '{0:+010.2f}'.format(float(nodule_slice.z_pos)) + '_' +
                nodule.nodule_id + '_' +
                nodule_slice.image_uid + '_full.png')


def slice_image_name(base_dir, nodule, nodule_slice):
    return join(base_dir,
                nodule.study + '_' +
                nodule.series + '_' +
                nodule.nodule_id + '_' +
                '{0:+010.2f}'.format(float(nodule_slice.z_pos)) + '_' +
                nodule_slice.image_uid + '_' +
                nodule.malignancy + '.png')


def parse_dicom_file(file_path, study_data):
    ds = read_file(file_path,
                   stop_before_pixels=True)
    image_uid = ds["0008", "0018"].value
    check_initialized(image_uid, 'image_uid')
    study = ds["0020", "000d"].value
    check_initialized(study, 'study_id')
    series = ds["0020", "000e"].value
    check_initialized(series, 'series_id')
    series_data = study_data.get(study, {})
    image_data = series_data.get(series, {})

    if image_uid in image_data:
        log.warn('Found duplicate image_uid in files: {}; {}'
                 .format(image_data[image_uid], file_path))

    image_data[image_uid] = file_path
    series_data[series] = image_data
    study_data[study] = series_data


def check_initialized(value, attribute):
    if not value:
        raise ValueError(
            '{} must be present in dicom file!'.format(attribute))


class DicomLoader(object):
    def __init__(self, dicom_path):
        log.info('Dicoms directory: {}'.format(dicom_path))
        self._dicom_path = dicom_path

    def load_dicoms_metadata(self):
        cache_file = join(self._dicom_path, cache_file_name)

        if isfile(cache_file):
            log.info('Found cache file with dicom metadata, '
                     'delete it to reload: {}. Loading...'
                     .format(cache_file))
            return load_cache(cache_file)

        study_data = {}
        error_files = []
        file_counter = 1

        for dir_name, sub_dirs, file_list in walk(self._dicom_path):
            for file in file_list:
                if file.lower().endswith(dic_ext):
                    file_path = join(dir_name, file)

                    try:
                        log.debug('Found dicom file #{} {}, loading'
                                  .format(file_counter, file_path))
                        parse_dicom_file(file_path, study_data)
                    except ValueError:
                        error_files.append(file)
                        log.error('Can\'t load dicom file {} '
                                  .format(file_path), exc_info=True)
                    finally:
                        file_counter += 1

        log.info('These {} files has not been loaded: \n{}'
                 .format(len(error_files), '\n'.join(error_files)))
        log.info('{} images found totally'
                 .format(sum([len(f) for l in study_data.values()
                              for f in l.values()])))

        log.info('Creating dicom metadata cache: {}'
                 .format(cache_file))
        create_cache(cache_file, study_data, log)

        return study_data
