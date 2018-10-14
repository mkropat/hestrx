__all__ = ['toggle_hex', 'save']

import codecs
from codecs import iterdecode
import sys
import vim

from hestrx import generate_bytes
from hestrx import generate_hex
from hestrx import iter_split
from hestrx import prepend
from hestrx import Stopwatch

from hestrx_vimwrapper import cmd
from hestrx_vimwrapper import echo
from hestrx_vimwrapper import persisted_setting
from hestrx_vimwrapper import buffer_flags
from hestrx_vimwrapper import settings
from hestrx_vimwrapper import setting_flags
from hestrx_vimwrapper import vim_flags
from hestrx_vimwrapper import vim_vars

encoding_to_bom = {
    'utf_16_be': codecs.BOM_UTF16_BE,
    'utf_16_le': codecs.BOM_UTF16_LE,
    'utf_32_be': codecs.BOM_UTF32_BE,
    'utf_32_le': codecs.BOM_UTF32_LE,
}

vim_to_python_encodings = {
    'ucs-2':    'utf_16_be',
    'ucs-2le':  'utf_16_le',
    'utf-16':   'utf_16_be',
    'utf-16le': 'utf_16_le',
    'ucs-4':    'utf_32_be',
    'ucs-4le':  'utf_32_le',
}

def toggle_hex():
    if buffer_flags.hestrx:
        buf2bin()
    else:
        buf2hex()

def buf2bin():
    if not in_hex():
        return

    timer = Stopwatch()
    echo('Converting to binary. Please wait.')

    hex2bin()
    set_bin()

    echo('Converted to binary. ({} seconds)'.format(timer.stop()))

def buf2hex():
    if in_hex():
        return

    if settings.buftype != '':
        echo('Error converting to hex: buffer must be a normal file', highlight='warningMsg')
        return

    timer = Stopwatch()
    echo('Converting to hex. Please wait.')

    bin2hex()
    set_hex()

    echo('Converted to hex. ({} seconds)'.format(timer.stop()))

def save():
    afile = vim.eval('expand("<afile>")')
    if in_hex():
        timer = Stopwatch()
        write_hex(afile)
        echo('"{}" written in binary ({} seconds)'.format(
            afile,
            timer.stop()
        ))
    else:
        write_vim(afile)

def in_hex():
    setting = buffer_flags.hestrx
    heuristic = in_hex_heuristic()

    if setting != heuristic:
        if heuristic:
            set_hex()
        else:
            set_bin()

    return heuristic

def bin2hex():
    with persisted_setting('modified'):
        line_ending = get_line_ending()
        if sys.version_info.major == 2:
            as_bytes = (l + line_ending for l in vim.current.buffer)
        else:
            lines = (l + line_ending for l in vim.current.buffer)

            as_bytes = (l.encode(get_fileencoding(), errors='copyerrors') for l in lines)

        bytes_with_bom = prepend(get_bom(), as_bytes)
        vim.current.buffer[:] = list(generate_hex(bytes_with_bom))

def hex2bin():
    with persisted_setting('modified'):
        byte_iter = generate_bytes(vim.current.buffer)
        str_iter = iterdecode(handle_bom(byte_iter), get_fileencoding(), errors='copyerrors')
        lines = iter_split(str_iter, get_line_ending())

        vim.current.buffer[:] = list(lines)

def set_bin():
    settings.buftype = ''
    buffer_flags.hestrx = False

def set_hex():
    settings.buftype = 'acwrite'
    buffer_flags.hestrx = True

    if not buffer_flags.hestrx_write_hook:
        cmd('autocmd BufWriteCmd <buffer> pythonx hestrx_vim.save()')
        buffer_flags.hestrx_write_hook = True

def write_hex(file_name):
    with open(file_name, 'wb') as f:
        for chunk in generate_bytes(vim.current.buffer):
            f.write(chunk)
    setting_flags.modified = False

def write_vim(file_name):
    write_cmd = 'write{} {} {}'.format(
        ('!' if vim_flags.cmdbang else ''),
        vim_vars.cmdarg,
        file_name)
    cmd(write_cmd)

def in_hex_heuristic():
    return vim.current.buffer[0].startswith('STRCTHEX:')

def handle_bom(iterable):
    expected_bom = get_bom()
    i = iter(iterable)
    first = next(i)
    if first[:len(expected_bom)] == expected_bom:
        first = first[len(expected_bom):]
    else:
        setting_flags.bomb = False
    yield first
    for x in i:
        yield x

def get_bom():
    if not setting_flags.bomb:
        return b''
    return encoding_to_bom.get(get_fileencoding(), b'')

def get_fileencoding():
    result = settings.fileencoding
    if not result:
        result = 'utf-8'
    return vim_to_python_encodings.get(result, result)

def get_line_ending():
    fileformat = settings.fileformat

    result = '\n'
    if fileformat == 'dos':
        result = '\r\n'
    elif fileformat == 'mac':
        result = '\r'

    return result
