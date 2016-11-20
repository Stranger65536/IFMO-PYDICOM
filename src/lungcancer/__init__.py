import getopt
import sys

from lungcancer.AnnotationsLoader import AnnotationsLoader
from lungcancer.DicomLoader import DicomLoader


def main(argv=None):
    if argv is None:
        argv = sys.argv
    opts, args = getopt.getopt(argv[1:], [])
    if len(args) < 2:
        print('Usage: __init__.py <dicom_directory> <annotations directory>')
        return 1
    else:
        annotations_loader = AnnotationsLoader(args[1])
        nodules = annotations_loader.load_nodules_annotations()
        return 0


if __name__ == '__main__':
    sys.exit(main())
