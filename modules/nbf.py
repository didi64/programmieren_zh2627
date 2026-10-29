import json
import os
import re
from IPython.display import display, Markdown
from ipywidgets import Output, VBox, HBox, Button, Text, Checkbox, BoundedIntText
from pathselector import PathSelector


def get_score(alls, anys=None):
    if 0 in alls:
        return 0

    return 2*sum(x/(x + 1.2) for x in alls) + sum(x/(x + 1.2) for x in anys)


def file_iter(rootdir):
    for root, folders, files in os.walk(rootdir):
        folders[:] = [f for f in folders if not (f.startswith('.') or f.startswith('__'))]
        for file in files:
            if file.endswith('.py') or file.endswith('.ipynb'):
                yield root + '/' + file


def search_file(file, pats):
    if file.endswith('.ipynb'):
        return _search_notebook(file, pats)
    elif file.endswith('.py'):
        return _search_pyfile(file, pats)
    else:
        raise ValueError('filename must end with ".py" or ".ipynb"')


def _search_notebook(file, pats):
    counts = [0] * len(pats)

    with open(file, 'r') as f:
        notebook = json.loads(f.read())

    tags = notebook['metadata'].get('tags', [])
    tags = ', '.join(tag.lower() for tag in tags)
    for i, pat in enumerate(pats):
        counts[i] += bool(pat.search(tags))*5

    for cell in notebook['cells']:
        if cell['cell_type'] not in ('code', 'markdown'):
            continue

        for line in cell['source']:
            for i, pat in enumerate(pats):
                counts[i] += bool(pat.search(line))

    return counts


def _search_pyfile(file, pats):
    counts = [0] * len(pats)

    with open(file, 'r') as f:
        lines = f.readlines()

    for line in lines:
        for i, pat in enumerate(pats):
            counts[i] += bool(pat.search(line))

    return counts


def search(rootdir, alls=None, anys=None, max_res=5, ignorecase=True, regex=False):
    def make_patters(s: str, ignorecase=True, regex=False):
        if not s:
            return []

        flags = re.IGNORECASE if ignorecase else re.NOFLAG

        if regex:
            pats = [re.compile(s, flags=flags)]
        else:
            pats = [re.compile(fr'\b{ss}\b', flags=flags) for ss in s.split()]

        return pats

    all_pats = make_patters(alls, ignorecase, regex)
    any_pats = make_patters(anys, ignorecase, regex)
    pats = all_pats + any_pats

    if not pats:
        return [], 0

    results = []
    for fn in file_iter(rootdir):
        counts = search_file(fn, pats)
        n = len(all_pats)
        score = get_score(counts[:n], counts[n:])

        if score:
            result = (score, fn)
            results.append(result)

    results = sorted(results, key=lambda x: x[0], reverse=True)[:max_res]
    results = [(round(score), file) for score, file in results]
    return results, len(results)


def word_finder(rootdir, alls=None, anys=None, max_res=5, ignorecase=True, regex=False):
    show_results(*search(rootdir, alls, anys, max_res, ignorecase, regex))


def show_results(results, tot_results):
    md_escape = lambda s: re.sub(r'([\\`*_{}\[\]()#+\-.!])', r'\\\1', s)
    display(Markdown(f'**Results** ({len(results)}/{tot_results}):  \n'))
    for score, path in results:
        rel_path = os.path.relpath(path, os.getcwd())
        link = f'[({score}) {md_escape(rel_path)}](<{rel_path}>)'  # <rel_path> required im Filename has Spaces
        link = Markdown(link)
        display(link)


class InputCollector:
    def __init__(self):
        self._alls = Text(value='',
                          placeholder='Funktion Variable',
                          continuous_update=False,
                          description='Alle',
                          )
        self._anys = Text(value='',
                          placeholder='dict list import\\smath',
                          continuous_update=False,
                          description='Opt.',
                          )
        self._max_res = BoundedIntText(value=5,
                                       description='Resultate',
                                       min=1,
                                       layout={'width': '150px'},
                                       )
        self._regex = Checkbox(indent=False,
                               description='Regex',
                               layout={'width': '100px'},
                               )
        self._ignorecase = Checkbox(value=True,
                                    description='Case egal',
                                    indent=False,
                                    layout={'width': '100px'},
                                    )

        self._hbox = HBox(children=[self._regex, self._ignorecase, self._max_res])
        self.widget = VBox(children=[self._alls, self._anys, self._hbox])

    @property
    def args(self):
        return (self._alls.value, self._anys.value, self._max_res.value,
                self._ignorecase.value, self._regex.value,
                )

    def _ipython_display_(self):
        display(self.widget)


class NBFinder:
    def __init__(self, rootdir):
        self.out = Output()
        self.ic = InputCollector()
        self.ps = PathSelector(rootdir)
        self.button = Button(description='suche!',
                             layout={'border': '2px solid red', 'width': '100px'},
                             )
        self.button.on_click(self.on_click)
        self.widget = VBox(children=[HBox(children=[self.ps.widget, self.ic.widget]), self.button])

    def on_click(self, bt):
        results, n_results = search(self.ps.path, *self.ic.args)
        self.out.clear_output()
        with self.out:
            show_results(results, n_results)

    def _ipython_display_(self):
        display(self.widget, self.out)


if __name__ == '__main__':
    import sys

    JLAB_DIR = '/home/probst/Projects/JupyterNotebooks'
    if len(sys.argv) == 2:
        root = sys.argv[1]
    else:
        root = os.environ.get('JLAB_DIR', JLAB_DIR)
    display(NBFinder(root))