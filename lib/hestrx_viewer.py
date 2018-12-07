import vim

from hestrx import as_ascii
from hestrx import generate_bytes

from hestrx_vimwrapper import cmd
from hestrx_vimwrapper import window_context

def toggle_viewer():
    _, viewer_win = get_linked_viewer_wins()
    if viewer_win is None:
        open_viewer()
    else:
        close_viewer()

def open_viewer():
    linked_win, viewer_win = get_linked_viewer_wins()

    if viewer_win is None:
        cmd('rightbelow 20 vsplit', 'enew')

        viewer_win = vim.current.window

        win_id = linked_win.vars.get('hestrx_win_id', None)
        if win_id is None:
            win_id = next_win_id()
            linked_win.vars['hestrx_win_id'] = win_id
        viewer_win.vars['hestrx_linked_win'] = win_id

        viewer_win.options['list'] = False
        viewer_win.options['number'] = False
        viewer_win.options['relativenumber'] = False
        viewer_win.options['spell'] = False
        viewer_win.options['wrap'] = False

        buf = viewer_win.buffer
        buf.options['bufhidden'] = 'hide'
        buf.options['buftype'] = 'nofile'
        buf.options['swapfile'] = False
        buf.options['buflisted'] = False

        vim.current.window = linked_win

    update_viewer()

def close_viewer():
    linked_win, viewer_win = get_linked_viewer_wins()
    if viewer_win is not None:
        del viewer_win.vars['hestrx_linked_win']
        cmd('bdelete {}'.format(viewer_win.buffer.number))

def update_viewer():
    linked_win, viewer_win = get_linked_viewer_wins()

    if linked_win is None or viewer_win is None:
        return

    viewer_width = int(vim.eval('winwidth({})'.format(viewer_win.number)))
    if viewer_width != 20:
        with window_context(viewer_win):
            cmd('vertical resize 20')

    viewer_line_start = viewer_win.buffer.vars.get('line_start', -1)
    viewer_line_end = viewer_win.buffer.vars.get('line_end', -1)

    line_start = line_end = None
    with window_context(linked_win):
        line_start = int(vim.eval('line("w0")')) - 1
        line_end = int(vim.eval('line("w$")'))

    if line_start != viewer_line_start or line_end != viewer_line_end:
        lines = linked_win.buffer[line_start:line_end]
        viewer_win.buffer[:] = list(as_ascii(lines))

        viewer_win.buffer.vars['line_start'] = line_start
        viewer_win.buffer.vars['line_end'] = line_end

def get_linked_viewer_wins():
    linked_win_id = vim.current.window.vars.get('hestrx_linked_win', None)
    win_id = vim.current.window.vars.get('hestrx_win_id', None)

    if linked_win_id is not None:
        linked_win = next(
            (w for w in vim.current.tabpage.windows if w.vars.get('hestrx_win_id', None) == linked_win_id),
            None
        )
        viewer_win = vim.current.window
    elif win_id is not None:
        linked_win = vim.current.window
        viewer_win = next(
            (w for w in vim.current.tabpage.windows if w.vars.get('hestrx_linked_win', None) == win_id),
            None
        )
    else:
        linked_win = vim.current.window
        viewer_win = None

    return (linked_win, viewer_win)

def next_win_id():
    next_id = vim.vars.get('hestrx_next_win_id', 0)
    vim.vars['hestrx_next_win_id'] = next_id + 1
    return next_id
