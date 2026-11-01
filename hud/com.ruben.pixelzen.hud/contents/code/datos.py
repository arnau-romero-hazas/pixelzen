#!/usr/bin/env python3
"""PixelZen HUD - motor de datos. Solo lectura, sin red, sin sudo.
  datos.py rapido  -> CPU, RAM, temperatura, bateria, red (cada ~2 s)
  datos.py lento   -> puertos, repos git, servicios, herramientas (cada ~20 s)
Salida: JSON por stdout."""
import glob, json, os, re, shutil, subprocess, sys, time

MODO = sys.argv[1] if len(sys.argv) > 1 else 'rapido'
ETQ = sys.argv[2] if len(sys.argv) > 2 else 'hud'
ESTADO = os.path.join(os.environ.get('XDG_RUNTIME_DIR', '/tmp'), f'pixelzen-{ETQ}-{MODO}.json')

def sh(cmd, t=2):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=t).stdout
    except Exception:
        return ''

def leer(p, d=''):
    try:
        return open(p).read().strip()
    except Exception:
        return d

def carga_estado():
    try: return json.load(open(ESTADO))
    except Exception: return {}

def guarda_estado(e):
    try: json.dump(e, open(ESTADO, 'w'))
    except Exception: pass

# ----------------------------------------------------------------- rapido
def cpu_pct(e):
    v = [int(x) for x in open('/proc/stat').readline().split()[1:9]]
    idle, total = v[3] + v[4], sum(v)
    ant = e.get('cpu')
    e['cpu'] = [idle, total]
    if not ant or total == ant[1]: return 0.0
    return round(100.0 * (1 - (idle - ant[0]) / (total - ant[1])), 1)

def memoria():
    m = {}
    for l in open('/proc/meminfo'):
        k, v = l.split(':'); m[k] = int(v.split()[0])
    tot, disp = m['MemTotal'], m['MemAvailable']
    sw = m.get('SwapTotal', 0)
    return dict(pct=round(100.0 * (tot - disp) / tot, 1), usado=round((tot - disp) / 1048576, 1), total=round(tot / 1048576, 1),
                swap=round(100.0 * (sw - m.get('SwapFree', 0)) / sw, 1) if sw else 0)

def temperatura():
    for h in glob.glob('/sys/class/hwmon/hwmon*'):
        if leer(h + '/name') in ('k10temp', 'coretemp', 'zenpower'):
            t = leer(h + '/temp1_input')
            if t: return round(int(t) / 1000.0, 1)
    for t in glob.glob('/sys/class/thermal/thermal_zone*/temp'):
        v = leer(t)
        if v: return round(int(v) / 1000.0, 1)
    return None

def bateria():
    for b in glob.glob('/sys/class/power_supply/BAT*'):
        cap = int(leer(b + '/capacity', '0')); est = leer(b + '/status')
        try:
            pw = int(leer(b + '/power_now', '0')); en = int(leer(b + '/energy_now', '0')); ef = int(leer(b + '/energy_full', '0'))
            if pw > 0:
                horas = (en / pw) if est == 'Discharging' else ((ef - en) / pw if est == 'Charging' else 0)
                minutos = int(horas * 60)
            else: minutos = 0
            watts = round(pw / 1e6, 1)
        except Exception: minutos, watts = 0, 0
        return dict(pct=cap, estado=est, min=minutos, w=watts)
    return None

def red(e):
    r = sh(['ip', '-o', 'route', 'show', 'default']); m = re.search(r'dev (\S+)', r); iface = m.group(1) if m else None
    gw = re.search(r'via (\S+)', r)
    out = dict(iface=iface, ip=None, ssid=None, senal=None, rx=0, tx=0, gw=gw.group(1) if gw else None, vpn=dict(on=False, iface=None, ip=None))
    ahora = time.time()
    if iface:
        a = sh(['ip', '-o', '-4', 'addr', 'show', iface]); m = re.search(r'inet (\S+?)/', a); out['ip'] = m.group(1) if m else None
        try:
            rx = int(leer(f'/sys/class/net/{iface}/statistics/rx_bytes', '0')); tx = int(leer(f'/sys/class/net/{iface}/statistics/tx_bytes', '0'))
            ant = e.get('net')
            if ant and ant[0] == iface and ahora > ant[3]:
                dt = ahora - ant[3]; out['rx'] = max(0, int((rx - ant[1]) / dt)); out['tx'] = max(0, int((tx - ant[2]) / dt))
            e['net'] = [iface, rx, tx, ahora]
        except Exception: pass
        if os.path.exists(f'/sys/class/net/{iface}/wireless'):
            l = sh(['iw', 'dev', iface, 'link'])
            m = re.search(r'SSID: (.+)', l); out['ssid'] = m.group(1).strip() if m else None
            m = re.search(r'signal: (-?\d+) dBm', l)
            if m: out['senal'] = max(0, min(100, 2 * (int(m.group(1)) + 100)))
    for v in sorted(os.listdir('/sys/class/net')):
        if re.match(r'(tailscale|tun|wg|proton|nordlynx|vpn)', v) and leer(f'/sys/class/net/{v}/operstate') != 'down':
            a = sh(['ip', '-o', '-4', 'addr', 'show', v]); m = re.search(r'inet (\S+?)/', a)
            out['vpn'] = dict(on=True, iface=v, ip=m.group(1) if m else None); break
    return out

def rapido():
    e = carga_estado()
    top = []
    for l in sh(['ps', '-eo', 'comm,%cpu', '--sort=-%cpu', '--no-headers'], 2).splitlines()[:6]:
        p = l.rsplit(None, 1)
        if len(p) == 2 and p[0] not in ('ps', 'python3') and len(top) < 3: top.append([p[0], float(p[1])])
    du = shutil.disk_usage('/')
    d = dict(t=int(time.time()), cpu=cpu_pct(e), ram=memoria(), temp=temperatura(), bat=bateria(), net=red(e),
             load=[float(x) for x in leer('/proc/loadavg').split()[:3]], up=int(float(leer('/proc/uptime', '0').split()[0])),
             disco=round(100.0 * du.used / du.total, 1), libre=round(du.free / 2 ** 30), top=top, nuc=os.cpu_count())
    guarda_estado(e); return d

# ----------------------------------------------------------------- lento
PUERTOS = {22: 'ssh', 53: 'dns', 80: 'http', 443: 'https', 631: 'cups', 3000: 'dev', 3306: 'mysql', 5000: 'dev', 5173: 'vite', 5432: 'pg',
           6379: 'redis', 8000: 'dev', 8080: 'http', 8888: 'jupyter', 9090: 'prom', 27017: 'mongo', 1716: 'kdeconn', 5900: 'vnc'}
def puertos():
    vistos = {}
    for l in sh(['ss', '-tlnpH']).splitlines():
        c = l.split()
        if len(c) < 5: continue
        m = re.search(r':(\d+)$', c[3]);
        if not m: continue
        p = int(m.group(1)); host = c[3].rsplit(':', 1)[0]
        pr = re.search(r'\(\("([^"]+)"', l)
        loc = host in ('127.0.0.1', '[::1]', '127.0.0.53%lo', '127.0.0.54')
        if p not in vistos: vistos[p] = dict(p=p, n=(pr.group(1) if pr else PUERTOS.get(p, '')), local=loc)
        elif not loc: vistos[p]['local'] = False
    return sorted(vistos.values(), key=lambda x: x['p'])[:24]

def repos(e):
    ahora = time.time()
    if e.get('repos_t', 0) < ahora - 600:
        raices = [os.path.expanduser(p) for p in ('~/proyectos', '~/dev', '~/code', '~/src', '~/projects', '~/git', '~/Documentos', '~/Obsidian', '~/Escritorio')]
        encontrados = []
        for r in raices:
            if not os.path.isdir(r): continue
            for dp, dn, _ in os.walk(r):
                if dp[len(r):].count(os.sep) >= 3: dn[:] = []; continue
                if '.git' in dn: encontrados.append(dp); dn[:] = []
                else: dn[:] = [x for x in dn if not x.startswith('.') and x not in ('node_modules', 'venv', '.venv', 'target')]
        e['repos_l'] = encontrados[:8]; e['repos_t'] = ahora
    out = []
    for r in e.get('repos_l', []):
        b = sh(['git', '-C', r, 'rev-parse', '--abbrev-ref', 'HEAD']).strip()
        if not b: continue
        st = sh(['git', '-C', r, 'status', '--porcelain']).splitlines()
        ab = sh(['git', '-C', r, 'rev-list', '--left-right', '--count', '@{u}...HEAD']).split()
        out.append(dict(n=os.path.basename(r), b=b, sucio=len(st), atras=int(ab[0]) if len(ab) == 2 else 0, adelante=int(ab[1]) if len(ab) == 2 else 0))
    return out[:3]

def version(cmd, args=('--version',)):
    if not shutil.which(cmd): return None
    o = sh([cmd, *args], 2).strip() or ''
    m = re.search(r'(\d+\.\d+(?:\.\d+)?)', o); return m.group(1) if m else '?'

def edad_pacman():
    try: return int((time.time() - os.path.getmtime('/var/lib/pacman/sync/core.db')) / 3600)
    except Exception: return None

def lento():
    e = carga_estado()
    fallos = len([l for l in sh(['systemctl', '--failed', '--no-legend', '--plain'], 3).splitlines() if l.strip()])
    fallos += len([l for l in sh(['systemctl', '--user', '--failed', '--no-legend', '--plain'], 3).splitlines() if l.strip()])
    errores = len([l for l in sh(['journalctl', '-p', '3', '-S', '-1h', '--no-pager', '-q'], 4).splitlines() if l.strip()])
    est = len(sh(['ss', '-tnH', 'state', 'established']).splitlines())
    vecinos = len([l for l in sh(['ip', 'neigh']).splitlines() if 'REACHABLE' in l or 'STALE' in l or 'DELAY' in l])
    dns = re.search(r'nameserver (\S+)', leer('/etc/resolv.conf'))
    tools = {t: bool(shutil.which(t)) for t in ('btop', 'fastfetch', 'nmap', 'wireshark', 'tcpdump', 'docker', 'podman', 'dig', 'mtr', 'ncat', 'git', 'ranger', 'yazi')}
    d = dict(puertos=puertos(), est=est, vecinos=vecinos, dns=dns.group(1) if dns else None, repos=repos(e), fallos=fallos, errores=errores,
             tc=dict(py=version('python3'), node=version('node'), go=version('go', ('version',)), rust=version('rustc'), docker=version('docker')),
             tools=tools, pacman_h=edad_pacman(), kernel=os.uname().release.split('-')[0], host=os.uname().nodename)
    guarda_estado(e); return d

DEMO = os.path.exists(os.path.expanduser('~/.config/pixelzen/demo'))
def anonimiza(d, modo):
    """Con el fichero ~/.config/pixelzen/demo los datos personales se sustituyen por otros ficticios (para capturas)."""
    if modo == 'rapido':
        n = d['net']; n['ssid'] = 'MiWiFi' if n.get('ssid') else None; n['ip'] = '192.168.1.42' if n.get('ip') else None; n['gw'] = '192.168.1.1' if n.get('gw') else None
        if n['vpn'].get('on'): n['vpn']['ip'] = '100.64.0.7'
    else:
        d['host'] = 'pixelzen'; d['dns'] = '1.1.1.1'
        d['repos'] = [dict(n='pixelzen', b='main', sucio=2, atras=0, adelante=1), dict(n='blog', b='dev', sucio=0, atras=0, adelante=0)]
    return d

if __name__ == '__main__':
    modo = sys.argv[1] if len(sys.argv) > 1 else 'rapido'
    r = lento() if modo == 'lento' else rapido()
    print(json.dumps(anonimiza(r, modo) if DEMO else r, ensure_ascii=False))
