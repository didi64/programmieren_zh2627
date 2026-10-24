import re
from IPython import get_ipython
from IPython.core.magic import Magics, cell_magic, magics_class


@magics_class
class ContentModifierMagic(Magics):

    @staticmethod
    def decode_umlauts(text):
        umlaut_mapping = {
            '&auml;': 'ä', '&ouml;': 'ö', '&uuml;': 'ü',
            '&Auml;': 'Ä', '&Ouml;': 'Ö', '&Uuml;': 'Ü'
        }
        pattern = re.compile('|'.join(re.escape(key) for key in umlaut_mapping.keys()))
        return pattern.sub(lambda match: umlaut_mapping[match.group(0)], text)

    @cell_magic
    def umlauts(self, line, cell):
        """Converts the cell contents to uppercase and replaces the cell text."""
        new_cell_text = self.decode_umlauts(f'%%umlauts  \n{cell}')
        self.shell.set_next_input(new_cell_text, replace=True)


get_ipython().register_magics(ContentModifierMagic)