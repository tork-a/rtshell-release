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

rtteardown library.

'''


import optparse
import os
import os.path
import rtctree.path
import rtctree.tree
import rtsprofile.rts_profile
import sys
import traceback

import actions
import option_store
import rtshell


def disconnect_actions(rtsprofile):
    disconnects = []
    for conn in rtsprofile.data_port_connectors:
        source_comp = rtsprofile.find_comp_by_target(conn.source_data_port)
        source_path = '/' + source_comp.path_uri
        source_port = conn.source_data_port.port_name
        prefix = source_comp.instance_name + '.'
        if source_port.startswith(prefix):
            source_port = source_port[len(prefix):]
        dest_comp = rtsprofile.find_comp_by_target(conn.target_data_port)
        dest_path = '/' + dest_comp.path_uri
        dest_port =conn.target_data_port.port_name
        prefix = dest_comp.instance_name + '.'
        if dest_port.startswith(prefix):
            dest_port = dest_port[len(prefix):]
        disconnects.append(actions.DisconnectPortsAct(source_path, source_port,
            dest_path, dest_port, conn.connector_id))

    for conn in rtsprofile.service_port_connectors:
        source_comp = rtsprofile.find_comp_by_target(conn.source_service_port)
        source_path = '/' + source_comp.path_uri
        source_port = conn.source_service_port.port_name
        prefix = source_comp.instance_name + '.'
        if source_port.startswith(prefix):
            source_port = source_port[len(prefix):]
        dest_comp = rtsprofile.find_comp_by_target(conn.target_service_port)
        dest_path = '/' + dest_comp.path_uri
        dest_port = conn.target_service_port.port_name
        prefix = dest_comp.instance_name + '.'
        if dest_port.startswith(prefix):
            dest_port = dest_port[len(prefix):]
        disconnects.append(actions.DisconnectPortsAct(source_path, source_port,
            dest_path, dest_port, conn.connector_id))
    return disconnects


def teardown(profile=None, xml=True, dry_run=False, tree=None):
    # Load the profile
    if profile:
        # Read from a file
        with open(profile) as f:
            if xml:
                rtsp = rtsprofile.rts_profile.RtsProfile(xml_spec=f)
            else:
                rtsp = rtsprofile.rts_profile.RtsProfile(yaml_spec=f)
    else:
        # Read from standard input
        lines = sys.stdin.read()
        if xml:
            rtsp = rtsprofile.rts_profile.RtsProfile(xml_spec=lines)
        else:
            rtsp = rtsprofile.rts_profile.RtsProfile(yaml_spec=lines)

    # Build a list of actions to perform that will destroy the system
    actions = disconnect_actions(rtsp)
    if dry_run:
        for a in actions:
            print a
    else:
        if not tree:
            # Load the RTC Tree, using the paths from the profile
            tree = rtctree.tree.RTCTree(paths=[rtctree.path.parse_path(
                '/' + c.path_uri)[0] for c in rtsp.components])
        for a in actions:
            a(tree)


def main(argv=None, tree=None):
    usage = '''Usage: %prog [options] [RTSProfile file]
Destroy an RT system using an RTSProfile.'''
    parser = optparse.OptionParser(usage=usage, version=rtshell.RTSH_VERSION)
    parser.add_option('--dry-run', dest='dry_run', action='store_true',
            default=False,
            help="Print what will be done but don't actually do anything. \
[Default: %default]")
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
            default=False, help='Verbose output. [Default: %default]')
    parser.add_option('-x', '--xml', dest='xml', action='store_true',
            default=True, help='Use XML input format. [Default: True]')
    parser.add_option('-y', '--yaml', dest='xml', action='store_false',
            help='Use YAML input format. [Default: False]')

    if argv:
        sys.argv = [sys.argv[0]] + argv
    try:
        options, args = parser.parse_args()
    except optparse.OptionError, e:
        print >>sys.stderr, 'OptionError: ', e
        return 1
    option_store.OptionStore().verbose = options.verbose


    if not args:
        profile = None
    elif len(args) == 1:
        profile = args[0]
    else:
        print >>sys.stderr, usage
        return 1

    try:
        teardown(profile=profile, xml=options.xml, dry_run=options.dry_run,
                tree=tree)
    except Exception, e:
        if options.verbose:
            traceback.print_exc()
        print >>sys.stderr, '{0}: {1}'.format(os.path.basename(sys.argv[0]), e)
        return 1
    return 0


# vim: tw=79

