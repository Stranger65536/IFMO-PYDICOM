import getopt
import importlib
import logging
import sys

from lungcancer.extract.AnnotationsLoader import AnnotationsLoader
from lungcancer.extract.DicomLoader import DicomLoader
from lungcancer.extract.ImageExtractor import ImageExtractor
from lungcancer.extract.PatientDiagnosisLoader import PatientDiagnosisLoader

importlib.reload(logging)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    opts, args = getopt.getopt(argv[1:], [])
    if len(args) < 3:
        print('Usage: __init__.py <annotations directory> '
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
        ImageExtractor.extract(args[0], args[1], args[2], args[3])
        return 0


if __name__ == '__main__':
    sys.exit(main())
