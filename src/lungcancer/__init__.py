import getopt
import sys

from lungcancer.AnnotationsLoader import AnnotationsLoader
from lungcancer.DicomLoader import DicomLoader
from lungcancer.PatientDiagnosisLoader import PatientDiagnosisLoader


def main(argv=None):
    if argv is None:
        argv = sys.argv
    opts, args = getopt.getopt(argv[1:], [])
    if len(args) < 3:
        print('Usage: __init__.py <annotations directory> <diagnosis directory> <dicom_directory>\n'
              'annotations directory - all *.xml files from the specified directory will be treated as annotations\n'
              'diagnosis directory - all *.csv files from the specified directory will be treated as patients '
              'diagnosis and will override corresponding malignancy characteristic from annotations\n'
              'dicom_directory - all *.dcm files from the specified directory will be treated as dicom files and '
              'parsed for nodule images extraction according to the loaded annotations')
        return 1
    else:
        nodules = read_annotations(args[0])
        diagnosis = read_diagnosis(args[1])
        metadata = read_dicoms_metadata(args[2])
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
