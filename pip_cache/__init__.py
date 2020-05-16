"""
File: pip-cache.py
Author: Bruno Beltran
Email: brunobeltran0@email.com
Github: https://github.com/brunobeltran0/pip-cache
Description: Keeps a local cache of all available PyPi packages. Fast, local,
manually updated version of `pip search`.
"""
from __future__ import print_function
import os
import sys

import marisa_trie

from .xdg import get_xdg_data_dir
import argparse


def get_pip_cache_data_dir():
    return os.path.join(get_xdg_data_dir(), 'pip-cache')


def get_raw_index_filename():
    return os.path.join(get_pip_cache_data_dir(), 'all-packages.txt')


def get_index_filename():
    return os.path.join(get_pip_cache_data_dir(), 'all-packages.marisa')


def get_all_package_names_raw():
    """Return all packages names in the cache, as a newline-delimited string
    """
    raw_index_filename = get_raw_index_filename()

    if not os.path.isfile(raw_index_filename):
        return []

    with open(raw_index_filename, 'r') as f:
        return f.read()


def get_all_package_names():
    """Return a list of all packages names in the cache
    """
    return get_all_package_names_raw().splitlines()


def get_package_names(prefix=''):
    """Return a list of packages name strings from cache matching a prefix.
    """
    index_trie_filename = get_index_filename()

    if not os.path.isfile(index_trie_filename):
        return []

    index = marisa_trie.Trie()
    index.load(index_trie_filename)
    return index.keys(prefix)


def pkgnames(prefix=''):
    if not prefix:
        # If no prefix is provided, reading the package names from the raw list
        # is more performant
        print(get_all_package_names_raw())
    else:
        matching_packages = get_package_names(prefix=prefix)
        response = '\n'.join(matching_packages)
        print(response)


#TODO: support auto-async updates
# update_interval = timedelta(days=1)
# update_index_now = False
# import time
# from datetime import timedelta
# if not os.path.isfile(index_filename):
#     open(index_filename, 'a').close()
#     update_index_now = True

# now = time.time()
# update_time = os.path.getmtime(index_filename)
# if now - update_time > update_interval.total_seconds():
#     update_index_now = True

# there does not seem to be a good behavior for case when completion is
# attempted during update of index, since blocking to wait for completion seems
# even worse than just using the partial or empty index (and thus failing to
# complete correctly) until the update is done. Thus, we go with the latter
# option, and use no locking of our index file.
def update_package_list():
    try:
        import xmlrpclib
    except ImportError:
        import xmlrpc.client as xmlrpclib

    pip_cache_data_dir = get_pip_cache_data_dir()
    raw_index_filename = get_raw_index_filename()
    index_filename = get_index_filename()

    # make sure that the directory we might be writing in exists
    if not os.path.isdir(pip_cache_data_dir):
        os.mkdir(pip_cache_data_dir)

    print('Connecting to PyPi...', end='', flush=True)
    client = xmlrpclib.ServerProxy('https://pypi.python.org/pypi')
    print('done!')

    print('downloading package names...', end='', flush=True)
    packages = client.list_packages()
    print('done!')

    print('Writing packages to cache...', end='', flush=True)
    with open(raw_index_filename, 'w') as f:
        f.write('\n'.join(packages))
    print('done!')

    print('Indexing packages...', end='', flush=True)
    trie = marisa_trie.Trie(packages)
    trie.save(index_filename)
    print('done!')


def main():
    parser = argparse.ArgumentParser(
        prog='pip-cache',
        description='Handle an offline cache of available pip libraries'
    )
    subparsers = parser.add_subparsers()

    parser_update = subparsers.add_parser(
        'update',
        help='Updates the local cache of pip package names',
    )
    parser_update.set_defaults(func=update_package_list)

    parser_pkgnames = subparsers.add_parser(
        'pkgnames',
        help='List packages whose names start with a prefix',
    )
    parser_pkgnames.add_argument(
        'prefix', nargs="?", type=str, default='',
        help='Optional prefix.',
    )
    parser_pkgnames.set_defaults(func=pkgnames)
    #args = parser.parse_args(['pkgnames', 'test'])
    #args = parser.parse_args(['update'])
    # if user passes nothing, assume he wants help
    if len(sys.argv) == 1:
        sys.argv.append('--help')
    args = parser.parse_args(sys.argv[1:])
    func_args = vars(args)
    func_args = dict(func_args)
    func_args.pop('func', None)
    args.func(**func_args)


if __name__ == '__main__':
    main()
