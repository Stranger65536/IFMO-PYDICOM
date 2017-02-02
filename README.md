# Summary

This library allows you to perform machine learning on lung cancer nodules images extracted from LIDC DICOM files or predefined Keras datasets

# Hardware requirements

* At least 1GB free RAM to  

# Software requirements

* Python 3.1+ (Tested on Anaconda 4 with Python 3.4.5 x64)

# Prerequirements

1. Go to https://wiki.cancerimagingarchive.net/display/Public/LIDC-IDRI
2. Download DICOM images (DICOM, 124GB) and place them into `DICOM directory`
3. Download Radiologist Annotations/Segmentations (XML) and place them into `Annotations directory`
4. Download Patient Diagnoses (XLS) and copy its main data into csv file `Diagnosis file` with row format like: `LIDC-IDRI-0068,3`

# Running

## Image extraction

Skip this step if you want to use any of default Keras datasets instead of custom images

```bash

usage: extract.py [-h] -D DICOM_FOLDER -a ANNOTATIONS_FOLDER -d
                  DIAGNOSIS_DIRECTORY -o OUTPUT_DIRECTORY

Extracts nodules images from DICOM files and names them according to the
diagnosis

optional arguments:
  -h, --help            show this help message and exit
  -D DICOM_FOLDER, --dicom DICOM_FOLDER
                        all *.dcm files from the specified directory will be
                        treated as dicom files and parsed for nodule images
                        extraction according to the loaded annotations
  -a ANNOTATIONS_FOLDER, --annotations ANNOTATIONS_FOLDER
                        all *.xml files from the specified directory will be
                        treated as annotations
  -d DIAGNOSIS_DIRECTORY, --diagnosis DIAGNOSIS_DIRECTORY
                        All *.csv files from the specified directory will be
                        treated as patients diagnosis and will override
                        corresponding malignancy characteristic from
                        annotations
  -o OUTPUT_DIRECTORY, --output_directory OUTPUT_DIRECTORY
                        All nodule images will be stored in the specified
                        directory. Directory will be created if necessary
```

First run may take a while. During first time extraction caches with annotations, dicoms metadata and diagnosis will be created. It will reduce time for next image extractions. 


```
python src\extract.py -D <DICOM directory> -a <Annotations directory> -d <Diagnosis file directory> -o <target folder for extracted images>
```

