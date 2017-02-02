# coding=utf-8
class Nodule(object):
    def __init__(self, study, series, nodule_id):
        self._study = study
        self._series = series
        self._nodule_id = nodule_id
        self._malignancy = None
        self._slices = set()

    @property
    def study(self):
        return self._study

    @property
    def series(self):
        return self._series

    @property
    def nodule_id(self):
        return self._nodule_id

    @property
    def malignancy(self):
        return self._malignancy

    @property
    def slices(self):
        return self._slices

    @malignancy.setter
    def malignancy(self, value):
        self._malignancy = value

    def __eq__(self, other):
        if not isinstance(other, Nodule):
            return False

        return \
            self.study == other.study and \
            self.series == other.series and \
            self.nodule_id == other.nodule_id

    def __hash__(self, *args, **kwargs):
        return hash((self.study,
                     self.series,
                     self.nodule_id))

    def __repr__(self, *args, **kwargs):
        return ''.join(['Slice(',
                        str(self.study), ',',
                        str(self.series), ',',
                        str(self.nodule_id), ',',
                        str(self.malignancy), ',',
                        str(self.slices), ')'])

    def __str__(self, *args, **kwargs):
        return ''.join(['Slice(',
                        str(self.study), ',',
                        str(self.series), ',',
                        str(self.nodule_id), ',',
                        str(self.malignancy), ')'])
