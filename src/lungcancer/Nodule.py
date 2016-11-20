class Nodule:
    def __init__(self):
        self._study = ''
        self._series = ''
        self._nodule_id = ''
        self._image_uid = ''
        self._image_z_position = ''
        self._inclusion = False
        self._points = []
        self._annotations = {}

    def set_study(self, study):
        self._study = study
        return self

    def set_series(self, series):
        self._series = series
        return self

    def set_nodule_id(self, nodule_id):
        self._nodule_id = nodule_id
        return self

    def set_image_uid(self, image_uid):
        self._image_uid = image_uid
        return self

    def set_image_z_position(self, image_z_position):
        self._image_z_position = image_z_position
        return self

    def set_inclusion(self, inclusion):
        self._inclusion = inclusion
        return self

    def get_study(self):
        return self._study

    def get_series(self):
        return self._series

    def get_nodule_id(self):
        return self._nodule_id

    def get_image_uid(self):
        return self._image_uid

    def get_image_z_position(self):
        return self._image_z_position

    def get_inclusion(self):
        return self._inclusion

    def get_points(self):
        return self._points

    def get_annotations(self):
        return self._annotations

    def __repr__(self, *args, **kwargs):
        return "".join(["Nodule(", str(self._study), ",",
                        str(self._series), ",",
                        str(self._image_z_position), ",",
                        str(len(self._points)), ")"])
