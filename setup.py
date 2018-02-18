#!/usr/bin/env python3.6
"""
Installation script.
"""
import os            # OS path traversal, testing if inodes are dirs.
import pip           # Installs packages.
import re            # Regex for getting attrs from __init__.py
import setuptools    # My setuptools bindings.
import shutil        # Checking for executables in $PATH env.
import subprocess    # Invoking git to inspect the commits.
import sys           # Accessing the stderr stream.
import dependencies  # Any package dependencies.


PKG = 'neko2'
OTHER_PKGS = ()
GIT_DIR = '.git'


###############################################################################
#                                                                             #
# Main setup.py script starts here.                                           #
#                                                                             #
###############################################################################


MAIN_INIT_FILE = os.path.join(PKG, '__init__.py')


with open(MAIN_INIT_FILE) as init:
    # noinspection PyTypeChecker
    attrs = {
        k: v for k, v in re.findall(
            r'__(\w+)__\s?=\s?\'([^\']*)\'',
            '\n'.join(filter(bool, init.read().split('\n')))
        )
    }
    
version = attrs.pop('version', None)
if not version:
    version = '0.0'
version += '.'

# If I forget to increment this number, we have a fallback. This number
# is the total number of commits made to the repo. Unfortunately this
# only works if `git` is installed, so I need to check for this one
# first. We also ensure '.git' is an existing directory before we do
# anything else, because we need that for `git log --oneline` to work.
# This is useful also because `git log` defaults to only checking the 
# current branch. This means I can work on a separate branch and this
# will only update the bot if it has had any new commits since then.
git_loc = shutil.which('git')
if git_loc and os.path.isdir(GIT_DIR):
    commits: str = subprocess.check_output(
        [git_loc, 'log', '--oneline'],
        universal_newlines=True
    )
    
    commit_number = str(commits.count('\n'))
    version += commit_number
else:
    print('You probably should consider installing Git on this machine.',
          file=sys.stderr)
    # If we have not got git installed, or the `.git` dir is missing, 
    # then we cannot get the commit count, so set the patch number to
    # 0.
    version += '0'

print(f'>Installing version {version} of Neko².',
      file=sys.stderr, end='\n\n')

attrs['version'] = version


print('>Will get the following dependencies:',
      *dependencies.dependencies,
      sep='\n •  ',
      file=sys.stderr,
      end='\n\n')

# Causes less problems in the long run.
pip.main(['install', *dependencies.dependencies])


# Detect the packages to store
def recurse(p):
    results = [p]
    for parent, dirs, _ in os.walk(p):
        results.extend(os.path.join(parent, _dir) for _dir in dirs)
    return tuple(results)


# Calculate all packages to get.
attrs['name'] = PKG
attrs['packages'] = *recurse(PKG), *[recurse(p) for p in OTHER_PKGS]

print('>Installing the following packages:', 
      *attrs['packages'],
      sep='\n •  ',
      file=sys.stderr,
      end='\n\n')

print(attrs)

setuptools.setup(**attrs)
