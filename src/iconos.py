#!/usr/bin/env python3
"""PixelZen - genera el tema de iconos 'PixelZen' (pixel art) en tema/iconos/PixelZen.
Glifos monocromos: Pixelarticons (MIT, github.com/halfmage/pixelarticons). Azulejos, carpetas y hojas: propios.
Lo que no se cubra cae a breeze-dark (Inherits). Python puro."""
import configparser, glob, os, re, shutil, sys

RAIZ = os.path.expanduser('~/.local/share/pixelzen')
SRC = f'{RAIZ}/vendor/pixelarticons/svg'
OUT = f'{RAIZ}/tema/iconos/PixelZen'
BREEZE = '/usr/share/icons/breeze-dark'
WASHI, DIM = '#f3e9d2', '#b4aed4'

def glifo_d(nombre):
    f = f'{SRC}/{nombre}.svg'
    if not os.path.exists(f): return None
    return ' '.join(re.findall(r' d="([^"]+)"', open(f).read()))

def mezcla(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]; b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))

def escribe(ruta, txt):
    os.makedirs(os.path.dirname(ruta), exist_ok=True); open(ruta, 'w').write(txt)

CAB = '<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 {s} {s}" shape-rendering="crispEdges">\n'
ESTILO = '<style type="text/css" id="current-color-scheme">.ColorScheme-Text{color:%s}</style>\n' % WASHI

def mono(glifos, flip=False, op=1.0):
    """glifos: lista de nombres (se apilan). Un solo color que sigue el esquema (ColorScheme-Text)."""
    cuerpo = ''
    for g in glifos:
        d = glifo_d(g)
        if d: cuerpo += f'<path class="ColorScheme-Text" fill="currentColor" fill-opacity="{op}" d="{d}"/>\n'
    if not cuerpo: return None
    t = '<g transform="translate(24,0) scale(-1,1)">\n' + cuerpo + '</g>\n' if flip else cuerpo
    return CAB.format(s=24) + ESTILO + t + '</svg>\n'

def R(x, y, w, h, c, o=1.0): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}"' + (f' fill-opacity="{o}"' if o < 1 else '') + '/>\n'

def glifo_en(nombre, x, y, esc, color, op=1.0):
    d = glifo_d(nombre)
    return f'<path transform="translate({x},{y}) scale({esc})" fill="{color}" fill-opacity="{op}" d="{d}"/>\n' if d else ''

def azulejo(glifo, base, color_glifo=WASHI, extra=''):
    osc, claro, sombra = mezcla(base, '#05061a', 0.62), mezcla(base, '#ffffff', 0.28), mezcla(base, '#05061a', 0.28)
    s = CAB.format(s=32)
    s += R(2, 0, 28, 32, osc) + R(0, 2, 32, 28, osc)                      # borde con esquinas muescadas
    s += R(4, 2, 24, 28, base) + R(2, 4, 28, 24, base)
    s += R(4, 2, 24, 2, claro) + R(2, 4, 2, 2, claro)                     # luz arriba-izquierda
    s += R(4, 28, 24, 2, sombra) + R(28, 24, 2, 4, sombra)                # sombra abajo-derecha
    s += glifo_en(glifo, 4, 4, 1, '#05061a', 0.35) if glifo else ''      # sombra del glifo
    s += glifo_en(glifo, 4, 3, 1, color_glifo) if glifo else ''
    return s + extra + '</svg>\n'

def carpeta(glifo=None, abierta=False, base='#8a4a79'):
    osc, claro, sombra = mezcla(base, '#05061a', 0.65), mezcla(base, '#ffffff', 0.30), mezcla(base, '#05061a', 0.25)
    if abierta: base, claro = mezcla(base, '#ffffff', 0.12), mezcla(base, '#ffffff', 0.40)
    s = CAB.format(s=32)
    s += R(2, 4, 12, 4, osc) + R(2, 6, 28, 24, osc) + R(0, 8, 32, 20, osc)   # silueta
    s += R(4, 6, 8, 2, claro) + R(4, 8, 24, 2, claro)                       # pestaña y filo
    s += R(4, 10, 24, 16, base) + R(2, 10, 2, 16, base) + R(28, 10, 2, 16, base)
    s += R(4, 24, 24, 2, sombra)
    s += glifo_en(glifo, 10, 12, 0.5, WASHI, 0.95) if glifo else ''
    return s + '</svg>\n'

def hoja(glifo, color, etiqueta_color=None):
    osc, hoja_c, sombra = '#2b2850', '#e9e0cc', '#c9bfa6'
    s = CAB.format(s=32)
    s += R(6, 2, 14, 2, osc) + R(6, 4, 18, 2, osc) + R(6, 6, 20, 24, osc) + R(8, 30, 16, 0, osc)          # silueta con esquina doblada
    s += R(8, 4, 12, 2, hoja_c) + R(8, 6, 16, 22, hoja_c) + R(24, 6, 0, 0, hoja_c)
    s += R(20, 4, 2, 2, sombra) + R(22, 6, 2, 2, sombra) + R(20, 6, 2, 2, '#fff7e0')                     # pliegue
    s += R(8, 26, 16, 2, sombra)
    s += R(8, 8, 16, 4, color) + R(8, 8, 16, 1, mezcla(color, '#ffffff', 0.35))                             # franja de tipo
    s += glifo_en(glifo, 10, 14, 0.5, color, 1.0) if glifo else ''
    return s + '</svg>\n'

def torii(base='#14183f'):
    s = azulejo(None, base)[:-7]
    R_, R2 = '#e0524a', '#8a2420'
    s += R(5, 7, 22, 3, R_) + R(3, 6, 3, 2, R_) + R(26, 6, 3, 2, R_) + R(1, 5, 3, 2, R_) + R(28, 5, 3, 2, R_)
    s += R(7, 12, 18, 2, R_) + R(9, 10, 2, 17, R_) + R(21, 10, 2, 17, R_) + R(9, 24, 2, 3, R2) + R(21, 24, 2, 3, R2)
    s += R(5, 10, 22, 1, R2) + R(15, 10, 2, 2, '#16101e')
    return s + '</svg>\n'

# ----------------------------------------------------------------------- reglas (acciones, estado, dispositivos, lugares)
REGLAS = [
 (r'^document-open-recent|^view-history|^history|^clock|^appointment-soon', 'clock'),
 (r'^document-save', 'save'), (r'^document-open', 'folder'), (r'^(document|file|window|tab)-new|^folder-new', 'plus-box'),
 (r'^document-print|^printer|^print', 'printer'), (r'^document-export|^document-send|^upload|^archive-insert', 'upload'),
 (r'^document-import|^archive-extract|^download|^emblem-downloads', 'download'),
 (r'^document-edit|^edit-rename|^draw-freehand|^edit$|^editor', 'pencil'),
 (r'^edit-copy|^edit-duplicate|^duplicate', 'copy'), (r'^edit-cut', 'cut'), (r'^edit-paste', 'clipboard'),
 (r'^edit-delete|^edit-trash|^delete|^trash', 'trash'), (r'^edit-clear', 'x'),
 (r'^edit-find|^system-search|^search|^find', 'search'), (r'^edit-select', 'checkbox-on'),
 (r'^edit-undo|^undo', 'undo'), (r'^edit-redo|^redo', 'redo'),
 (r'^zoom-in', 'zoom-in'), (r'^zoom-out', 'zoom-out'), (r'^zoom', 'aspect-ratio'),
 (r'^list-add|^add$|^plus', 'plus'), (r'^list-remove|^remove$|^minus', 'minus'),
 (r'^(window-close|dialog-close|dialog-cancel|tab-close|process-stop|dialog-no|close)', 'x'),
 (r'^(dialog-ok|dialog-yes|emblem-ok|checkmark|task-complete|emblem-default|emblem-checked)', 'check'),
 (r'^system-log-out', 'logout'), (r'^system-shutdown|^application-exit|^system-exit', 'power'),
 (r'^system-reboot|^system-restart', 'reload'), (r'^system-suspend|^system-hibernate|^weather-clear-night|^night-light|^nightcolor', 'moon'),
 (r'^system-lock|^object-locked|^emblem-locked|^lock', 'lock'), (r'^object-unlocked|^emblem-unlocked|^unlock', 'unlock'),
 (r'^system-switch-user|^system-users|^user-group|^users', 'users'),
 (r'^pan-end|^arrow-right-double', 'chevron-right'), (r'^pan-start', 'chevron-left'), (r'^pan-up', 'chevron-up'), (r'^pan-down', 'chevron-down'),
 (r'^go-next|^arrow-right|^go-right', 'arrow-right'), (r'^go-previous|^arrow-left|^go-left', 'arrow-left'),
 (r'^go-up|^arrow-up', 'arrow-up'), (r'^go-down|^arrow-down', 'arrow-down'),
 (r'^go-home|^user-home|^folder-home|^home', 'home'),
 (r'^go-top', 'arrow-bar-up'), (r'^go-bottom', 'arrow-bar-down'), (r'^go-first', 'arrow-bar-left'), (r'^go-last', 'arrow-bar-right'),
 (r'^go-jump|^go-parent', 'corner-down-right'),
 (r'^view-refresh|^reload|^sync|^emblem-synchronizing|^state-sync|^view-restore-refresh', 'refresh'),
 (r'^view-fullscreen|^window-maximize|^zoom-fit', 'expand'), (r'^view-restore|^window-restore|^restore|^window-unmaximize', 'collapse'),
 (r'^window-minimize', 'minus'),
 (r'^view-list|^format-list-unordered', 'list-box'), (r'^view-grid|^view-list-icons|^view-app-grid|^view-media-visualization', 'grid-2x2-2'),
 (r'^view-sort|^sort', 'sort-vertical'), (r'^view-filter|^filter', 'filter'), (r'^view-visible|^visibility|^show-', 'eye'),
 (r'^view-hidden|^hint|^hide', 'eye-off'), (r'^view-calendar|^calendar|^appointment', 'calendar'),
 (r'^view-pim-notes|^knotes|^note', 'sticky-note'), (r'^view-statistics|^office-chart', 'chart'),
 (r'^configure|^preferences-system$|^preferences-other|^applications-system|^settings|^emblem-system|^systemsettings', 'settings-cog'),
 (r'^preferences-desktop-theme|^preferences-desktop-color|^color', 'colors-swatch'), (r'^preferences-desktop-font|^font', 'letter-a'),
 (r'^preferences-desktop-display|^video-display|^monitor|^display|^preferences-desktop$', 'monitor'),
 (r'^preferences-desktop-keyboard|^input-keyboard|^keyboard', 'keyboard'), (r'^input-mouse|^mouse|^preferences-desktop-mouse', 'mouse'),
 (r'^input-gaming|^input-gamepad|^gamepad', 'gamepad'),
 (r'^preferences-desktop-notification|^notification|^bell', 'bell'),
 (r'^help-about|^dialog-information|^help-hint|^emblem-information|^info|^help-info', 'circle-info'),
 (r'^help-contents|^help$|^dialog-question|^help-browser|^system-help', 'circle-question'),
 (r'^dialog-warning|^emblem-warning|^data-warning|^task-attention', 'warning-diamond'),
 (r'^dialog-error|^emblem-error|^data-error|^task-reject|^process-error', 'square-alert'),
 (r'^media-playback-start|^player-play|^media-play', 'play'), (r'^media-playback-pause|^player-pause', 'pause'),
 (r'^media-playback-stop|^player-stop|^media-stop', 'stop'),
 (r'^media-skip-forward|^media-seek-forward|^media-skip-next', 'forward'),
 (r'^media-skip-backward|^media-seek-backward|^media-skip-previous', 'forward!'),
 (r'^media-record|^media-recording', 'circle'), (r'^media-eject', 'arrow-bar-up'),
 (r'^media-playlist-repeat|^media-repeat', 'repeat'), (r'^media-playlist-shuffle', 'shuffle'),
 (r'^audio-volume-(high|overamplified)', 'volume-3'), (r'^audio-volume-medium', 'volume-2'), (r'^audio-volume-low', 'volume-1'),
 (r'^audio-volume-(muted|off)', 'volume-x'), (r'^(audio-input-microphone-muted|microphone-sensitivity-muted|mic-off)', 'mic-off'),
 (r'^audio-input-microphone|^microphone|^mic', 'mic'), (r'^audio-headphones|^audio-headset|^headphone', 'headphone'),
 (r'^audio-card|^audio-speakers|^speaker|^audio-output', 'volume-2'), (r'^audio', 'music'),
 (r'^network-wireless-(disconnected|offline|none|0$)|^network-wireless-signal-none|^network-wireless-off', 'wifi~'),
 (r'^network-wireless-(signal-weak|[1-3]\d$|[0-2]\d$)|^network-wireless-(connecting|acquiring)', 'wifi~'),
 (r'^network-wireless|^network-wifi|^wifi|^network-connect$', 'wifi'),
 (r'^network-wired|^network-ethernet|^network-card|^network-modem', 'modem'),
 (r'^network-disconnect|^network-offline|^network-error|^network-unavailable|^network-wired-disconnected|^network-wired-unavailable', 'unlink'),
 (r'^network-vpn|^network-server|^network-workgroup|^network-defaultroute|^preferences-system-network|^network-transmit|^network|^applications-internet|^internet', 'globe'),
 (r'^bluetooth|^preferences-system-bluetooth', 'signal'),
 (r'^power-profile-performance', 'speed-fast'), (r'^power-profile-balanced', 'speed-medium'), (r'^power-profile-(power-saver|powersave)', 'leaf'),
 (r'^(display-brightness|brightness|weather-clear$)', 'sun'), (r'^weather-few-clouds|^weather-clouds-night', 'cloud-sun'),
 (r'^weather-(clouds|overcast|showers|rain|fog|mist)', 'cloud'), (r'^weather-snow', 'snowflake'), (r'^weather-storm', 'zap'),
 (r'^mail-send', 'send'), (r'^mail-reply', 'message-reply'), (r'^mail-attach|^attachment', 'attachment'), (r'^mail|^message-new|^kmail', 'mail'),
 (r'^bookmark|^user-bookmarks', 'bookmark'), (r'^emblem-favorite|^favorite|^starred|^rating|^non-starred|^star', 'star'),
 (r'^emblem-important|^flag', 'flag'), (r'^emblem-shared|^document-share|^emblem-share|^system-share|^share', 'share'),
 (r'^insert-link|^link$|^emblem-symbolic-link|^emblem-link', 'link'),
 (r'^user-identity|^user-info|^user-available|^user$|^avatar|^im-user|^user-', 'user'),
 (r'^drive-removable-media|^media-removable|^usb|^drive-removable', 'usb'), (r'^drive-optical|^media-optical|^media-cdrom|^media-dvd|^drive-cdrom', 'album'),
 (r'^drive-harddisk|^drive-multidisk|^drive-partition|^harddrive|^disk', 'database'), (r'^media-flash|^media-sdcard|^sd-card|^drive-flash', 'memory-stick'),
 (r'^computer-laptop|^laptop|^computer-apple', 'laptop'), (r'^computer|^system$|^pc$', 'computer'),
 (r'^phone|^smartphone|^multimedia-player|^kdeconnect', 'smartphone'), (r'^tablet', 'tablet'), (r'^camera|^photo', 'camera'),
 (r'^video-camera|^webcam', 'webcam'), (r'^scanner', 'printer'), (r'^uninterruptible-power|^plug', 'plug'),
 (r'^cpu|^chip', 'cpu'), (r'^gpu|^video-card', 'gpu'), (r'^memory|^ram$', 'memory-stick'), (r'^thermometer|^temperature', 'thermometer'),
 (r'^tools-wizard|^wand|^autocorrect', 'wand'), (r'^security-|^shield', 'shield'), (r'^dialog-password|^password|^key', 'key'),
 (r'^edit-image|^image|^viewimage', 'image'), (r'^video|^film', 'video'), (r'^text|^document-properties', 'file-text'),
 (r'^overflow-menu|^open-menu|^application-menu|^view-more|^menu', 'menu'), (r'^application-exit', 'power'),
]
REGLAS = [(re.compile(r), g) for r, g in REGLAS]
SUFIJOS = re.compile(r'(-symbolic)?(-rtl)?$')

def casa(nombre):
    base = SUFIJOS.sub('', nombre)
    for rx, g in REGLAS:
        if rx.search(base): return g
    return None

def bateria(nombre):
    m = re.match(r'^battery-(\d+)(-charging)?|^battery-(full|good|low|caution|empty|missing)(-charging)?', nombre)
    if not m: return None
    if m.group(1) is not None: n = int(m.group(1)); carga = bool(m.group(2))
    else: n = {'full': 100, 'good': 70, 'low': 25, 'caution': 10, 'empty': 0, 'missing': 0}[m.group(3)]; carga = bool(m.group(4))
    g = 'battery-full' if n >= 80 else 'battery-medium' if n >= 45 else 'battery-low' if n >= 15 else 'battery'
    if 'missing' in nombre: return mono(['battery'], op=0.4)
    s = mono([g])
    if carga and s:
        z = glifo_d('zap')
        s = s.replace('</svg>', f'<g transform="translate(6,6) scale(0.5)">\n<path fill="#05061a" d="{z}" transform="translate(1,1)"/><path fill="#e0b36a" d="{z}"/></g>\n</svg>')
    return s

# ----------------------------------------------------------------------- apps (azulejos)
APPS = [  # regex sobre el nombre del icono / archivo -> (glifo, color)
 (r'brave|chrom|firefox|vivaldi|librewolf|zen|web-browser|epiphany|falkon|qutebrowser', ('globe', '#d9602f')),
 (r'dolphin|file-manager|nautilus|thunar|nemo|pcmanfm|krusader|ranger', ('files', '#6a4a9a')),
 (r'konsole|alacritty|kitty|terminal|foot|wezterm|xterm|ghostty|tilix|yakuake', ('terminal', '#14183f')),
 (r'kate|kwrite|text-editor|gedit|micro|nano|neovim|vim|helix|emacs', ('pencil', '#2f7a86')),
 (r'code|vscod|cursor|jetbrains|idea|pycharm|clion|zed|sublime', ('code', '#2f64b8')),
 (r'systemsettings|preferences-system|kcm_|settings', ('settings-cog', '#4a5a8a')),
 (r'systemmonitor|system-monitor|ksysguard|btop|htop|resources|mission', ('analytics', '#3a7a4a')),
 (r'spectacle|screenshot|flameshot|screencast|obs', ('camera', '#b95e7c')),
 (r'discover|software|pamac|octopi|packagekit|appcenter', ('shopping-bag', '#3a64b8')),
 (r'obsidian|notes|joplin|logseq|notebook', ('notebook', '#6a3fa0')),
 (r'syncthing', ('refresh', '#2f78b8')), (r'discord', ('discord', '#5a62c8')), (r'telegram', ('telegram', '#2f86b8')),
 (r'whatsapp', ('whatsapp', '#2f9a5a')), (r'claude|anthropic', ('sparkles', '#c8662e')), (r'signal|element|matrix', ('message', '#2f7ab8')),
 (r'steam|lutris|heroic|game|minecraft|prism', ('gamepad', '#3a4a7a')),
 (r'vlc|mpv|haruna|celluloid|totem|video|kdenlive|shotcut', ('play', '#c86a2e')),
 (r'elisa|music|spotify|rhythmbox|audacious|amarok|strawberry|deadbeef', ('music', '#b9487c')),
 (r'gwenview|image|photo|krita|gimp|inkscape|digikam|shotwell|blender', ('image', '#3a8a7a')),
 (r'okular|evince|document-viewer|pdf|zathura|foliate|calibre', ('article', '#b8402e')),
 (r'libreoffice|office|onlyoffice|writer|calc|impress', ('article', '#2f64b8')), (r'calculator|kcalc|galculator', ('calculator', '#b8862e')),
 (r'kdeconnect|phone', ('smartphone', '#2f9a7a')), (r'qemu|virt|virtualbox|vmware|boxes|vm', ('server', '#5a4a9a')),
 (r'docker|podman|container', ('docker', '#2f78b8')), (r'wireshark', ('analytics', '#2f6ab8')), (r'nmap|zenmap', ('compass', '#b83a3a')),
 (r'burp|zaproxy|sqlmap|metasploit|hydra|john|hashcat', ('bug', '#8a2a3a')), (r'git|github|gitg|lazygit|gitk', ('git-branch', '#c8602e')),
 (r'mail|thunderbird|kmail|evolution|geary', ('mail', '#2f6ab8')), (r'calendar|korganizer|kalendar', ('calendar', '#b8602e')),
 (r'weather|kweather', ('cloud-sun', '#3a8ab8')), (r'clock|alarm|timer|kclock', ('clock', '#5a4a9a')), (r'ark|archive|zip|file-roller|peazip', ('archive', '#8a6a2e')),
 (r'cachyos|hello|arch|manjaro|start-here|distributor|kickoff|menu', ('menu', '#8a4a79')), (r'bluetooth|blueman|bluedevil', ('signal', '#2f6ab8')),
 (r'network|nm-|wifi|connection', ('wifi', '#2f7a86')), (r'printer|cups|hplip', ('printer', '#5a5a7a')), (r'kwallet|bitwarden|keepass|password|keyring', ('key', '#b8862e')),
 (r'timeshift|backup|deja|restic|borg|snapper', ('database', '#3a7a6a')), (r'translate|dictionary', ('languages', '#2f6ab8')),
]
CAT = {'Development': ('code', '#2f64b8'), 'Network': ('globe', '#2f7a86'), 'AudioVideo': ('play', '#c86a2e'), 'Audio': ('music', '#b9487c'),
       'Video': ('video', '#c86a2e'), 'Graphics': ('image', '#3a8a7a'), 'Office': ('article', '#2f64b8'), 'Utility': ('tools', '#5a5a8a'),
       'System': ('cpu', '#4a5a8a'), 'Game': ('gamepad', '#3a4a7a'), 'Settings': ('settings-cog', '#4a5a8a'), 'Education': ('teach', '#2f9a7a'),
       'Science': ('test-tube', '#2f9a7a'), 'TextEditor': ('pencil', '#2f7a86'), 'FileManager': ('files', '#6a4a9a'), 'TerminalEmulator': ('terminal', '#14183f')}
APPS = [(re.compile(r, re.I), v) for r, v in APPS]

def escoge_app(nombre, cats=()):
    for rx, v in APPS:
        if rx.search(nombre): return v
    for c in cats:
        if c in CAT: return CAT[c]
    return ('blocks', '#4a4a7a')

def iconos_de_apps():
    hallados = {}
    for f in glob.glob('/usr/share/applications/*.desktop') + glob.glob(os.path.expanduser('~/.local/share/applications/*.desktop')) + \
             glob.glob('/var/lib/flatpak/exports/share/applications/*.desktop'):
        cp = configparser.RawConfigParser(strict=False, interpolation=None)
        try: cp.read(f, encoding='utf-8')
        except Exception: continue
        if not cp.has_section('Desktop Entry'): continue
        ic = cp.get('Desktop Entry', 'Icon', fallback='')
        if not ic or ic.startswith('/'): continue
        cats = [c for c in cp.get('Desktop Entry', 'Categories', fallback='').split(';') if c]
        hallados.setdefault(ic, cats)
    return hallados

# ----------------------------------------------------------------------- lugares y tipos de archivo
CARPETAS = {'folder': None, 'folder-documents': 'file-text', 'folder-download': 'download', 'folder-downloads': 'download', 'folder-music': 'music',
            'folder-pictures': 'image', 'folder-videos': 'video', 'folder-video': 'video', 'folder-desktop': 'monitor', 'folder-templates': 'article',
            'folder-public': 'globe', 'folder-publicshare': 'globe', 'folder-remote': 'cloud', 'folder-network': 'globe', 'folder-favorites': 'star',
            'folder-bookmark': 'bookmark', 'folder-cloud': 'cloud', 'folder-git': 'git-branch', 'folder-code': 'code', 'folder-projects': 'briefcase',
            'folder-games': 'gamepad', 'folder-activities': 'sparkles', 'folder-locked': 'lock', 'folder-important': 'flag', 'folder-development': 'code',
            'user-home': 'home', 'folder-home': 'home', 'inode-directory': None, 'folder-script': 'terminal', 'folder-tar': 'archive'}
MIMES = [  # regex -> (glifo, color)
 (r'^application-pdf', ('article', '#b8402e')), (r'^image-', ('image', '#3a8a7a')), (r'^audio-', ('music', '#b9487c')), (r'^video-', ('video', '#c86a2e')),
 (r'zip|tar|rar|7z|archive|compressed|bzip|xz|gzip|^application-x-cd', ('archive', '#8a6a2e')),
 (r'python', ('snake', '#2f64b8')), (r'html|xml|xhtml', ('globe', '#d9602f')), (r'json|yaml|toml|ini|conf', ('braces', '#6a4a9a')),
 (r'markdown|text-x-readme|rst', ('notes', '#2f7a86')), (r'shellscript|x-script|text-x-sh|bash', ('terminal', '#3a7a4a')),
 (r'text-x-(c|cpp|csrc|chdr|java|rust|go|javascript|typescript|php|ruby|perl|lua)|application-javascript|x-source|x-code|text-css', ('code', '#2f64b8')),
 (r'spreadsheet|ods|xls|csv', ('grid-3x3', '#2f9a5a')), (r'presentation|odp|ppt', ('presentation', '#c86a2e')),
 (r'word|odt|office-document|x-office-document|msword|rtf|document', ('article', '#2f64b8')),
 (r'executable|x-elf|x-sharedlib|x-pie', ('cpu', '#5a5a8a')), (r'font', ('letter-a', '#6a4a9a')), (r'torrent', ('download', '#2f78b8')),
 (r'ebook|epub|mobi', ('book-open', '#8a4a79')), (r'database|sql|sqlite', ('database', '#3a7a6a')), (r'certificate|pgp|ssh|key', ('key', '#b8862e')),
 (r'text-plain|text-x-generic|^text-', ('file-text', '#6a6a9a')), (r'^unknown|^application-octet|^application-x-generic', ('file', '#6a6a9a')),
]
MIMES = [(re.compile(r), v) for r, v in MIMES]

def lista_breeze(ctx):
    nombres = set()
    for f in glob.glob(f'{BREEZE}/{ctx}/*/*.svg'): nombres.add(os.path.basename(f)[:-4])
    return sorted(nombres)

def construir():
    shutil.rmtree(OUT, ignore_errors=True)
    n = dict(mono=0, tile=0, carp=0, hoja=0)
    # acciones, estado, dispositivos, emblemas, lugares sueltos
    for ctx in ('actions', 'status', 'devices', 'emblems', 'applets', 'preferences', 'animations'):
        for nombre in lista_breeze(ctx):
            s = bateria(nombre) if nombre.startswith('battery') else None
            if s is None:
                g = casa(nombre)
                if not g: continue
                flip = g.endswith('!'); op = 0.5 if g.endswith('~') else 1.0
                s = mono([g.rstrip('!~')], flip=flip, op=op)
            if s:
                escribe(f'{OUT}/scalable/{ctx}/{nombre}.svg', s); n['mono'] += 1
    # lugares: carpetas coloreadas + basura + el resto por reglas
    for nombre in lista_breeze('places') + list(CARPETAS):
        if nombre in CARPETAS or nombre.startswith('folder'):
            g = CARPETAS.get(nombre)
            if g is None and nombre not in CARPETAS:
                m = re.sub(r'^folder-', '', nombre); g = casa(m) or casa(nombre)
            escribe(f'{OUT}/scalable/places/{nombre}.svg', carpeta(g)); n['carp'] += 1
            if nombre == 'folder': escribe(f'{OUT}/scalable/places/folder-open.svg', carpeta(None, True)); n['carp'] += 1
            continue
        if nombre.startswith('user-trash'):
            s = mono(['trash']); s = s.replace('</svg>', '<rect x="9" y="3" width="6" height="2" fill="#e0837f"/></svg>') if 'full' in nombre else s
            escribe(f'{OUT}/scalable/places/{nombre}.svg', s); n['mono'] += 1; continue
        g = casa(nombre)
        if g:
            s = mono([g.rstrip('!~')], flip=g.endswith('!'))
            if s: escribe(f'{OUT}/scalable/places/{nombre}.svg', s); n['mono'] += 1
    # mimetypes
    for nombre in lista_breeze('mimetypes'):
        if nombre.startswith('inode-directory'):
            escribe(f'{OUT}/scalable/mimetypes/{nombre}.svg', carpeta(None)); n['carp'] += 1; continue
        for rx, (g, c) in MIMES:
            if rx.search(nombre):
                escribe(f'{OUT}/scalable/mimetypes/{nombre}.svg', hoja(g, c)); n['hoja'] += 1; break
    # categorias de menu
    cat = {'applications-accessories': ('tools', '#5a5a8a'), 'applications-development': ('code', '#2f64b8'), 'applications-education': ('teach', '#2f9a7a'),
           'applications-games': ('gamepad', '#3a4a7a'), 'applications-graphics': ('image', '#3a8a7a'), 'applications-internet': ('globe', '#2f7a86'),
           'applications-multimedia': ('play', '#c86a2e'), 'applications-office': ('article', '#2f64b8'), 'applications-other': ('blocks', '#4a4a7a'),
           'applications-science': ('test-tube', '#2f9a7a'), 'applications-system': ('cpu', '#4a5a8a'), 'applications-utilities': ('tools', '#5a5a8a'),
           'preferences-other': ('settings-cog', '#4a5a8a'), 'preferences-system': ('settings-cog', '#4a5a8a'), 'applications-all': ('grid-2x2-2', '#6a4a9a')}
    for nombre, (g, c) in cat.items():
        escribe(f'{OUT}/scalable/categories/{nombre}.svg', azulejo(g, c)); n['tile'] += 1
    # apps: todos los iconos que piden tus .desktop + los de breeze
    apps = iconos_de_apps()
    for nombre in lista_breeze('apps'): apps.setdefault(nombre, [])
    for nombre, cats in apps.items():
        g, c = escoge_app(nombre, cats)
        escribe(f'{OUT}/scalable/apps/{nombre}.svg', azulejo(g, c, '#7fe0a0' if g == 'terminal' else WASHI)); n['tile'] += 1
    # propios: boton de inicio (torii)
    for nombre in ('pixelzen-inicio', 'start-here-kde', 'start-here-kde-plasma', 'start-here', 'org.cachyos.hello', 'distributor-logo-cachyos', 'cachyos'):
        escribe(f'{OUT}/scalable/apps/{nombre}.svg', torii()); n['tile'] += 1
    dirs = ['scalable/' + c for c in ('actions', 'apps', 'categories', 'devices', 'emblems', 'mimetypes', 'places', 'status', 'applets', 'preferences', 'animations')]
    idx = ['[Icon Theme]', 'Name=PixelZen', 'Comment=Iconos pixel art para PixelZen (glifos Pixelarticons, MIT)', 'Inherits=breeze-dark,breeze,hicolor',
           'FollowsColorScheme=true', 'DisplayDepth=32', 'Example=folder', 'Directories=' + ','.join(dirs), '']
    ctxs = {'actions': 'Actions', 'apps': 'Applications', 'categories': 'Categories', 'devices': 'Devices', 'emblems': 'Emblems', 'mimetypes': 'MimeTypes',
            'places': 'Places', 'status': 'Status', 'applets': 'Applications', 'preferences': 'Applications', 'animations': 'Animations'}
    for d in dirs:
        c = d.split('/')[1]
        idx += [f'[{d}]', 'Size=32', 'MinSize=8', 'MaxSize=512', 'Type=Scalable', f'Context={ctxs[c]}', '']
    escribe(f'{OUT}/index.theme', '\n'.join(idx))
    return n

if __name__ == '__main__':
    print(construir())
