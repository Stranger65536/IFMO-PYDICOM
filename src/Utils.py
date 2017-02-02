# coding=utf-8
from os import walk
from os.path import join
from pickle import dump
from pickle import load


def list_files(directory, ext=''):
    return [f for l
            in [[join(dir_name, f)
                 for f in file_list
                 if f.lower().endswith(ext)]
                for dir_name, _, file_list
                in walk(directory)]
            for f in l]


def create_cache(file, obj, log):
    try:
        with open(file, mode='wb') as f:
            dump(obj, f)
    except IOError:
        log.error('Can\'t create cache at {}'
                  .format(file), exc_info=True)


def load_cache(file):
    with open(file, 'rb') as f:
        return load(f)
