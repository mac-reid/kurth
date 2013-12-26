#!/usr/bin/env python

import os, zlib, cPickle


def walk_dir(path):
    subdir = {}
    for dirpath, subdirs, files in os.walk(path):
        subdir[dirpath] = {'dirs': subdirs, 'files': files}
    return subdir

def do_stuff():
    filesystem = {}
    filesystem['/'] = {'dirs': ['bin', 'usr', 'tmp', 'boot', 'sbin', 'lib',
                                'lib64', 'etc'],
                       'files': ['initrd.img', 'vmlinuz']}

    dirs = ['/bin', '/usr', '/tmp', '/boot', '/sbin', '/lib', '/lib64', '/etc']
    for path in dirs:
        filesystem.update(walk_dir(path))
    print len(filesystem)
    with open('fs.gz', 'w') as out:
        out.write(zlib.compress(cPickle.dumps(filesystem)))
        # cPickle.dump(filesystem, out)
    stuff = raw_input('type: ')
