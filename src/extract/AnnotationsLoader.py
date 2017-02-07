# coding=utf-8
from collections import namedtuple
from os.path import isfile
from os.path import join
from re import compile
from xml.sax import parseString
from xml.sax.handler import ContentHandler

from LoggerUtils import LoggerUtils
from Utils import create_cache
from Utils import list_files
from Utils import load_cache
from extract.Nodule import Nodule
from extract.Slice import Slice

log = LoggerUtils.get_logger('AnnotationsLoader')
non_id_char = compile('[^_0-9a-zA-Z]')
xml_ext = '.xml'
cache_file_name = 'annotations.cache'


def _name_mangle(name):
    return non_id_char.sub('_', name)


Point = namedtuple('Point', 'x y')


class CaseInsensitiveDict(dict):
    def __setitem__(self, key, value):
        super(CaseInsensitiveDict, self) \
            .__setitem__(str(key).lower(), value)

    def __getitem__(self, key):
        return super(CaseInsensitiveDict, self) \
            .__getitem__(str(key).lower())

    def __contains__(self, key):
        return super(CaseInsensitiveDict, self) \
            .__contains__(str(key).lower())


class DataNode(object):
    def __init__(self):
        self._attributes = CaseInsensitiveDict()
        self._data = None

    @property
    def attributes(self):
        return self._attributes

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    def __len__(self):
        return 1

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.attributes[key]
        else:
            return [self][key]

    def __contains__(self, name):
        return name in self.attributes

    def __nonzero__(self):
        return bool(self.attributes or self.data)

    def __getattr__(self, name):
        if name.startswith('__'):
            # need to do this for Python special methods???
            raise AttributeError(name)
        return self.attributes[name]

    def add_xml_attribute(self, name, value):
        if name in self.attributes:
            # multiple attribute of the same name
            # are represented by a list
            children = self.attributes[name]
            if not isinstance(children, list):
                children = [children]
                self.attributes[name] = children
            children.append(value)
        else:
            self.attributes[name] = value

    def __str__(self):
        return self.data or self.__repr__()

    def __repr__(self):
        items = sorted(self.attributes.items())
        if self.data:
            items.append(('data', self.data))
        return u'{%s}' % ', '.join(
            [u'%s:%s' % (k, repr(v)) for k, v in items])


class TreeBuilder(ContentHandler):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.root = DataNode()
        self.current = self.root
        self.text_parts = []

    def startElement(self, name, attributes):
        self.stack.append((self.current, self.text_parts))
        self.current = DataNode()
        self.text_parts = []
        # xml attributes --> python attributes
        for k, v in attributes.items():
            self.current.add_xml_attribute(_name_mangle(k), v)

    def endElement(self, name):
        text = ''.join(self.text_parts).strip()
        if text:
            self.current.data = text
        if self.current.attributes:
            obj = self.current
        else:
            # a text only node is simply represented by the string
            obj = text or ''
        self.current, self.text_parts = self.stack.pop()
        self.current.add_xml_attribute(_name_mangle(name), obj)

    def characters(self, content):
        self.text_parts.append(content)


def get_field(node, field):
    if field not in node.attributes:
        raise ValueError('{} is not presented at node {}'
                         .format(field, node))
    else:
        return node.attributes[field]


def parse_nodules(xml_text, nodules):
    builder = TreeBuilder()
    parseString(xml_text.encode('utf-8'), builder)
    root = next(iter(builder.root.attributes.values()))
    response_header = get_field(node=root,
                                field='ResponseHeader')
    series = get_field(node=response_header,
                       field='SeriesInstanceUid')
    study = get_field(node=response_header,
                      field='StudyInstanceUID')
    r_sessions = list(get_field(node=root,
                                field='ReadingSession'))
    for r_session in r_sessions:
        unbl_r_nodules = list(get_field(node=r_session,
                                        field='UnblindedReadNodule'))
        for unbl_r_nodule in unbl_r_nodules:
            nodule_id = get_field(node=unbl_r_nodule,
                                  field='noduleID')
            if nodule_id.startswith('Nodule '):
                nodule_id = nodule_id[7:].strip()
            if nodule_id.isnumeric():
                nodule_id = str(int(nodule_id))

            rois = list(get_field(node=unbl_r_nodule,
                                  field='roi'))

            if not nodules.get((study, series, nodule_id)):
                nodule = nodules[(study, series, nodule_id)] = \
                    Nodule(study, series, nodule_id)
            else:
                nodule = nodules[(study, series, nodule_id)]

            for roi in rois:
                image_uid = get_field(node=roi,
                                      field='imageSOP_UID')
                z_pos = get_field(node=roi,
                                  field='imageZposition')
                inclusion = get_field(node=roi,
                                      field='inclusion')

                if 'true' != inclusion.lower():
                    # to work only with included slices
                    continue

                edge_maps = list(get_field(node=roi,
                                           field='edgeMap'))
                points = []
                for edge in edge_maps:
                    x = int(get_field(node=edge,
                                      field='xCoord'))
                    y = int(get_field(node=edge,
                                      field='yCoord'))
                    points.append(Point(x, y))

                nodule.slices.add(Slice(image_uid=image_uid,
                                        z_pos=z_pos,
                                        points=points))
    return nodules


class AnnotationsLoader(object):
    def __init__(self, annotations_path):
        log.info('Annotations directory: {}'.format(annotations_path))
        self._annotations_path = annotations_path

    def load_nodules_annotations(self):
        cache_file = join(self._annotations_path, cache_file_name)

        if isfile(cache_file):
            log.info('Found cache file with annotations, '
                     'delete it to reload: {}. Loading...'
                     .format(cache_file))
            return load_cache(cache_file)

        nodules = {}
        files = list_files(self._annotations_path, xml_ext)
        error_files = []
        file_counter = 1

        for file in files:
            try:
                log.info('Parsing file {} of {}: {}'
                         .format(file_counter, len(files), file))
                with open(file) as f:
                    xml_text = f.read()
                    parse_nodules(xml_text, nodules)
                    log.info('File {} has been parsed successfully'
                             .format(file))
            except ValueError:
                error_files.append(file)
                log.error('Can\'t load annotations from file {}'
                          .format(file), exc_info=True)
            finally:
                file_counter += 1

        log.info('These {} files has not been loaded: \n{}'
                 .format(len(error_files), '\n'.join(error_files)))
        log.info('{} nodule annotations with {} slices loaded totally'
                 .format(len(nodules),
                         sum([len(n.slices) for n in
                              nodules.values()])))

        log.info('Creating annotations cache: {}'.format(cache_file))
        create_cache(cache_file, list(nodules.values()), log)

        return list(nodules.values())
