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

from hestrx_viewer import close_viewer
from hestrx_viewer import open_viewer
from hestrx_viewer import toggle_viewer
from hestrx_viewer import update_viewer

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
    buf = vim.current.buffer
    if 'hestrx' in buf.vars:
        close_viewer()
        buf2bin()
    else:
        buf2hex()
        open_viewer()

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

    if vim.current.buffer.options['buftype']:
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
    buf = vim.current.buffer
    setting = 'hestrx' in buf.vars
    heuristic = in_hex_heuristic()

    if setting != heuristic:
        if heuristic:
            set_hex()
        else:
            set_bin()

    return heuristic

def bin2hex():
    buf = vim.current.buffer

    with persisted_setting('modified'):
        line_ending = get_line_ending()
        if sys.version_info.major == 2:
            as_bytes = (l + line_ending for l in buf)
        else:
            lines = (l + line_ending for l in buf)

            as_bytes = (l.encode(get_fileencoding(), errors='copyerrors') for l in lines)

        bytes_with_bom = prepend(get_bom(), as_bytes)
        buf[:] = list(generate_hex(bytes_with_bom))

def hex2bin():
    buf = vim.current.buffer

    with persisted_setting('modified'):
        byte_iter = generate_bytes(buf)
        str_iter = iterdecode(handle_bom(byte_iter), get_fileencoding(), errors='copyerrors')
        lines = iter_split(str_iter, get_line_ending())

        buf[:] = list(lines)

def set_bin():
    buf = vim.current.buffer

    buf.options['buftype'] = ''
    del buf.vars['hestrx']

    if 'hestrx_filetype' in buf.vars:
        cmd('setlocal filetype=' + buf.vars['hestrx_filetype'].decode('ascii'))
        del buf.vars['hestrx_filetype']

def set_hex():
    buf = vim.current.buffer

    buf.options['buftype'] = 'acwrite'
    buf.vars['hestrx'] = True

    current_filetype = buf.options['filetype']
    if current_filetype != 'shx':
        buf.vars['hestrx_filetype'] = current_filetype
        cmd('setlocal filetype=shx')

    if 'hestrx_write_hook' not in buf.vars:
        cmd('autocmd BufWriteCmd <buffer> pythonx hestrx_vim.save()')
        buf.vars['hestrx_write_hook'] = True

def write_hex(file_name):
    buf = vim.current.buffer

    with open(file_name, 'wb') as f:
        for chunk in generate_bytes(buf):
            f.write(chunk)
    buf.options['modified'] = False

def write_vim(file_name):
    write_cmd = 'write{} {} {}'.format(
        ('!' if vim.vvars['cmdbang'] else ''),
        vim.vvars['cmdarg'],
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
        vim.current.buffer.options['bomb'] = False
    yield first
    for x in i:
        yield x

def get_bom():
    if not vim.current.buffer.options['bomb']:
        return b''
    return encoding_to_bom.get(get_fileencoding(), b'')

def get_fileencoding():
    result = vim.current.buffer.options['fileencoding'].decode('ascii')
    if not result:
        result = 'utf-8'
    return vim_to_python_encodings.get(result, result)

def get_line_ending():
    fileformat = vim.current.buffer.options['fileformat']

    result = '\n'
    if fileformat == 'dos':
        result = '\r\n'
    elif fileformat == 'mac':
        result = '\r'

    return result
