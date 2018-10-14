if exists('g:loaded_hestrx')
  finish
endif

let g:loaded_hestrx = 1

let s:script_dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')
let g:hestrx_lib_dir = fnamemodify(s:script_dir, ':h') . '/lib'

command -nargs=0 Hestrx call hestrx#ToggleHex()

if mapcheck('gX', 'n') == ''
  nnoremap gX :Hestrx<cr>
endif
