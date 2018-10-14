function! hestrx#ToggleHex()
  if !exists('g:loaded_hestrx_python')
    if !has('pythonx')
      echohl warningMsg
      echo 'Python required. Please install Python 2 or 3 and set pyxversion.'
      echohl None
      return
    endif

    pythonx <<EOF
import sys, vim
sys.path.append(vim.eval('g:hestrx_lib_dir'))
import hestrx_vim
EOF

    let g:loaded_hestrx_python = 1
  endif

  pythonx hestrx_vim.toggle_hex()
endfunction
