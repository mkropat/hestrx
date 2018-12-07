__all__ = [
    'cmd',
    'echo',
    'persisted_setting',
    'window_context',
]

from contextlib import contextmanager
import vim

def cmd(*vim_commands):
    vim.command(' | '.join(vim_commands))

def echo(msg, highlight=None):
    echo_cmd = 'echo {}'.format(quote_str(str(msg)))
    if highlight is None:
        cmd('redraw', echo_cmd)
    else:
        cmd(
            'redraw',
            'echohl ' + highlight,
            echo_cmd,
            'echohl None'
        )

@contextmanager
def persisted_setting(setting):
    value = vim.current.buffer.options[setting]
    try:
        yield
    finally:
        vim.current.buffer.options[setting] = value

@contextmanager
def window_context(context):
    original = vim.current.window
    vim.current.window = context
    try:
        yield
    finally:
        vim.current.window = original

def quote_str(s):
    return '"{}"'.format(
        s.replace('\\', '\\\\').replace('"', '\\"')
    )
