#!/usr/bin/env python
# -*- Python -*-
# -*- coding: utf-8 -*-

'''rtshell

Copyright (C) 2009-2014
    Geoffrey Biggs
    RT-Synthesis Research Group
    Intelligent Systems Research Institute,
    National Institute of Advanced Industrial Science and Technology (AIST),
    Japan
    All rights reserved.
Licensed under the Eclipse Public License -v 1.0 (EPL)
http://www.opensource.org/licenses/eclipse-1.0.txt

Implementation of the command to make a component exit.

'''


import optparse
import os
import os.path
import rtctree.exceptions
import rtctree.tree
import rtctree.path
import RTC
import sys
import traceback

import path
import rts_exceptions
import rtshell


def log_cb(rtc, time, source, level, msg):
    print '[{0} {1}] {2} <{3}> {4}'.format(rtc, time, level, source, msg)


def print_logs(paths, options, tree=None):
    for p in paths:
        path, port = rtctree.path.parse_path(p[1])
        if port:
            raise rts_exceptions.NotAComponentError(p[0])
        if not path[-1]:
            raise rts_exceptions.NotAComponentError(p[0])
        p.append(path)

    if not tree:
        parsed = [p[2] for p in paths]
        tree = rtctree.tree.RTCTree(paths=parsed, filter=parsed)

    filters = ','.join(options.filters)
    ids = []
    try:
        for p in paths:
            if not tree.has_path(p[2]):
                raise rts_exceptions.NoSuchObjectError(p[0])
            rtc = tree.get_node(p[2])
            if rtc.is_zombie:
                raise rts_exceptions.ZombieObjectError(p[0])
            if not rtc.is_component:
                raise rts_exceptions.NotAComponentError(p[0])

            id = rtc.add_logger(log_cb, level=options.level,
                    filters=filters)
            ids.append((rtc, id))
    except rtctree.exceptions.AddLoggerError, e:
        # Remove all the loggers that were added
        for i in ids:
            i[0].remove_logger(i[1])
        # Re-raise
        raise e

    # Wait for a keyboard interrupt
    try:
        while True:
            raw_input('')
    except KeyboardInterrupt:
        pass
    # Remove all the loggers that were added
    for i in ids:
        i[0].remove_logger(i[1])


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] <path 1> [path 2...]
View a component logs.'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-f', '--filter', dest='filters', action='append',
            type='string', default='ALL',
            help='Event source filters. [Default: %default]')
    parser.add_option('-l', '--level', dest='level', action='store',
            type='string', default='NORMAL',
            help='Log level. [Default: %default]')
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
            default=False,
            help='Output verbose information. [Default: %default]')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except optparse.OptionError, e:
        print >>sys.stderr, 'OptionError:', e
        return 1

    if not args:
        # If no paths given then can't do anything.
        print >>sys.stderr, '{0}: No component specified.'.format(
                os.path.basename(sys.argv[0]))
        return 1
    paths = [[p, path.cmd_path_to_full_path(p)] for p in args]

    try:
        print_logs(paths, options, tree)
    except Exception, e:
        if options.verbose:
            traceback.print_exc()
        print >>sys.stderr, '{0}: {1}'.format(os.path.basename(sys.argv[0]), e)
        return 1
    return 0


# vim: tw=79

