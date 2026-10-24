from pathlib import Path
from IPython.display import display
from ipywidgets import Select


def get_folders_and_files(path):
    path = Path(path)
    folders = [name for f in path.iterdir()
               if (f.is_dir() and
                   (name := f.name) and not name.startswith('.') and not name.startswith('__'))
               ]
    files = [f.name for f in path.glob('*.ipynb')] + [f.name for f in path.glob('*.py')]

    return sorted(folders), sorted(files)


class PathSelector:
    type_prefix = {'top':   '⬆️ ',
                   'folder':    '  📁 ',
                   'file':    '  ',
                   }

    def __init__(self, rootdir):
        self.rootdir = Path(rootdir).absolute()
        self.relpath = self.rootdir.relative_to(self.rootdir)

        self.widget = Select(options=self.get_options(), value=None, rows=5)
        self.widget.observe(self.on_select, names='value')

    @property
    def path(self):
        return (self.rootdir / self.relpath).as_posix()

    def _make_options(self, folders, files):
        top = self.type_prefix['top'] + self.relpath.as_posix()
        folders = [self.type_prefix['folder'] + f for f in folders]
        files = [self.type_prefix['file'] + f for f in files]
        return [top] + folders + files

    def get_selected(self):
        val = self.widget.value
        for tp, pre in self.type_prefix.items():
            if val.startswith(pre):
                return tp, val.removeprefix(pre)

    def get_options(self):
        folders, files = get_folders_and_files(self.rootdir / self.relpath)
        options = self._make_options(folders, files)
        return options

    def update_options(self):
        options = self.get_options()
        self.widget.unobserve(self.on_select, names='value')
        self.widget.options = options
        self.widget.value = None
        self.widget.observe(self.on_select, names='value')

    def on_select(self, change):
        tp, f = self.get_selected()
        if tp == 'file' or (tp == 'top' and f == '.'):
            return
        elif tp == 'top':
            self.relpath = Path(self.rootdir / f).parent.relative_to(self.rootdir)
        elif tp == 'folder':
            self.relpath = self.relpath / f
        else:
            raise Exception('Should never happen!')

        self.update_options()

    def _ipython_display_(self):
        display(self.widget)