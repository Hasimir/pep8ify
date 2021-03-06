#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functools import partial
import os
from os.path import join
import shutil
from difflib import unified_diff

from lib2to3.main import main

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), '')


def setup():
    pass


def teardown():
    # This finds all of the backup files that we created and replaces
    # the *_in.py files that were created for testing
    potential_backups = []
    for root, dirs, files in os.walk(FIXTURE_PATH):
        for filename in files:
            potential_backups.append(join(root, filename))

    real_backups = [potential_backup for potential_backup in potential_backups
                    if potential_backup.endswith(".bak")]
    for backup in real_backups:
        shutil.move(backup, backup.replace(".bak", ""))


def in_and_out_files_from_directory(directory):
    fixture_files = os.listdir(directory)
    fixture_in_files = [join(directory, fixture_file)
        for fixture_file in fixture_files if fixture_file.endswith("_in.py")]
    all_fixture_files = [(fixture_in, fixture_in.replace("_in.py", "_out.py"))
        for fixture_in in fixture_in_files]
    return all_fixture_files


def test_all_fixtures():
    for root, dirs, files in os.walk(FIXTURE_PATH):
        # Loop recursively through all files. If the files is in a
        # subdirectory, only run the fixer of the subdirectory name, else run
        # all fixers.
        for in_file, out_file in in_and_out_files_from_directory(root):
            fixer_to_run = None

            # This partial business is a hack to make the description
            # attribute actually work.
            # See http://code.google.com/p/python-nose/issues/detail?id=244#c1
            func = partial(check_fixture, in_file, out_file, fixer_to_run)
            func.description = "All fixes"
            if in_file.startswith(FIXTURE_PATH):
                func.description = in_file[len(FIXTURE_PATH):]
            yield (func,)


test_all_fixtures.setup = setup
test_all_fixtures.teardown = teardown


def check_fixture(in_file, out_file, fixer):
    if fixer:
        main("pep8ify.fixes", args=['--no-diffs', '--fix', fixer, '-w', in_file])
    else:
        main("pep8ify.fixes", args=['--no-diffs', '--fix', 'all',
            '--fix', 'maximum_line_length', '-w', in_file])
    in_file_contents = open(in_file, 'r').readlines()
    out_file_contents = open(out_file, 'r').readlines()

    if in_file_contents != out_file_contents:
        text = "in_file doesn't match out_file\n"
        text += ''.join(unified_diff(out_file_contents, in_file_contents,
                                     'expected', 'refactured result'))
        raise AssertionError(text)
