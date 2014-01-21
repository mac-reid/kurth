#!/usr/bin/env python

import re, sys, zlib, itertools, cPickle

class FS_Walker:
    'fs = filesystem'

    filesystem = {}

    def __init__(self, path):
        self.__open_fs_pickle(path)

    def check_dir_in_filesystem(self, directory):
        return directory in self.filesystem

    def get_contents_of_dir(self, directory):
        return self.filesystem.get(directory, {'files': [],'dirs': []})

    def __open_fs_pickle(self, pickle):
        try:
            with open(pickle) as infile:
                self.filesystem = cPickle.loads(zlib.decompress(infile.read()))
        except IOError:
            print >> sys.stderr, 'Fatal: ' + pickle + ' not found.'
            sys.exit(1)

    def read(self, filename):
        pass
