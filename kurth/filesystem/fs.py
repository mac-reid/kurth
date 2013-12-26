#!/usr/bin/env python

import re, sys, zlib, itertools, cPickle

class FS_Walker:
    'fs = filesystem'

    filesystem = {}
    current_path = '/'

    def __init__(self, path):
        self.__open_fs_pickle(path)

    def convert_hardlinks(self, path):
        pass

    def cd(self, args):
        new_path = args[0]
        if '..' in new_path:
            new_path = self.convert_hardlinks(new_path)
        concat_path = self.current_path + new_path
        if concat_path in self.filesystem:
            self.current_path = concat_path
        elif new_path in self.filesystem:
            self.current_path = new_path
        else:
            return 'bash: cd: %s: No such file or directory' % new_path

    def ls(self, args=None):
        data = self.filesystem.get(self.current_path, {'files': [],'dirs': []})
        if not args:
            data = [x for x in data if not x.startswith('.')]
        return sorted(data['files'] + data['dirs'])

    def __open_fs_pickle(self, pickle):
        try:
            with open(pickle) as infile:
                self.filesystem = cPickle.loads(zlib.decompress(infile.read()))
        except Exception:
            print >> sys.stderr, pickle + ' not found.'

    def popd(self):
        pass

    def pushd(self, args):
        pass

    def pwd(self):
        return self.current_path

    def read(self, somefile):
        pass
