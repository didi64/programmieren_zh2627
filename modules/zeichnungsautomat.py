from automatons import DEA
from canvasenvs import DrawEnv


abc = 'abcdefghijklmnopqrstuvwxyz'
digits = '0123456789.-'
sep = ','
special_chars = '#'
symbols = abc + abc.upper() + digits + sep + special_chars


def make_delta():
    delta = {
        (0, 'u'): (0, 'u'),  # pen up
        (0, 'd'): (0, 'd'),  # pen down
        (0, 'E'): (0, 'E'),  # cls
        (0, 'l'): (1, 'l'),  # set linewidth <linewidth>;
        (0, 'f'): (1, 'f'),  # set fill_style <html_color>;
        (0, 's'): (1, 's'),  # set stroke_style <html_color>;
        (0, 'g'): (1, 'g'),  # goto x,y;
        (0, 'G'): (1, 'G'),  # Goto +x,+y;
        (0, 'r'): (1, 'r'),  # stroke_rect width [,height];
        (0, 'R'): (1, 'R'),  # fill_rect width [,height];
        (0, 'c'): (1, 'c'),  # stroke_circle radius;
        (0, 'C'): (1, 'C'),  # fill_circle radius;
        (0, 'e'): (1, 'e'),  # clear_rect width [, height];
        (1, ';'): (0, ';'),  # draw (exec cmd_buffer)
    }
    for c in symbols:
        delta[(1, c)] = (1, c)
    return delta


def get_automat_and_canvas(**kwargs):
    delta = make_delta()
    automat = DEA(delta)
    dm = DrawEnv(automat, **kwargs)  # Drawing-Machine
    return automat, dm