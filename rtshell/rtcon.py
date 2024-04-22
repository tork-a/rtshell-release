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

Implementation of the command to connect two ports.

'''


import optparse
import os
import os.path
import rtctree.exceptions
import rtctree.tree
import rtctree.path
import sys
import traceback

import path
import rts_exceptions
import rtshell


def connect_ports(paths, options, tree=None):
    cmd_paths, fps = zip(*paths)
    pathports = [rtctree.path.parse_path(fp) for fp in fps]
    for ii, p in enumerate(pathports):
        if not p[1]:
            raise rts_exceptions.NotAPortError(cmd_paths[ii])
        if not p[0][-1]:
            raise rts_exceptions.NotAPortError(cmd_paths[ii])
    paths, ports = zip(*pathports)

    if not tree:
        tree = rtctree.tree.RTCTree(paths=paths, filter=paths)

    port_objs = []
    for ii, p in enumerate(pathports):
        obj = tree.get_node(p[0])
        if not obj:
            raise rts_exceptions.NoSuchObjectError(cmd_paths[ii])
        if obj.is_zombie:
            raise rts_exceptions.ZombieObjectError(cmd_paths[ii])
        if not obj.is_component:
            raise rts_exceptions.NotAComponentError(cmd_paths[ii])
        port_obj = obj.get_port_by_name(p[1])
        if not port_obj:
            raise rts_exceptions.PortNotFoundError(p[0], p[1])
        port_objs.append(port_obj)

    conn_name = options.name if options.name else None
    port_objs[0].connect(port_objs[1:], name=conn_name, id=options.id,
            props=options.properties)


def main(argv=None, tree=None):
    def property_callback(option, opt, option_value, parser):
        if option_value.count('=') != 1:
            raise optparse.OptionValueError('Bad property format: {0}'.format(
                option_value))
        key, equals, value = option_value.partition('=')
        if not getattr(parser.values, option.dest):
            setattr(parser.values, option.dest, {})
        if key in getattr(parser.values, option.dest):
            print >>sys.stderr, '{0}: Warning: duplicate property: {1}'.format(
                    sys.argv[0], option_value)
        getattr(parser.values, option.dest)[key] = value

    usage = '''Usage: %prog [options] <path 1> <path 2> [<path 3> ...]
Connect two or more ports.'''
    version = rtshell.RTSH_VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-i', '--id', dest='id', action='store', type='string',
            default='', help='ID of the connection. [Default: %default]')
    parser.add_option('-n', '--name', dest='name', action='store',
            type='string', default=None,
            help='Name of the connection. [Default: %default]')
    parser.add_option('-p', '--property', dest='properties', action='callback',
            callback=property_callback, type='string',
            help='Connection properties.')
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

    if not getattr(options, 'properties'):
        setattr(options, 'properties', {})

    if not args:
        # If no paths given then can't do anything.
        print >>sys.stderr, '{0}: No ports specified.'.format(
                os.path.basename(sys.argv[0]))
        return 1
    paths = [(p, path.cmd_path_to_full_path(p)) for p in args]

    try:
        connect_ports(paths, options, tree=tree)
    except Exception, e:
        if options.verbose:
            traceback.print_exc()
        print >>sys.stderr, '{0}: {1}'.format(os.path.basename(sys.argv[0]), e)
        return 1
    return 0


# vim: tw=79

