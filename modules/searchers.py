import os
import re
import nbf.searchables
from filetools import file_iter
from tagging import tag_finder as _search_tags
from ipywidgets import Output
from IPython.display import Markdown, display


def show_results(results, n=5):
    n = min(len(results), n)
    link_widget = Output(layout={'border': '1px solid black'})
    display(link_widget)
    with link_widget:
        display(Markdown('**Results** ({}/{}):  \n'.format(n, len(results))))
    for res in results[:n]:
        if isinstance(res, nbf.searchables.Searchable):
            nb_path = res['searchable'].path_to_file
            score = int(res['score'])
        else:
            nb_path = res
            score = None
        with link_widget:
            rel_path = os.path.relpath(nb_path, os.getcwd())
            link = '[({1}) {0}](<{0}>)  '.format(rel_path, score)
            link = Markdown(link)
            display(link)


def _search_words(words, rootdir='/home/studi/work'):
    results = []

    if type(words) is str:
        words = (words,)
    pats = set(re.compile(re.escape(k)) for k in words)

    files = file_iter(rootdir, pats=('*.ipynb', '*.py'), exclude_dirs=('__pycache__', 'src'))
    for fn in files:
        s = nbf.searchables.Searchable(fn)
        d = s.search(pats)

        all_scores = [d[x] for x in pats]
        score = nbf.helpers.get_score(all_scores)

        if not score:
            continue

        res = {'searchable': s,
               'score': score,
               }
        results.append(res)

    results = sorted(results, key=lambda x: x['score'], reverse=True)
    return results


def word_finder(*words, n=5, rootdir='/home/studi/work'):
    '''*words: str
        searches rootdir for notebooks containing the given words and shows links to these notebooks
    '''
    assert all(type(word) is str for word in words), 'all positional arguments must be strings!'
    res = _search_words(words, rootdir=rootdir)
    show_results(res, n=n)


def tag_finder(*words, n=5, rootdir='/home/studi/work'):
    assert all(type(word) is str for word in words), 'all positional arguments must be strings!'
    res = _search_tags(rootdir, words)
    show_results(res, n=n)