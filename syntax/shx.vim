if exists("b:current_syntax")
    finish
endif

syntax case ignore
syntax match shxHex "\v<\x+>"
syntax match shxHexAlt "\v(^(.*:)?\s*([^ \t:]+\s+\S+\s+)*)@<!<\x+>"
syntax match shxLabel "\v^\s*\w+:"he=e-1

highlight default link shxHex   Number
highlight default link shxHexAlt Normal
highlight default link shxLabel Identifier

let b:current_syntax='shx'
