# PixelZen - prompt de fish. Quitar: borrar este fichero (revertir.sh lo hace).
function fish_prompt
    set -l ult $status
    set -l rosa e0837f; set -l dim 9a94b8; set -l cian 7fc4c4; set -l amb e0b36a; set -l verde 7fb88a; set -l rojo e0524a; set -l viol 8a4a79
    set -l ruta (string replace -r "^$HOME" "~" -- $PWD)
    set_color $viol; echo -n '╭─ '
    set_color $rosa; echo -n $USER
    set_color $dim; echo -n '@'(prompt_hostname | string lower)' '
    set_color $cian; echo -n $ruta
    if command -q git; and command git rev-parse --is-inside-work-tree >/dev/null 2>&1
        set -l rama (command git branch --show-current 2>/dev/null)
        test -z "$rama"; and set rama (command git rev-parse --short HEAD 2>/dev/null)
        set -l sucio (command git status --porcelain 2>/dev/null | count)
        set_color $dim; echo -n '  '
        set_color $verde; echo -n "⎇ $rama"
        test $sucio -gt 0; and begin; set_color $amb; echo -n " ~$sucio"; end
    end
    if test $ult -ne 0
        set_color $rojo; echo -n "  ✗ $ult"
    end
    echo
    set_color $viol; echo -n '╰─'
    set_color $rosa; echo -n '› '
    set_color normal
end
function fish_right_prompt
    set_color 5d5a86; echo -n (date +%H:%M)
    set_color normal
end
