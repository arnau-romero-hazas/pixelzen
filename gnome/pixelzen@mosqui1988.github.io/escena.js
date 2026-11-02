// PixelZen para GNOME - fondo animado.
// Traduccion directa de fondo-animado/.../ui/main.qml (Plasma) a GNOME Shell.
// Toda la escena vive en un lienzo de 640x400 "pixeles de arte" que se escala con filtro
// NEAREST, asi que las coordenadas y las formulas son las mismas que en el QML original.

import GLib from 'gi://GLib';
import GdkPixbuf from 'gi://GdkPixbuf';
import Clutter from 'gi://Clutter';
import Cogl from 'gi://Cogl';
import St from 'gi://St';
import Cairo from 'cairo';

const W = 640, H = 400;

// ---------------------------------------------------------------- utilidades de color y actores
const cacheColor = new Map();
function hexA(hex) {
    const h = hex.replace('#', '');
    return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
}
// GNOME 46 usa Clutter.Color; desde GNOME 47 set_background_color recibe Cogl.Color.
export function color(hex, alpha = 255) {
    const k = hex + alpha;
    if (cacheColor.has(k)) return cacheColor.get(k);
    const [red, green, blue] = hexA(hex);
    const C = Clutter.Color ?? Cogl.Color;
    const c = new C({red, green, blue, alpha});
    cacheColor.set(k, c);
    return c;
}

const clamp01 = v => v < 0 ? 0 : v > 1 ? 1 : v;
const op255 = v => Math.round(clamp01(v) * 255);

// Pixel de arte (equivalente a Px.qml) pintado con Cairo en coordenadas de 640x400
const cacheRgb = new Map();
function px(cr, hex, op, ax, ay, aw = 1, ah = 1) {
    if (op <= 0.004) return;
    let c = cacheRgb.get(hex);
    if (!c) { c = hexA(hex).map(v => v / 255); cacheRgb.set(hex, c); }
    cr.setSourceRGBA(c[0], c[1], c[2], op > 1 ? 1 : op);
    cr.rectangle(Math.round(ax), Math.round(ay), aw, ah);
    cr.fill();
}
// opacidad de un actor grande; lo oculta si es casi transparente. Devuelve si queda visible.
function fija(a, op) {
    const o = op255(op);
    const v = o > 1;
    if (a.visible !== v) a.visible = v;
    if (v && a.opacity !== o) a.opacity = o;
    return v;
}

// ---------------------------------------------------------------- texturas
function contenido(pixbuf) {
    const c = St.ImageContent.new_with_preferred_size(pixbuf.width, pixbuf.height);
    const fmt = pixbuf.has_alpha ? Cogl.PixelFormat.RGBA_8888 : Cogl.PixelFormat.RGB_888;
    const bytes = pixbuf.read_pixel_bytes();
    try {
        c.set_bytes(bytes, fmt, pixbuf.width, pixbuf.height, pixbuf.rowstride);
    } catch (e) {
        // GNOME 47+: set_bytes recibe primero el contexto de Cogl
        const ctx = global.stage.context.get_backend().get_cogl_context();
        c.set_bytes(ctx, bytes, fmt, pixbuf.width, pixbuf.height, pixbuf.rowstride);
    }
    return c;
}
function imagen(padre, cont, w, h) {
    const a = new Clutter.Actor({width: w, height: h});
    a.set_content(cont);
    a.set_content_scaling_filters(Clutter.ScalingFilter.NEAREST, Clutter.ScalingFilter.NEAREST);
    padre.add_child(a);
    return a;
}

// LCG del QML (mismas semillas -> mismas olas y petalos)
function lcg(seed) {
    let s = seed;
    return () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
}

const ALAS = [
    [[-5, -2], [-4, -2], [-3, -1], [-2, -1], [-1, 0], [0, 0], [1, 0], [2, -1], [3, -1], [4, -2], [5, -2]],
    [[-5, 1], [-4, 1], [-3, 1], [-2, 0], [-1, 0], [0, 0], [1, 0], [2, 0], [3, 1], [4, 1], [5, 1]],
    [[-5, 2], [-4, 1], [-3, 1], [-2, 0], [-1, 0], [0, 1], [1, 0], [2, 0], [3, 1], [4, 1], [5, 2]]];
const COL_PETALO = ['#f7cfdb', '#eda0b8', '#fdeff3'];
const LUCIERNAGAS = [[70, 300], [95, 330], [130, 290], [565, 310], [590, 340], [20, 345], [470, 296], [160, 355], [248, 318], [520, 352]];

// ================================================================= Escena
export class Escena {
    constructor(dir, contenedor, settings) {
        this._dir = dir;
        this._cont = contenedor;
        this._settings = settings;
        this._monitores = [];
        this._timer = 0;
        this._pausa = false;
        this.tick = 0;

        // ubicacion por defecto hasta que responda ubicacion.py
        this.lat = 40.4; this.lon = -3.7;

        this.D = JSON.parse(new TextDecoder().decode(
            GLib.file_get_contents(`${dir}/datos.json`)[1]));
        this.brillantes = this.D.estrellas.filter(e => e[3] === 1);

        let n = lcg(7);
        this.olas = [];
        for (let i = 0; i < 44; i++)
            this.olas.push([300 + Math.floor(n() * 260), 286 + Math.floor(n() * 108), 3 + Math.floor(n() * 11), n() * 6.28, 0.03 + n() * 0.05, n() < 0.35]);
        n = lcg(21);
        this.petalos = [];
        for (let i = 0; i < 46; i++)
            this.petalos.push([n() * 640, n() * 400, 0.35 + n() * 0.45, 0.06 + n() * 0.12, n() * 6.28, Math.floor(n() * 3)]);

        this._cargaTexturas();
        this._leeAjustes();
        this.recalcula();
    }

    _cargaTexturas() {
        const img = f => GdkPixbuf.Pixbuf.new_from_file(`${this._dir}/images/${f}.png`);
        this.tex = {};
        for (const f of ['cielo-noche', 'cielo-dorado', 'cielo-dia', 'escena-noche', 'escena-dorado', 'escena-dia', 'sol', 'luna'])
            this.tex[f] = contenido(img(f));
        // nubes: una hoja de sprites por iluminacion; se recorta cada nube una vez
        this.texNubes = {};
        for (const fase of ['noche', 'dorado', 'dia']) {
            const hoja = img(`nubes-${fase}`);
            this.texNubes[fase] = this.D.nubes.map(nb => contenido(hoja.new_subpixbuf(0, nb[4], nb[2], nb[3]).copy()));
        }
    }

    _leeAjustes() {
        const s = this._settings;
        this.animar = s.get_boolean('animar');
        this.fps = Math.max(2, Math.min(24, s.get_int('fps')));
        this.horaSim = s.get_double('hora-simulada');
        this.demo = s.get_boolean('ciclo-rapido');
    }

    ajustesCambiados() {
        this._leeAjustes();
        this.recalcula();
        this.pinta();
        this._programa();
    }

    // ------------------------------------------------------------ astronomia (igual que el QML)
    static suave(t) { t = clamp01(t); return t * t * (3 - 2 * t); }
    sol(fecha) {
        const rad = Math.PI / 180;
        const n = fecha.getTime() / 86400000 + 2440587.5 - 2451545.0;
        const L = (280.460 + 0.9856474 * n) % 360;
        const g = ((357.528 + 0.9856003 * n) % 360) * rad;
        const lam = (L + 1.915 * Math.sin(g) + 0.020 * Math.sin(2 * g)) * rad;
        const eps = (23.439 - 0.0000004 * n) * rad;
        const ra = Math.atan2(Math.cos(eps) * Math.sin(lam), Math.cos(lam));
        const dec = Math.asin(Math.sin(eps) * Math.sin(lam));
        const gmst = (18.697374558 + 24.06570982441908 * n) % 24;
        let Hh = (gmst * 15 + this.lon) * rad - ra;
        Hh = Math.atan2(Math.sin(Hh), Math.cos(Hh));
        const phi = this.lat * rad;
        const e = Math.asin(Math.sin(phi) * Math.sin(dec) + Math.cos(phi) * Math.cos(dec) * Math.cos(Hh));
        const A = Math.atan2(Math.sin(Hh), Math.cos(Hh) * Math.sin(phi) - Math.tan(dec) * Math.cos(phi)) + Math.PI;
        const c0 = Math.max(-1, Math.min(1, -Math.tan(phi) * Math.tan(dec)));
        return {e: e / rad, az: A / rad % 360, H: Hh, H0: Math.acos(c0)};
    }
    fechaEfectiva() {
        const d = new Date();
        if (this.demo) {
            const h = (Date.now() / 1000 % 90) / 90 * 24;
            d.setHours(Math.floor(h), Math.floor(h % 1 * 60), Math.floor(h * 3600 % 60), 0);
        } else if (this.horaSim >= 0) {
            d.setHours(Math.floor(this.horaSim), Math.round(this.horaSim % 1 * 60), 0, 0);
        }
        return d;
    }
    recalcula() {
        const s = this.sol(this.fechaEfectiva());
        const su = Escena.suave;
        this.elev = s.e;
        this.wA = s.e <= -14 ? 0 : s.e >= 0 ? 1 : su((s.e + 14) / 14);
        this.wB = s.e <= 0 ? 0 : s.e >= 16 ? 1 : su(s.e / 16);
        this.nocheF = clamp01((4 - s.e) / 10);
        this.estrellaF = clamp01((-6 - s.e) / 8);
        this.solX = Math.max(30, Math.min(610, 320 + (s.az - 180) * 2.3));
        this.solY = Math.max(24, 272 - Math.max(s.e, -9) * 3.6);
        this.solOp = clamp01((s.e + 6) / 6);
        const H0 = s.H0;
        let f = -1;
        if (s.H >= H0) f = (s.H - H0) / (2 * Math.PI - 2 * H0);
        else if (s.H <= -H0) f = (s.H + 2 * Math.PI - H0) / (2 * Math.PI - 2 * H0);
        if (f >= 0) { this.lunaX = 110 + f * 420; this.lunaY = 272 - 56 * Math.sin(Math.PI * f) * 3.6; }
        else if (this.lunaX === undefined) { this.lunaX = 320; this.lunaY = 300; }
        this.lunaOp = f >= 0 ? clamp01((-s.e - 1) / 5) : 0;
        this.cuerpoX = this.elev > -1 ? this.solX : this.lunaX;
        this.cuerpoOp = this.elev > -1 ? clamp01((this.elev + 2) / 6) : this.lunaOp;
    }
    ponUbicacion(lat, lon) {
        this.lat = lat; this.lon = lon;
        this.recalcula();
        this.pinta();
    }
    osc(f, p) { return 0.5 + 0.5 * Math.sin(this.tick * f + p); }

    // ------------------------------------------------------------ construccion
    // Un unico lienzo de 640x400 con todo el paisaje. El monitor principal lo muestra tal cual y los
    // demas usan un Clutter.Clone: la escena se calcula y se dibuja una sola vez por cuadro.
    // Los pixeles animados (estrellas, olas, petalos...) se pintan con Cairo en dos St.DrawingArea
    // de 640x400 en vez de ser cientos de actores: Clutter solo mueve ~25 actores por cuadro.
    construye(monitores) {
        this.destruyeMonitores();
        if (!monitores.length) return;
        this._lienzo = this._creaLienzo();
        monitores.forEach((mon, i) => this._monitores.push(this._creaMonitor(mon, i === 0)));
        this.pinta();
        this._programa();
    }

    _creaLienzo() {
        const D = this.D, T = this.tex;
        const l = {};
        const raiz = new Clutter.Actor({width: W, height: H});
        l.raiz = raiz;
        const area = fn => {
            const a = new St.DrawingArea({width: W, height: H});
            a.set_content_scaling_filters(Clutter.ScalingFilter.NEAREST, Clutter.ScalingFilter.NEAREST);
            a.connect('repaint', ar => {
                const cr = ar.get_context();
                try {
                    const [sw] = ar.get_surface_size();
                    cr.scale(sw / W, sw / W);
                    cr.setAntialias(Cairo.Antialias.NONE);
                    fn(cr);
                } catch (e) {
                    logError(e, 'PixelZen escena');
                } finally {
                    cr.$dispose();
                }
            });
            raiz.add_child(a);
            return a;
        };

        l.cielo = ['noche', 'dorado', 'dia'].map(f => imagen(raiz, T[`cielo-${f}`], W, H));
        l.atras = area(cr => this._pintaAtras(cr));            // estrellas, grullas, estrella fugaz
        l.sol = imagen(raiz, T.sol, 208, 208);
        l.luna = imagen(raiz, T.luna, 208, 208);
        l.nubes = D.nubes.map((nb, i) => ['noche', 'dorado', 'dia'].map(f => {
            const a = imagen(raiz, this.texNubes[f][i], nb[2], nb[3]);
            a.y = nb[1];
            return a;
        }));
        l.escena = ['noche', 'dorado', 'dia'].map(f => imagen(raiz, T[`escena-${f}`], W, H));
        l.delante = area(cr => this._pintaDelante(cr));        // luces, lago, petalos, luciernagas
        return l;
    }

    _creaMonitor(mon, principal) {
        const raiz = new Clutter.Actor({x: mon.x, y: mon.y, width: mon.width, height: mon.height, clip_to_allocation: true});
        raiz.set_background_color(color('#0a0c24'));
        this._cont.add_child(raiz);

        const u = Math.max(mon.width / W, mon.height / H);
        const arte = new Clutter.Actor({width: W, height: H});
        arte.set_scale(u, u);
        arte.set_position(Math.round((mon.width - W * u) / 2), Math.round((mon.height - H * u) / 2));
        raiz.add_child(arte);
        arte.add_child(principal ? this._lienzo.raiz : new Clutter.Clone({source: this._lienzo.raiz, width: W, height: H}));

        // velo oscuro arriba a la izquierda (contraste para los iconos del escritorio)
        const r = Math.max(480, mon.width * 0.26);
        const velo = new St.DrawingArea({width: r, height: r});
        velo.connect('repaint', area => {
            const cr = area.get_context();
            const [w] = area.get_surface_size();
            const g = new Cairo.RadialGradient(0, 0, 0, 0, 0, w);
            g.addColorStopRGBA(0.0, 0.04, 0.03, 0.09, 0.82);
            g.addColorStopRGBA(0.5, 0.04, 0.03, 0.09, 0.62);
            g.addColorStopRGBA(1.0, 0.04, 0.03, 0.09, 0.0);
            cr.setSource(g);
            cr.rectangle(0, 0, w, w);
            cr.fill();
            cr.$dispose();
        });
        raiz.add_child(velo);
        return {raiz};
    }

    destruyeMonitores() {
        // primero los clones, luego el lienzo (que cuelga del monitor principal)
        for (const m of this._monitores.slice().reverse()) m.raiz.destroy();
        this._monitores = [];
        this._lienzo = null;
    }

    // ------------------------------------------------------------ animacion
    _programa() {
        if (this._timer) { GLib.source_remove(this._timer); this._timer = 0; }
        if (this._pausa || !this._lienzo) return;
        const ms = this.animar ? Math.round(1000 / this.fps) : 60000;
        this._timer = GLib.timeout_add(GLib.PRIORITY_DEFAULT, ms, () => {
            if (this.animar) {
                this.tick++;
                if (this.demo || this.tick % this.fps === 0) this.recalcula();
            } else {
                this.recalcula();
            }
            this.pinta();
            return GLib.SOURCE_CONTINUE;
        });
    }

    pausa(p) {
        if (p === this._pausa) return;
        this._pausa = p;
        if (!p) { this.recalcula(); this.pinta(); }
        this._programa();
    }

    // actores grandes (texturas): opacidades y posiciones
    pinta() {
        const l = this._lienzo;
        if (!l) return;
        const t = this.tick;
        const noche = this.elev < 0;
        const opNub = [noche ? 1 - this.wA : 0, noche ? this.wA : 1 - this.wB, this.wB];

        fija(l.cielo[1], this.wA); fija(l.cielo[2], this.wB);
        fija(l.escena[1], this.wA); fija(l.escena[2], this.wB);

        l.sol.set_position(Math.round(this.solX - 104), Math.round(this.solY - 104));
        fija(l.sol, this.solOp);
        l.luna.set_position(Math.round(this.lunaX - 104), Math.round(this.lunaY - 104));
        fija(l.luna, this.lunaOp);

        this.D.nubes.forEach((nb, i) => {
            const v = 0.035 + (i % 4) * 0.012;
            const cx = Math.round(((nb[0] + nb[2] + t * v) % (640 + nb[2])) - nb[2]);
            for (let k = 0; k < 3; k++) {
                const a = l.nubes[i][k];
                if (fija(a, opNub[k]) && a.x !== cx) a.x = cx;
            }
        });

        l.atras.queue_repaint();
        l.delante.queue_repaint();
    }

    // estrellas, grullas y estrella fugaz (detras de nubes y montanas)
    _pintaAtras(cr) {
        const t = this.tick, D = this.D;
        cr.setOperator(Cairo.Operator.CLEAR); cr.paint(); cr.setOperator(Cairo.Operator.OVER);
        const ef = this.estrellaF;
        if (ef > 0.01) {
            D.estrellas.forEach((e, i) => {
                const o = i % 3 === 0 ? 0.3 + 0.7 * this.osc(0.10 + (i % 7) * 0.02, i * 1.3) : 1;
                px(cr, e[2], ef * o, e[0], e[1]);
            });
            this.brillantes.forEach((e, i) => {
                const o = ef * 0.8 * Math.max(0, this.osc(0.07 + (i % 5) * 0.01, i * 2.1) - 0.55) / 0.45;
                if (o <= 0.004) return;
                px(cr, '#c7ccff', o, e[0] - 1, e[1]); px(cr, '#c7ccff', o, e[0] + 1, e[1]);
                px(cr, '#c7ccff', o, e[0], e[1] - 1); px(cr, '#c7ccff', o, e[0], e[1] + 1);
            });
        }
        // grullas
        const cuadro = [0, 1, 2, 1][Math.floor(t / 5) % 4];
        for (const [cx, cy] of [[((t * 0.22 + 40) % 760) - 60, 126 + 4 * Math.sin(t * 0.03)],
            [((t * 0.22 + 22) % 760) - 60, 116 + 4 * Math.sin(t * 0.03 + 1)],
            [((t * 0.20 + 5) % 760) - 60, 138 + 4 * Math.sin(t * 0.025 + 2)]]) {
            for (const [dx, dy] of ALAS[cuadro]) px(cr, '#120c26', 1, cx + dx, cy + dy);
            px(cr, '#120c26', 1, cx, cy + 1);
        }
        // estrella fugaz
        const periodo = this.fps * 38;
        const ciclo = Math.floor(t / periodo), fase = t % periodo;
        if (fase < 14 && ef > 0.5) {
            const x0 = 60 + ((ciclo * 137) % 300), y0 = 20 + ((ciclo * 53) % 70);
            for (let i = 0; i < 7; i++)
                px(cr, i === 0 ? '#fff8e6' : '#c7ccff', 1 - i / 8, x0 + (fase - i) * 5, y0 + (fase - i) * 2.4);
        }
    }

    // luces del templo, lago, petalos y luciernagas (delante del paisaje)
    _pintaDelante(cr) {
        const t = this.tick, D = this.D, nf = this.nocheF;
        cr.setOperator(Cairo.Operator.CLEAR); cr.paint(); cr.setOperator(Cairo.Operator.OVER);

        if (nf > 0.02) {
            D.ventanas.forEach((v, i) => {
                const p = nf * (((Math.floor(t / 24) + i) % 13 === 0) ? 0.25
                    : 0.7 + 0.3 * Math.sin(t * 0.09 * (1 + (i % 4) * 0.15) + i * 2.1));
                px(cr, '#f2b866', 0.10 * p, v[0] - 1, v[1] - 1, 4, 6);
                px(cr, '#f2b866', p, v[0], v[1], 2, 4);
            });
            D.faroles.forEach((fr, i) => {
                const p = nf * (0.65 + 0.35 * Math.sin(t * 0.11 + i * 1.7));
                const g = Math.max(2, Math.round(fr[2] / 3));
                px(cr, '#f2b866', 0.05 * p, fr[0] - g * 2, fr[1] - g * 2, g * 4 + 1, g * 4 + 1);
                px(cr, '#f2b866', 0.12 * p, fr[0] - g, fr[1] - g, g * 2 + 1, g * 2 + 1);
                px(cr, '#fff0c0', p, fr[0], fr[1], 1, 2);
            });
        }
        // olas
        for (const o of this.olas) {
            px(cr, o[5] ? '#cdaacc' : '#8d78b8', (0.08 + 0.55 * Math.max(0, Math.sin(t * 0.04 + o[3]))) * (1 - 0.6 * this.wB),
                o[0] + 6 * Math.sin(t * o[4] + o[3]), o[1], o[2], 1);
        }
        // camino de luz bajo el sol o la luna, y destellos
        const co = this.cuerpoOp;
        if (co > 0.02) {
            const col = this.elev > -1 ? '#ffe6a0' : '#f4e2c4';
            for (let i = 0; i < 38; i++) {
                const d = 8 + i * 3, w = Math.max(3, 46 - d * 0.30);
                px(cr, col, co * (0.75 - d * 0.005) * this.osc(0.07, i * 1.7),
                    this.cuerpoX - w / 2 + 3 * Math.sin(t * 0.05 + i * 1.3), 280 + d, w * (0.45 + 0.55 * this.osc(0.09, i * 2.2)), 1);
            }
            const dx = this.cuerpoX - 352;
            D.destellos.forEach((ds, i) => {
                const o = co * Math.pow(Math.max(0, Math.sin(t * 0.16 + i * 0.9)), 3);
                if (o > 0.004) px(cr, '#fff4dc', o, ds[0] + dx, ds[1], 2, 1);
            });
        }
        // petalos
        this.petalos.forEach((p, i) => {
            const ax = (p[0] + t * p[3] + 18 * Math.sin(t * 0.03 + p[4])) % 660 - 10;
            const ay = (p[1] + t * p[2]) % 420 - 10;
            if (ay >= 395) return;
            const h = Math.floor(t / 7 + i) % 2;
            px(cr, COL_PETALO[p[5]], 1, ax, ay, h ? 2 : 1, h ? 1 : 2);
        });
        // luciernagas
        if (nf > 0.3) {
            LUCIERNAGAS.forEach((lc, i) => {
                const fx = lc[0] + 9 * Math.sin(t * (0.021 + i * 0.002) + i * 2.3);
                const fy = lc[1] + 5 * Math.sin(t * (0.017 + i * 0.0015) + i * 1.1);
                const b = nf * Math.pow(Math.max(0, Math.sin(t * (0.05 + i * 0.004) + i * 1.9)), 2);
                px(cr, '#c9e86a', 0.25 * b, fx - 1, fy - 1, 3, 3);
                px(cr, '#eaf5a0', 0.2 + 0.8 * b, fx, fy, 1, 1);
            });
        }
    }

    destroy() {
        if (this._timer) GLib.source_remove(this._timer);
        this._timer = 0;
        this.destruyeMonitores();
    }
}
