function! hestrx#ToggleHex()
  if !s:load_python()
    return
  endif

  if !exists('b:hestrx_buf_autocmds')
    autocmd CursorHold <buffer> pythonx hestrx_vim.update_viewer()
    autocmd CursorMoved <buffer> pythonx hestrx_vim.update_viewer()
    autocmd vimResized <buffer> pythonx hestrx_vim.update_viewer()

    let b:hestrx_buf_autocmds = 1
  endif

  pythonx hestrx_vim.toggle_hex()
endfunction

function! hestrx#ToggleViewer()
  if !s:load_python()
    return
  endif

  pythonx hestrx_vim.toggle_viewer()
endfunction

function! s:load_python()
  if !exists('g:loaded_hestrx_python')
    if !has('pythonx')
      echohl warningMsg
      echo 'Python required. Please install Python 2 or 3 and set pyxversion.'
      echohl None
      return 0
    endif

    pythonx <<EOF
import sys, vim
sys.path.append(vim.eval('g:hestrx_lib_dir'))
import hestrx_vim
EOF

    let g:loaded_hestrx_python = 1
  endif

  return 1
endfunction
