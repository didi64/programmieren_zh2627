from IPython import get_ipython
from IPython.core.magic import Magics, cell_magic, magics_class, needs_local_scope


@magics_class
class MyCustomMagics(Magics):

    @cell_magic
    @needs_local_scope
    def run_cell(self, line, cell, local_ns=None):
        if line.strip() == '':
            line = '1'
        try:
            n = eval(line, local_ns)
        except SyntaxError:
            raise SyntaxError(f'{line!r} is not a valid expression!')

        if type(n) is not int:
            raise ValueError('Usage: %%run_cell <non-negative integer>')

        print(f'running cell {max(0, n)} times')
        for _ in range(n):
            self.shell.run_cell(cell)


# Register the plugin within JupyterLab / IPython
get_ipython().register_magics(MyCustomMagics)