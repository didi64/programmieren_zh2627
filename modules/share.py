import sys
import os
import subprocess


ROOT = '/home/studi/work'
DATA = '/home/studi/work/.src/data'
SHARE_DIR = '/home/studi/work/share'


def get_prefixes(fn):
    with open(fn, 'r') as f:
        lines = f.readlines()
    prefixes = []
    for line in lines:
        fname, lname, email = line.strip().split()
        prefix = email[:email.index('@')]
        prefixes.append(prefix)
    return prefixes


def decode(numbers, pin):
    n = 0x10ffff
    s = ''.join([chr((int(x)-pin) % n) for x in numbers.split(',')])
    return s


def encode(t, pin):
    n = 0x10ffff
    s = ','.join([f'{((ord(x)+pin) % n):04}' for x in t])
    return s


def read_data(pin, fn='../../data/coords'):
    with open(fn) as f:
        coords = f.read()
    return decode(coords, pin)


def init_share(user, pin=12345):
    if os.path.exists(SHARE_DIR):
        print('Share Folder already exists!', file=sys.stderr)
        print('To delete it and reinstall, enter the following commands in a terminal:')
        print('cd && cd work')
        print('rm -rf share')
        return

    email_prefixes = get_prefixes(DATA + '/klassenliste.txt')
    tok = read_data(pin, DATA + '/coords')

    if tok[-3:] != 'HEe':
        raise ValueError('Ungueltiger Pin!')
    if user not in email_prefixes:
        raise ValueError(f'Unbekannter Email-Prefix {user}')

    with open(ROOT + '/.user', 'w') as f:
        f.write(user)

    with open(ROOT + '/.token_share', 'w') as f:
        f.write(tok)

    print('share folder initialized, cloning repos ...')
    res = subprocess.call(ROOT + '/.src/bin/init_share')
    if res == 0:
        print('Share-Folder fuer User {} eingerichtet.'.format(user))
    else:
        raise Exception('Etwas ging schief!  Errorcode {}'.format(res))