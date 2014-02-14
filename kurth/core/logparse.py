#!/usr/bin/env python

import re
import sys


def _add_to_dict(dictionary, data):
    splitdata = data[2].split(',')
    if len(splitdata) == 1:
        key = splitdata[0]
    else:
        index = len(splitdata) - 1
        key = splitdata[index]

    if key in dictionary:
        dictionary[key].append(data[:])
    else:
        dictionary[key] = list(data[:])


def parse_file(path):
    data = {}
    try:
        with open(path, 'r') as infile:
            regex = re.compile("([0-9|-]+) ([0-9|,-:]+) \[(.*)\] (.*$)")
            for line in infile:
                results = regex.search(line)
                _add_to_dict(data, results.groups())
    except IOError:
        print >> sys.stdout, 'File %s not found.' % path
    return data
