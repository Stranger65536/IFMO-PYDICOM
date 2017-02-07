# coding=utf-8
import logging
from argparse import ArgumentParser
from importlib import reload

from extract import ImageExtractor

reload(logging)


def main():
    parser = ArgumentParser(
        description='Extracts nodules images from DICOM files '
                    'and names them according to the diagnosis')
    parser.add_argument('-D', '--dicom',
                        dest='dicom',
                        metavar='DICOM_FOLDER',
                        required=True,
                        help='all *.dcm files from the specified '
                             'directory will be treated as dicom files '
                             'and parsed for nodule images extraction '
                             'according to the loaded annotations')
    parser.add_argument('-a', '--annotations',
                        dest='annotations',
                        metavar='ANNOTATIONS_FOLDER',
                        required=True,
                        help='all *.xml files from the specified '
                             'directory will be treated as annotations')
    parser.add_argument('-d', '--diagnosis',
                        dest='diagnosis',
                        metavar='DIAGNOSIS_DIRECTORY',
                        required=True,
                        help='All *.csv files from the specified '
                             'directory will be treated as patients '
                             'diagnosis and will override '
                             'corresponding malignancy characteristic '
                             'from annotations')
    parser.add_argument('-o', '--output_directory',
                        dest='output_directory',
                        metavar='OUTPUT_DIRECTORY',
                        required=True,
                        help='All nodule images will be stored in the '
                             'specified directory. Directory will be '
                             'created if necessary')
    parser.add_argument('-A', '--all',
                        dest='export_all_images',
                        default=False,
                        required=False,
                        action='store_true',
                        help='If set, images of all slices, including '
                             'slices without defined diagnosis and '
                             'with unknown diagnosis will be exported')
    parser.add_argument('-f', '--full',
                        dest='export_full_images',
                        default=False,
                        required=False,
                        action='store_true',
                        help='If set, full CT scans will be '
                             'extracted in a "full" subdirectory')
    args = parser.parse_args()
    ImageExtractor.extract_images(args.dicom,
                                  args.annotations,
                                  args.diagnosis,
                                  args.output_directory,
                                  args.export_all_images,
                                  args.export_full_images)


if __name__ == '__main__':
    main()
