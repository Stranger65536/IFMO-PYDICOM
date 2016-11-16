import os

import dicom
import numpy
from matplotlib import pyplot

path_dicom = "D:\Lung Cancer data\LIDC_FILTERED\LIDC-IDRI-0068"

for dir_name, sub_dirs, file_list in os.walk(path_dicom):
    for file in file_list:
        if ".dcm" in file.lower():  # check whether the file's DICOM
            file_path = os.path.join(dir_name, file)
            dic = dicom.read_file(file_path)
            dimensions = (int(dic.Rows), int(dic.Columns))
            x = numpy.arange(0.0, (dimensions[0] + 1) * dimensions[0], dimensions[0])
            y = numpy.arange(0.0, (dimensions[1] + 1) * dimensions[1], dimensions[1])
            pixel_spacing = (float(dic.PixelSpacing[0]),
                             float(dic.PixelSpacing[1]),
                             float(dic.SliceThickness))
            image = numpy.zeros(dimensions, dtype=dic.pixel_array.dtype)
            image = dic.pixel_array
            pyplot.figure(dpi=600)
            pyplot.axes().set_aspect('equal', 'datalim')
            pyplot.set_cmap(pyplot.gray())
            pyplot.pcolormesh(x, y, numpy.flipud(image[:, :]))
