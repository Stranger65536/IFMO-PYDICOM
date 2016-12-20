import getopt
import importlib
import logging
import sys

from lungcancer.prepare.ImageScaler import ImageScaler

importlib.reload(logging)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    opts, args = getopt.getopt(argv[1:], [])
    if len(args) < 2:
        print('Usage: __init__.py <images directory> <size in px>')
        return 1
    else:
        ImageScaler(args[0]).scale_images(int(args[1]))
        return 0


if __name__ == '__main__':
    sys.exit(main())
