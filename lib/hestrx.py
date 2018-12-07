# -*- coding: utf-8 -*-

import codecs
import timeit

def generate_bytes(hex_iter):
    for chunk in hex_iter:
        parts = chunk.split()
        if len(parts) > 0 and parts[0].endswith(':'):
            parts = parts[1:]
        yield bytearray().join(fromhex(p) for p in parts)

def generate_hex(data_iter):
    line_length = 16

    i = 0
    line = []
    for chunk in data_iter:
        for byte in bytearray(chunk):
            line.append('{:02x}'.format(byte))
            if len(line) == line_length:
                yield format_line(line, i)
                i += line_length
                line = []

    if len(line) > 0:
        yield format_line(line, i)

def as_ascii(hex_iter):
    for chunk in hex_iter:
        parts = chunk.split()
        if len(parts) > 0 and parts[0].endswith(':'):
            parts = parts[1:]
        try:
            as_bytes = bytearray().join(fromhex(p) for p in parts)
            as_str = as_bytes.decode('latin-1')
            yield u''.join(printable_ascii.get(c, u'·') for c in as_str)
        except ValueError:
            yield '?'*16

def iter_split(str_iter, sep):
    buf = ''

    for chunk in str_iter:
        buf += chunk

        parts = buf.split(sep)
        for part in parts[:-1]:
            yield part

        buf = parts[-1]

def prepend(value, iterable):
    i = iter(iterable)
    first = next(i)
    yield value + first
    for x in i:
        yield x

def lstrip(value, iterable):
    i = iter(iterable)
    first = next(i)
    if first[:len(value)] == value:
        first = first[len(value):]
    yield first
    for x in i:
        yield x

def fromhex(hex_str):
    if len(hex_str) % 2 != 0:
        hex_str = '0' + hex_str
    return bytearray.fromhex(hex_str)

def format_line(line, i):
    line_no = 'STRCTHEX' if i == 0 else '{:08x}'.format(i)
    return '{}: {}'.format(line_no, ' '.join(line))

def copyerrors(err):
    (escaped, end) = codecs.namereplace_errors(err)

    badData = b''
    while escaped:
        if not is_escape_sequence(escaped[0:6]):
            raise err

        badData += bytes.fromhex(escaped[2:6])
        escaped = escaped[6:]

    return (badData, end)

def is_escape_sequence(s):
    return s[0:2] == '\\u' and len(s) == 6

codecs.register_error('copyerrors', copyerrors)

class Stopwatch:
    def __init__(self, precision=2):
        self._precision = precision
        self._split = timeit.default_timer()

    def stop(self):
        start = self._split
        self._split = timeit.default_timer()
        return round(self._split - start, self._precision)

printable_ascii = {
    '\x09': u'→',
    '\x0a': u'←',
    '\x0d': u'↓',
    ' ': ' ',
    '!': '!',
    '"': '"',
    '#': '#',
    '$': '$',
    '%': '%',
    '&': '&',
    '\'': '\'',
    '(': '(',
    ')': ')',
    '*': '*',
    '+': '+',
    ',': ',',
    '-': '-',
    '.': '.',
    '/': '/',
    '0': '0',
    '1': '1',
    '2': '2',
    '3': '3',
    '4': '4',
    '5': '5',
    '6': '6',
    '7': '7',
    '8': '8',
    '9': '9',
    ':': ':',
    ';': ';',
    '<': '<',
    '=': '=',
    '>': '>',
    '?': '?',
    '@': '@',
    'A': 'A',
    'B': 'B',
    'C': 'C',
    'D': 'D',
    'E': 'E',
    'F': 'F',
    'G': 'G',
    'H': 'H',
    'I': 'I',
    'J': 'J',
    'K': 'K',
    'L': 'L',
    'M': 'M',
    'N': 'N',
    'O': 'O',
    'P': 'P',
    'Q': 'Q',
    'R': 'R',
    'S': 'S',
    'T': 'T',
    'U': 'U',
    'V': 'V',
    'W': 'W',
    'X': 'X',
    'Y': 'Y',
    'Z': 'Z',
    '[': '[',
    '\\': '\\',
    ']': ']',
    '^': '^',
    '_': '_',
    '`': '`',
    'a': 'a',
    'b': 'b',
    'c': 'c',
    'd': 'd',
    'e': 'e',
    'f': 'f',
    'g': 'g',
    'h': 'h',
    'i': 'i',
    'j': 'j',
    'k': 'k',
    'l': 'l',
    'm': 'm',
    'n': 'n',
    'o': 'o',
    'p': 'p',
    'q': 'q',
    'r': 'r',
    's': 's',
    't': 't',
    'u': 'u',
    'v': 'v',
    'w': 'w',
    'x': 'x',
    'y': 'y',
    'z': 'z',
    '{': '{',
    '|': '|',
    '}': '}',
    '~': '~',
}
