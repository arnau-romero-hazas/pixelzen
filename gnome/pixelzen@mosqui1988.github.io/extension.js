// PixelZen para GNOME Shell: fondo pixel art animado que sigue al sol + panel de datos.
// Port del tema PixelZen de KDE Plasma 6 (https://github.com/mosqui1988/pixelzen). GPL-3.0-or-later.

import GLib from 'gi://GLib';
import Gio from 'gi://Gio';
import Clutter from 'gi://Clutter';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

import {Escena} from './escena.js';
import {Hud} from './hud.js';

export default class PixelZenExtension extends Extension {
    enable() {
        this._settings = this.getSettings();
        this._ids = [];
        this._grupo = Main.layoutManager._backgroundGroup;

        // Todo cuelga de un contenedor propio dentro del grupo de fondos del escritorio:
        // queda por encima del fondo de GNOME y por debajo de ventanas e iconos del escritorio.
        this._raiz = new Clutter.Actor({reactive: false});
        this._grupo.add_child(this._raiz);

        try {
            this._escena = new Escena(this.path, this._raiz, this._settings);
        } catch (e) {
            logError(e, 'PixelZen: no encuentro las capas del fondo; ejecuta gnome/instalar.sh');
            this._escena = null;
        }
        this._hud = null;

        this._construye();
        this._ubicacion();
        this._timerUbi = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 1800, () => { this._ubicacion(); return GLib.SOURCE_CONTINUE; });

        const con = (obj, sig, fn) => this._ids.push([obj, obj.connect(sig, fn)]);
        con(Main.layoutManager, 'monitors-changed', () => this._construye());
        con(global.display, 'workareas-changed', () => this._colocaHud());
        // GNOME vuelve a crear su actor de fondo al cambiar de wallpaper o de monitores: nos mantenemos encima
        con(this._grupo, 'child-added', (_g, hijo) => {
            if (hijo !== this._raiz) this._grupo.set_child_above_sibling(this._raiz, null);
        });
        con(global.display, 'in-fullscreen-changed', () => this._actualizaPausa());
        con(Main.sessionMode, 'updated', () => this._actualizaPausa());
        con(this._settings, 'changed', (_s, clave) => {
            if (clave === 'hud' || clave === 'hud-monitor' || clave === 'todos-monitores') this._construye();
            else this._escena?.ajustesCambiados();
        });
        this._actualizaPausa();
    }

    _monitores() {
        const lm = Main.layoutManager;
        return this._settings.get_boolean('todos-monitores') ? lm.monitors : [lm.primaryMonitor];
    }

    _construye() {
        this._escena?.construye(this._monitores().filter(Boolean));
        this._grupo.set_child_above_sibling(this._raiz, null);

        const quiereHud = this._settings.get_boolean('hud');
        if (quiereHud && !this._hud) {
            this._hud = new Hud(this.path);
            this._raiz.add_child(this._hud.actor);
        } else if (!quiereHud && this._hud) {
            this._hud.destroy();
            this._hud = null;
        }
        if (this._hud) {
            this._raiz.set_child_above_sibling(this._hud.actor, null);
            this._colocaHud();
        }
    }

    _colocaHud() {
        if (!this._hud) return;
        const lm = Main.layoutManager;
        let i = this._settings.get_int('hud-monitor');
        if (i < 0 || i >= lm.monitors.length) i = lm.primaryIndex;
        this._hud.coloca(lm.getWorkAreaForMonitor(i));
    }

    // pausa la animacion con la pantalla bloqueada o con una ventana a pantalla completa en el monitor principal
    _actualizaPausa() {
        const bloqueada = Main.sessionMode.isLocked || Main.sessionMode.isGreeter;
        const lm = Main.layoutManager;
        const completa = lm.primaryIndex >= 0 && global.display.get_monitor_in_fullscreen(lm.primaryIndex);
        this._escena?.pausa(bloqueada || completa);
    }

    // ubicacion sin red: casa fija (~/.config/pixelzen/ubicacion.json) o la zona horaria
    _ubicacion() {
        if (!this._escena) return;
        try {
            const p = Gio.Subprocess.new(['python3', '-I', `${this.path}/code/ubicacion.py`],
                Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_SILENCE);
            p.communicate_utf8_async(null, null, (proc, res) => {
                try {
                    const [, out] = proc.communicate_utf8_finish(res);
                    const r = JSON.parse(out);
                    this._escena?.ponUbicacion(r.lat, r.lon);
                } catch (e) { /* se queda la ubicacion anterior */ }
            });
        } catch (e) { /* sin python3: Madrid por defecto */ }
    }

    disable() {
        for (const [obj, id] of this._ids) obj.disconnect(id);
        this._ids = [];
        if (this._timerUbi) GLib.source_remove(this._timerUbi);
        this._timerUbi = 0;
        this._hud?.destroy();
        this._hud = null;
        this._escena?.destroy();
        this._escena = null;
        this._raiz?.destroy();
        this._raiz = null;
        this._settings = null;
        this._grupo = null;
    }
}
