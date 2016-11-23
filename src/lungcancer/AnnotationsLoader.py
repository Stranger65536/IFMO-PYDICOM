import logging
import os
import re
import sys
import xml.etree.ElementTree as ElementTree
from logging.handlers import RotatingFileHandler

from lungcancer.Nodule import Nodule
from lungcancer.Point import Point


class AnnotationsLoader:
    _XmlExtension = '.xml'
    _ResponseHeader = 'ResponseHeader'.lower()
    _SeriesInstanceUid = 'SeriesInstanceUid'.lower()
    _StudyInstanceUID = 'StudyInstanceUID'.lower()
    _readingSession = 'readingSession'.lower()
    _unblindedReadNodule = 'unblindedReadNodule'.lower()
    _noduleID = 'noduleID'.lower()
    _characteristics = 'characteristics'.lower()
    _roi = 'roi'.lower()
    _imageSOP_UID = 'imageSOP_UID'.lower()
    _imageZposition = 'imageZposition'.lower()
    _inclusion = 'inclusion'.lower()
    _edgeMap = 'edgeMap'.lower()
    _xCoord = 'xCoord'.lower()
    _yCoord = 'yCoord'.lower()

    @staticmethod
    def _configure_logger():
        logger = logging.getLogger('AnnotationsLoader')
        logger.setLevel(logging.DEBUG)
        fh = RotatingFileHandler('AnnotationsLoader.log', mode='a', maxBytes=2 * 1024 * 1024,
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

    # noinspection PyUnresolvedReferences
    _log = _configure_logger.__func__()

    def __init__(self, annotations_path):
        self._log.info('Annotations directory: {}'.format(annotations_path))
        self._annotations_path = annotations_path

    def load_nodules_annotations(self):
        all_nodules = set()
        for dir_name, sub_dirs, file_list in os.walk(self._annotations_path):
            for file in file_list:
                if self._XmlExtension in file.lower():
                    file_path = os.path.join(dir_name, file)
                    self._process_annotation_file(all_nodules, file_path)
        self._log.info('{} nodule annotations loaded totally'.format(len(all_nodules)))
        return all_nodules

    # noinspection PyBroadException
    def _process_annotation_file(self, all_nodules, file_path):
        try:
            self._log.debug('Found annotation file {}, loading'.format(file_path))
            root = self._parse_xml(file_path)

            series = ''
            study = ''
            xml_nodules = []

            for elem in root:
                tag = elem.tag.lower()
                if tag == self._ResponseHeader:
                    series, study = self._handle_response_header_tag(elem, series, study)
                if tag == self._readingSession:
                    self._handle_reading_session_tag(elem, xml_nodules)

            self._check_mandatory_root_tag_values(series, study)
            self._fill_nodules_with_response_header_info(series, study, xml_nodules)
            self._log.debug('{} nodule annotations loaded from file'.format(len(xml_nodules)))
            all_nodules.update(xml_nodules)
        except Exception:
            type, value, traceback = sys.exc_info()
            self._log.error('Can\'t load xml file: {} due an error: {}'.format(file_path, value), exc_info=True)

    @staticmethod
    def _fill_nodules_with_response_header_info(series, study, xml_nodules):
        for nodule in xml_nodules:
            nodule.set_study(study)
            nodule.set_series(series)

    def _handle_reading_session_tag(self, elem, xml_nodules):
        for node in elem:
            tag = node.tag.lower()
            if tag == self._unblindedReadNodule:
                self._handle_unblinded_read_nodule_tag(node, xml_nodules)

    def _handle_response_header_tag(self, elem, series, study):
        for node in elem:
            tag = node.tag.lower()
            if tag == self._SeriesInstanceUid:
                series = node.text
            if tag == self._StudyInstanceUID:
                study = node.text
        return series, study

    def _check_mandatory_root_tag_values(self, series, study):
        self._check_initialized(study, self._StudyInstanceUID)
        self._check_initialized(series, self._SeriesInstanceUid)

    def _handle_unblinded_read_nodule_tag(self, node, xml_nodules):
        annotations = {}
        nodule_id = ''
        nodules = []

        for info in node:
            tag = info.tag.lower()
            if tag == self._noduleID:
                nodule_id = self._handle_nodule_id_tag(info)
            if tag == self._characteristics:
                self._handle_characteristics_tag(annotations, info)
            if tag == self._roi:
                self._handle_roi_tag(info, nodules)

        self._check_mandatory_unblinded_read_nodule_values(nodule_id)
        if not annotations or not annotations['malignancy']:
            self._log.debug('Missing or empty {} attribute for {} nodule(s)'.format(self._characteristics, len(nodules)))
        self._fill_nodules_with_unblinded_read_nodule_tag(annotations, nodule_id, nodules)
        xml_nodules.extend(nodules)

    def _check_mandatory_unblinded_read_nodule_values(self, nodule_id):
        self._check_initialized(nodule_id, self._noduleID)

    @staticmethod
    def _fill_nodules_with_unblinded_read_nodule_tag(annotations, nodule_id, nodules):
        for nodule in nodules:
            nodule.set_nodule_id(nodule_id)
            nodule.get_annotations().update(annotations)

    @staticmethod
    def _handle_nodule_id_tag(info):
        return info.text[7:] \
            if info.text.startswith('Nodule ') \
            else info.text

    @staticmethod
    def _handle_characteristics_tag(annotations, info):
        for annotation in info:
            annotations[annotation.tag.lower()] = annotation.text

    def _handle_roi_tag(self, info, nodules):
        image_uid = ''
        image_z_position = ''
        image_z_position_init = False
        inclusion = False
        inclusion_init = False
        points = []

        for attribute in info:
            tag = attribute.tag.lower()
            if tag == self._imageSOP_UID:
                image_uid = self._handle_image_uid_tag(attribute)
            if tag == self._imageZposition:
                image_z_position, image_z_position_init = self._handle_z_position_tag(attribute)
            if tag == self._inclusion:
                inclusion, inclusion_init = self._handle_inclusion_tag(attribute)
            if tag == self._edgeMap:
                self._handle_edge_map_tag(attribute, points)

        self._check_mandatory_roi_values(image_uid, image_z_position_init, inclusion_init)
        nodule = self._create_nodule_with_roi_info(image_uid, image_z_position, inclusion, points)
        nodules.append(nodule)

    def _check_mandatory_roi_values(self, image_uid, image_z_position_init, inclusion_init):
        self._check_initialized(image_uid, self._imageSOP_UID)
        self._check_initialized(image_z_position_init, self._imageZposition)
        self._check_initialized(inclusion_init, self._inclusion)

    @staticmethod
    def _create_nodule_with_roi_info(image_uid, image_z_position, inclusion, points):
        nodule = Nodule() \
            .set_image_uid(image_uid) \
            .set_image_z_position(image_z_position) \
            .set_inclusion(inclusion)
        nodule.get_points().extend(points)
        return nodule

    def _handle_edge_map_tag(self, attribute, points):
        point = self._parse_point(attribute)
        points.append(point)

    @staticmethod
    def _handle_inclusion_tag(attribute):
        inclusion = attribute.text.lower() == 'true'
        return inclusion, True

    @staticmethod
    def _handle_z_position_tag(attribute):
        image_z_position = float(attribute.text)
        return image_z_position, True

    @staticmethod
    def _handle_image_uid_tag(attribute):
        return attribute.text

    def _parse_point(self, attribute):
        x = y = 0
        x_init = y_init = False
        for coord in attribute:
            tag = coord.tag.lower()
            if tag == self._xCoord:
                x = int(coord.text)
                x_init = True
            if tag == self._yCoord:
                y = int(coord.text)
                y_init = True
        self._check_initialized(x_init, self._StudyInstanceUID)
        self._check_initialized(y_init, self._StudyInstanceUID)
        return Point(x, y)

    @staticmethod
    def _parse_xml(file_path):
        with open(file_path, 'r') as xml:
            xmlstring = xml.read().replace('\n', '')
        xmlstring = re.sub('(xmlns|xmlns:xsi|xsi:schemaLocation)="[^"]+"', '', xmlstring)
        root = ElementTree.fromstring(xmlstring)
        return root

    @staticmethod
    def _check_initialized(value, error_smg):
        if not value:
            raise ValueError('{} must be present in xml!'.format(error_smg))
