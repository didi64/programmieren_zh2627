import os
import fnmatch
from pathlib import Path


def find_file(rootdir, pats, exclude_pats=(), exclude_dirs=(), hidden_dir=False):
    '''returns a list of full file names of the matched files.
       - hidden files are excluded.
       - hidden_dir can be turned on
       - exclude_dirs: list of folders to exclude
       - pats: tuple, glob-patterns to match
       - exclude_pats: files matching these patterns are excluded
    '''
    results = []

    for root, folders, files in os.walk(rootdir):
        # prune folders to recurse on
        folders[:] = [f for f in folders if (hidden_dir or not f.startswith('.')) and f not in exclude_dirs]

        for file in files:
            if any(fnmatch.fnmatch(file, pat) for pat in pats):
                if file.startswith('.'):
                    continue
                if any(fnmatch.fnmatch(file, pat) for pat in exclude_pats):
                    continue

                full_path = Path(root) / file
                results.append(full_path)

        return results


def file_iter(rootdir, pats, exclude_pats=(), exclude_dirs=(), hidden_dir=False):
    '''as find_file, but as an iterator'''
    for root, folders, files in os.walk(rootdir):
        folders[:] = [f for f in folders if (hidden_dir or not f.startswith('.')) and f not in exclude_dirs]

        for file in files:
            if any(fnmatch.fnmatch(file, pat) for pat in pats):
                if file.startswith('.'):
                    continue
                if any(fnmatch.fnmatch(file, pat) for pat in exclude_pats):
                    continue

                full_path = Path(root) / file
                yield full_path