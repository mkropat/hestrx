__all__ = [
    'cmd',
    'echo',
    'persisted_setting',

    'buffer_flags',
    'buffer_vars',
    'global_flags',
    'global_vars',
    'setting_flags',
    'settings',
    'tab_flags',
    'tab_vars',
    'vim_flags',
    'vim_vars',
    'window_flags',
    'window_vars',
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
    value = getattr(settings, setting)
    try:
        yield
    finally:
        setattr(settings, setting, value)

def quote_str(s):
    return '"{}"'.format(
        s.replace('\\', '\\\\').replace('"', '\\"')
    )

class FlagVariables:
    def __init__(self, scope=''):
        self.__dict__['scope'] = scope

    def __getattr__(self, name):
        var = self.__dict__['scope'] + name
        return vim.eval('exists("{0}") && {0}'.format(var)) != '0'

    def __setattr__(self, name, value):
        var = self.__dict__['scope'] + name
        if value:
            cmd('let {}=1'.format(var))
        else:
            cmd('unlet {}'.format(var))

class Variables:
    def __init__(self, scope=''):
        self.__dict__['scope'] = scope

    def __getattr__(self, name):
        var = self.__dict__['scope'] + name
        return vim.eval(var)

    def __setattr__(self, name, value):
        var = self.__dict__['scope'] + name
        cmd('let {}={}'.format(
            var,
            quote_str(value) if isinstance(value, str) else value
        ))

class Settings:
    def __getattr__(self, name):
        return vim.eval('&' + name)

    def __setattr__(self, name, value):
        cmd('let &{}={}'.format(
            name,
            quote_str(value) if isinstance(value, str) else value
        ))

class FlagSettings:
    def __getattr__(self, name):
        return vim.eval('&' + name) != '0'

    def __setattr__(self, name, value):
        if value:
            cmd('set ' + name)
        else:
            cmd('set no' + name)

settings = Settings()
setting_flags = FlagSettings()

buffer_flags = FlagVariables('b:')
buffer_vars = Variables('b:')
global_flags = FlagVariables('g:')
global_vars = Variables('g:')
tab_flags = FlagVariables('t:')
tab_vars = Variables('t:')
vim_flags = FlagVariables('v:')
vim_vars = Variables('v:')
window_flags = FlagVariables('w:')
window_vars = Variables('w:')
