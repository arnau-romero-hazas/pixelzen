#!/usr/bin/env python3
"""PixelZen - ubicacion sin red. Casa fija (config) si la zona horaria es la de casa; si no, el punto de la zona horaria (zone1970.tab)."""
import json, os, re, subprocess
CFG = os.path.expanduser('~/.config/pixelzen/ubicacion.json')

def zona():
    try:
        z = subprocess.run(['timedatectl', 'show', '-p', 'Timezone', '--value'], capture_output=True, text=True, timeout=2).stdout.strip()
        if z: return z
    except Exception: pass
    try: return os.path.realpath('/etc/localtime').split('zoneinfo/')[1]
    except Exception: return ''

def iso6709(s):
    m = re.match(r'([+-])(\d{2})(\d{2})(\d{2})?([+-])(\d{3})(\d{2})(\d{2})?$', s)
    if not m: return None
    la = int(m[2]) + int(m[3]) / 60 + int(m[4] or 0) / 3600; lo = int(m[6]) + int(m[7]) / 60 + int(m[8] or 0) / 3600
    return (la if m[1] == '+' else -la, lo if m[5] == '+' else -lo)

def busca(tz):
    for f in ('/usr/share/zoneinfo/zone1970.tab', '/usr/share/zoneinfo/zone.tab'):
        try:
            for l in open(f):
                if l.startswith('#'): continue
                c = l.rstrip('\n').split('\t')
                if len(c) >= 3 and tz in c[2].split(',') + [c[2]]:
                    r = iso6709(c[1])
                    if r: return r
        except Exception: pass
    return None

try: cfg = json.load(open(CFG))
except Exception: cfg = {}
casa = cfg.get('casa'); tz = zona()
if casa and (not tz or tz == casa.get('tz')):
    out = {'lat': casa['lat'], 'lon': casa['lon'], 'origen': 'casa: ' + casa.get('nombre', ''), 'tz': tz}
else:
    r = busca(tz) if tz else None
    out = {'lat': r[0], 'lon': r[1], 'origen': 'zona horaria ' + tz, 'tz': tz} if r else {'lat': 40.4, 'lon': -3.7, 'origen': 'por defecto (Madrid)', 'tz': tz}
print(json.dumps(out))
