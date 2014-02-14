#!/usr/bin/env python

import sys
import zlib
import cPickle


class fs:
    filesystem = {}

    def __init__(self):
        # hard coded for now
        path = 'filesystem/fs.gz'
        self.__open_fs_pickle(path)

    def check_dir_in_filesystem(self, directory):
        return directory in self.filesystem

    def get_contents_of_dir(self, directory):
        return self.filesystem.get(directory, {'files': [], 'dirs': []})

    def __open_fs_pickle(self, pickle):
        try:
            with open(pickle) as infile:
                self.filesystem = cPickle.loads(zlib.decompress(infile.read()))
        except IOError:
            print >> sys.stderr, 'Fatal: ' + pickle + ' not found.'
            sys.exit(1)

    def read(self, filename):
        pass
