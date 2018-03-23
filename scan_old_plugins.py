#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# script to scan for duplicate old eclipse features, plugins and dropins by parseing bundles.info.
# generates a "clean_old_plugins" script to clean old versions.
# warning: DANGEROUS! review clean_old_plugins script before running it.

from datetime import datetime
import os
import platform
import shutil
import sys


"""
https://wiki.eclipse.org/Equinox/p2/Getting_Started
The file bundles.info contains a list of all the plug-ins installed in the current system.
On startup, all the plug-ins listed in this file are given to OSGi as the exact set of
plug-ins to run with.
Any extra plug-ins in the plugins directory or elsewhere are ignored.
"""
BUNDLES_INFO = "configuration/org.eclipse.equinox.simpleconfigurator/bundles.info"


def gen_script(src, dest, unused_list):
    system = platform.system()
    if system is 'Windows':
        mv_cmd = 'move /y'
        script_ext = 'cmd'
        script_hdr = '@echo off'
    elif system is 'Linux':
        mv_cmd = 'mv -f'
        script_ext = 'sh'
        script_hdr = '#!/bin/sh'
    else:
        raise NameError('No support platform.')

    desc = '''
:: script to remove duplicate old eclipse features, plugins and dropins by parseing bundles.info.
:: generate by scan_old_plugins.py which written by cmheia
    '''
    paths = set()
    cmd_lines = []
    for f in unused_list:
        r = os.path.split(f)[0]
        paths.add(r)
        s = os.path.abspath(os.path.join(src, f))
        d = os.path.join(dest, r, '')
        cmd_lines.append('{} "{}" "{}"\n'.format(mv_cmd, s, d))
    print('Write {} lines to {}\\clean_old_plugins.cmd'.format(len(unused_list), dest))
    os.makedirs(dest)
    with open(os.path.join(dest, 'clean_old_plugins.{}'.format(script_ext)), 'w') as f:
        f.write(script_hdr + '\n')
        f.write(desc + '\n')
        for p in paths:
            f.write('if not exist "{0}" md "{0}"\n'.format(
                os.path.join(dest, p)))
        for l in cmd_lines:
            f.write(l)


def move_files(src, dest, unused_list):
    print('moving {} to: {}'.format(len(unused_list), dest))
    os.makedirs(dest)
    for f in unused_list:
        dest = os.path.join(dest, os.path.split(f)[0])
        print('move {} to {}'.format(os.path.abspath(
            os.path.join(src, f)), dest))
        shutil.move(os.path.abspath(
            os.path.join(src, f)), dest)


def list_handler(src, dest, unused_list):
    # print(unused_list)
    gen_script(src, dest, unused_list)
    # move_files(src, dest, unused_list)
    print('done')


def find_unused_item(eclipse_dir):
    bundles = set()
    unused_list = []
    with open(os.path.join(eclipse_dir, BUNDLES_INFO), 'r') as f:
        for line in f:
            if line[0] != '#':
                p = line.rstrip().split(',')
                if len(p) is 5:
                    bundles.add(p[2])

    if not len(bundles) is 0:
        check_list = ['plugins']
        print('bundles count: {}'.format(len(bundles)))

        for d in check_list:
            plugins = os.listdir(os.path.join(eclipse_dir, d))
            if not len(plugins) is 0:
                print('plugins count: {}'.format(len(plugins)))

                for f in plugins:
                    p = d + '/' + f
                    if not p in bundles and not p + '/' in bundles:
                        unused_list.append(p)

    return unused_list


def main(argv):
    print(argv)
    if len(argv) is 0 or len(argv[0]) is 0:
        # raise NameError('No eclipse dir is offered.')
        target_dir = '.'
    else:
        target_dir = argv[0]

    eclipse_dir = os.path.abspath(target_dir)
    camp_dir = os.path.abspath(datetime.now().strftime(os.path.join(eclipse_dir, 'scan_result-%Y%m%d%H%M%S')))

    unused_list = find_unused_item(eclipse_dir)
    if not len(unused_list) is 0:
        list_handler(eclipse_dir, camp_dir, unused_list)
    else:
        print('Nothing to do.')


if __name__ == '__main__':
    main(sys.argv[1:])
