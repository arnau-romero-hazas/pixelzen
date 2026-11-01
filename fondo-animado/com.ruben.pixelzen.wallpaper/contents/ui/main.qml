import QtQuick
import QtQuick.Shapes
import org.kde.plasma.plasmoid
import org.kde.plasma.plasma5support as P5Support
import "datos.js" as DJ

WallpaperItem {
    id: root
    readonly property var datos: DJ.D
    readonly property bool animar: root.configuration.Animar !== false
    readonly property int fps: Math.max(2, Math.min(24, root.configuration.Fps || 8))
    readonly property real u: Math.max(width / 640, height / 400)
    readonly property real horaSim: root.configuration.HoraSimulada === undefined ? -1 : root.configuration.HoraSimulada
    readonly property bool demo: root.configuration.CicloRapido === true

    // ---- estado astronomico (se recalcula cada segundo, o cada cuadro en modo demo)
    property real lat: 39.17
    property real lon: -0.31
    property string origen: "casa"
    property real elev: -30       // altura del sol en grados
    property real azim: 180
    property real fracNoche: -1   // 0..1 durante la noche, -1 de dia
    property real wA: 0           // opacidad capa dorada sobre la noche
    property real wB: 0           // opacidad capa de dia sobre la dorada
    property real nocheF: 1       // 0 dia .. 1 noche cerrada (luces, luciernagas)
    property real estrellaF: 1
    property real solX: 320
    property real solY: 300
    property real lunaX: 320
    property real lunaY: 300
    property real solOp: 0
    property real lunaOp: 1
    property string horaTxt: ""

    function suave(t) { t = Math.max(0, Math.min(1, t)); return t * t * (3 - 2 * t) }
    function sol(fecha) {
        var rad = Math.PI / 180
        var n = fecha.getTime() / 86400000 + 2440587.5 - 2451545.0
        var L = (280.460 + 0.9856474 * n) % 360
        var g = ((357.528 + 0.9856003 * n) % 360) * rad
        var lam = (L + 1.915 * Math.sin(g) + 0.020 * Math.sin(2 * g)) * rad
        var eps = (23.439 - 0.0000004 * n) * rad
        var ra = Math.atan2(Math.cos(eps) * Math.sin(lam), Math.cos(lam))
        var dec = Math.asin(Math.sin(eps) * Math.sin(lam))
        var gmst = (18.697374558 + 24.06570982441908 * n) % 24
        var H = ((gmst * 15 + lon) * rad - ra)
        H = Math.atan2(Math.sin(H), Math.cos(H))        // [-pi, pi)
        var phi = lat * rad
        var e = Math.asin(Math.sin(phi) * Math.sin(dec) + Math.cos(phi) * Math.cos(dec) * Math.cos(H))
        var A = Math.atan2(Math.sin(H), Math.cos(H) * Math.sin(phi) - Math.tan(dec) * Math.cos(phi)) + Math.PI
        var c0 = Math.max(-1, Math.min(1, -Math.tan(phi) * Math.tan(dec)))
        return { e: e / rad, az: A / rad % 360, H: H, H0: Math.acos(c0) }
    }
    function fechaEfectiva() {
        var d = new Date()
        if (demo) {
            var h = (Date.now() / 1000 % 90) / 90 * 24
            d.setHours(Math.floor(h), Math.floor(h % 1 * 60), Math.floor(h * 3600 % 60), 0)
        } else if (horaSim >= 0) {
            d.setHours(Math.floor(horaSim), Math.round(horaSim % 1 * 60), 0, 0)
        }
        return d
    }
    function recalcula() {
        var d = fechaEfectiva()
        var s = sol(d)
        elev = s.e; azim = s.az
        horaTxt = (d.getHours() < 10 ? "0" : "") + d.getHours() + ":" + (d.getMinutes() < 10 ? "0" : "") + d.getMinutes()
        wA = s.e <= -14 ? 0 : s.e >= 0 ? 1 : suave((s.e + 14) / 14)
        wB = s.e <= 0 ? 0 : s.e >= 16 ? 1 : suave(s.e / 16)
        nocheF = Math.max(0, Math.min(1, (4 - s.e) / 10))
        estrellaF = Math.max(0, Math.min(1, (-6 - s.e) / 8))
        solX = Math.max(30, Math.min(610, 320 + (s.az - 180) * 2.3))
        solY = Math.max(24, 272 - Math.max(s.e, -9) * 3.6)
        solOp = Math.max(0, Math.min(1, (s.e + 6) / 6))
        // luna: arco artistico de oriente a poniente durante la noche
        var H0 = s.H0, f = -1
        if (s.H >= H0) f = (s.H - H0) / (2 * Math.PI - 2 * H0)
        else if (s.H <= -H0) f = (s.H + 2 * Math.PI - H0) / (2 * Math.PI - 2 * H0)
        fracNoche = f
        if (f >= 0) { lunaX = 110 + f * 420; lunaY = 272 - 56 * Math.sin(Math.PI * f) * 3.6 }
        lunaOp = f >= 0 ? Math.max(0, Math.min(1, (-s.e - 1) / 5)) : 0
    }
    Component.onCompleted: { Esc.u = u; recalcula(); ubi.connectSource(ubiCmd) }
    onUChanged: Esc.u = u
    onHoraSimChanged: recalcula()
    onDemoChanged: recalcula()
    Timer { interval: Math.round(1000 / root.fps); running: root.animar && root.visible; repeat: true
        onTriggered: { Esc.tick++; if (root.demo || Esc.tick % root.fps === 0) root.recalcula() } }

    // ---- ubicacion (sin red): casa o zona horaria
    readonly property string ubiCmd: "python3 -I " + Qt.resolvedUrl("../code/ubicacion.py").toString().replace("file://", "")
    P5Support.DataSource {
        id: ubi
        engine: "executable"; interval: 0; connectedSources: []
        onNewData: function (source, data) {
            disconnectSource(source)
            try { var r = JSON.parse(data["stdout"]); root.lat = r.lat; root.lon = r.lon; root.origen = r.origen } catch (e) {}
        }
    }
    Timer { interval: 1800000; running: true; repeat: true; onTriggered: ubi.connectSource(root.ubiCmd) }

    // ---- datos fijos
    readonly property var brillantes: datos.estrellas.filter(function (e) { return e[3] === 1 })
    readonly property var olas: (function () {
        var r = [], s = 7
        function n() { s = (s * 16807) % 2147483647; return s / 2147483647 }
        for (var i = 0; i < 44; i++) r.push([300 + Math.floor(n() * 260), 286 + Math.floor(n() * 108), 3 + Math.floor(n() * 11), n() * 6.28, 0.03 + n() * 0.05, n() < 0.35])
        return r
    })()
    readonly property var petalos: (function () {
        var r = [], s = 21
        function n() { s = (s * 16807) % 2147483647; return s / 2147483647 }
        for (var i = 0; i < 46; i++) r.push([n() * 640, n() * 400, 0.35 + n() * 0.45, 0.06 + n() * 0.12, n() * 6.28, Math.floor(n() * 3)])
        return r
    })()
    readonly property var luciernagas: [[70, 300], [95, 330], [130, 290], [565, 310], [590, 340], [20, 345], [470, 296], [160, 355], [248, 318], [520, 352]]
    readonly property var colPetalo: ["#f7cfdb", "#eda0b8", "#fdeff3"]
    readonly property real cuerpoX: elev > -1 ? solX : lunaX
    readonly property real cuerpoOp: elev > -1 ? Math.max(0, Math.min(1, (elev + 2) / 6)) : lunaOp

    Rectangle { anchors.fill: parent; color: "#0a0c24" }
    Item {
        id: escena
        x: (root.width - 640 * root.u) / 2
        y: (root.height - 400 * root.u) / 2
        width: 640 * root.u
        height: 400 * root.u

        // ------------------------------------------------ cielo (tres iluminaciones encadenadas)
        Image { anchors.fill: parent; source: "../images/cielo-noche.png"; smooth: false }
        Image { anchors.fill: parent; source: "../images/cielo-dorado.png"; smooth: false; opacity: root.wA }
        Image { anchors.fill: parent; source: "../images/cielo-dia.png"; smooth: false; opacity: root.wB }

        // ------------------------------------------------ estrellas
        Repeater {
            model: root.datos.estrellas
            Px {
                ax: modelData[0]; ay: modelData[1]; color: modelData[2]
                opacity: root.estrellaF * (index % 3 === 0 ? 0.3 + 0.7 * Esc.osc(0.10 + (index % 7) * 0.02, index * 1.3) : 1)
                visible: root.estrellaF > 0.01
            }
        }
        Repeater {
            model: root.brillantes
            Item {
                property real brillo: root.estrellaF * Math.max(0, Esc.osc(0.07 + (index % 5) * 0.01, index * 2.1) - 0.55) / 0.45
                visible: root.estrellaF > 0.01
                Px { ax: modelData[0] - 1; ay: modelData[1]; color: "#c7ccff"; opacity: parent.brillo * 0.8 }
                Px { ax: modelData[0] + 1; ay: modelData[1]; color: "#c7ccff"; opacity: parent.brillo * 0.8 }
                Px { ax: modelData[0]; ay: modelData[1] - 1; color: "#c7ccff"; opacity: parent.brillo * 0.8 }
                Px { ax: modelData[0]; ay: modelData[1] + 1; color: "#c7ccff"; opacity: parent.brillo * 0.8 }
            }
        }

        // ------------------------------------------------ sol y luna
        Image { source: "../images/sol.png"; smooth: false; width: 208 * Esc.u; height: 208 * Esc.u
            x: Math.round(root.solX - 104) * Esc.u; y: Math.round(root.solY - 104) * Esc.u; opacity: root.solOp; visible: opacity > 0.01 }
        Image { source: "../images/luna.png"; smooth: false; width: 208 * Esc.u; height: 208 * Esc.u
            x: Math.round(root.lunaX - 104) * Esc.u; y: Math.round(root.lunaY - 104) * Esc.u; opacity: root.lunaOp; visible: opacity > 0.01 }

        // ------------------------------------------------ nubes (una hoja por iluminacion)
        Repeater {
            model: root.datos.nubes
            Item {
                property real v: 0.035 + (index % 4) * 0.012
                property real cx: (Math.round(((modelData[0] + modelData[2] + Esc.tick * v) % (640 + modelData[2])) - modelData[2])) * Esc.u
                Image { source: "../images/nubes-noche.png"; sourceClipRect: Qt.rect(0, modelData[4], modelData[2], modelData[3]); smooth: false
                    width: modelData[2] * Esc.u; height: modelData[3] * Esc.u; x: parent.cx; y: modelData[1] * Esc.u; opacity: root.elev < 0 ? 1 - root.wA : 0 }
                Image { source: "../images/nubes-dorado.png"; sourceClipRect: Qt.rect(0, modelData[4], modelData[2], modelData[3]); smooth: false
                    width: modelData[2] * Esc.u; height: modelData[3] * Esc.u; x: parent.cx; y: modelData[1] * Esc.u; opacity: root.elev < 0 ? root.wA : 1 - root.wB }
                Image { source: "../images/nubes-dia.png"; sourceClipRect: Qt.rect(0, modelData[4], modelData[2], modelData[3]); smooth: false
                    width: modelData[2] * Esc.u; height: modelData[3] * Esc.u; x: parent.cx; y: modelData[1] * Esc.u; opacity: root.wB }
            }
        }

        // ------------------------------------------------ grullas y estrella fugaz
        Grulla { cx: ((Esc.tick * 0.22 + 40) % 760) - 60; cy: 126 + 4 * Math.sin(Esc.tick * 0.03) }
        Grulla { cx: ((Esc.tick * 0.22 + 22) % 760) - 60; cy: 116 + 4 * Math.sin(Esc.tick * 0.03 + 1) }
        Grulla { cx: ((Esc.tick * 0.20 + 5) % 760) - 60; cy: 138 + 4 * Math.sin(Esc.tick * 0.025 + 2) }
        Item {
            id: fugaz
            property int ciclo: Math.floor(Esc.tick / (root.fps * 38))
            property int fase: Esc.tick % (root.fps * 38)
            property real x0: 60 + ((ciclo * 137) % 300)
            property real y0: 20 + ((ciclo * 53) % 70)
            visible: fase < 14 && root.estrellaF > 0.5
            Repeater { model: 7
                Px { ax: fugaz.x0 + (fugaz.fase - index) * 5; ay: fugaz.y0 + (fugaz.fase - index) * 2.4; color: index === 0 ? "#fff8e6" : "#c7ccff"; opacity: 1 - index / 8 } }
        }

        // ------------------------------------------------ escena (montanas, templo, lago, cerezo), tres iluminaciones
        Image { anchors.fill: parent; source: "../images/escena-noche.png"; smooth: false }
        Image { anchors.fill: parent; source: "../images/escena-dorado.png"; smooth: false; opacity: root.wA }
        Image { anchors.fill: parent; source: "../images/escena-dia.png"; smooth: false; opacity: root.wB }

        // ------------------------------------------------ luces del templo (solo cuando oscurece)
        Repeater {
            model: root.datos.ventanas
            Item {
                visible: root.nocheF > 0.02
                property real p: root.nocheF * (((Math.floor(Esc.tick / 24) + index) % 13 === 0) ? 0.25 : 0.7 + 0.3 * Math.sin(Esc.tick * 0.09 * (1 + (index % 4) * 0.15) + index * 2.1))
                Px { ax: modelData[0] - 1; ay: modelData[1] - 1; aw: 4; ah: 6; color: "#f2b866"; opacity: 0.10 * parent.p }
                Px { ax: modelData[0]; ay: modelData[1]; aw: 2; ah: 4; color: "#f2b866"; opacity: parent.p }
            }
        }
        Repeater {
            model: root.datos.faroles
            Item {
                visible: root.nocheF > 0.02
                property real p: root.nocheF * (0.65 + 0.35 * Math.sin(Esc.tick * 0.11 + index * 1.7))
                property int g: Math.max(2, Math.round(modelData[2] / 3))
                Px { ax: modelData[0] - parent.g * 2; ay: modelData[1] - parent.g * 2; aw: parent.g * 4 + 1; ah: parent.g * 4 + 1; color: "#f2b866"; opacity: 0.05 * parent.p }
                Px { ax: modelData[0] - parent.g; ay: modelData[1] - parent.g; aw: parent.g * 2 + 1; ah: parent.g * 2 + 1; color: "#f2b866"; opacity: 0.12 * parent.p }
                Px { ax: modelData[0]; ay: modelData[1]; aw: 1; ah: 2; color: "#fff0c0"; opacity: parent.p }
            }
        }

        // ------------------------------------------------ lago: olas, camino del sol/luna y destellos
        Repeater {
            model: root.olas
            Px {
                ax: modelData[0] + 6 * Math.sin(Esc.tick * modelData[4] + modelData[3]); ay: modelData[1]; aw: modelData[2]
                color: modelData[5] ? "#cdaacc" : "#8d78b8"
                opacity: (0.08 + 0.55 * Math.max(0, Math.sin(Esc.tick * 0.04 + modelData[3]))) * (1 - 0.6 * root.wB)
            }
        }
        Repeater {      // camino de luz bajo el cuerpo celeste (sigue al sol o a la luna)
            model: 38
            Px {
                property real d: 8 + index * 3
                property real w: Math.max(3, 46 - d * 0.30)
                ax: root.cuerpoX - w / 2 + 3 * Math.sin(Esc.tick * 0.05 + index * 1.3); ay: 280 + d; aw: w * (0.45 + 0.55 * Esc.osc(0.09, index * 2.2))
                color: root.elev > -1 ? "#ffe6a0" : "#f4e2c4"
                opacity: root.cuerpoOp * (0.75 - d * 0.005) * Esc.osc(0.07, index * 1.7)
                visible: root.cuerpoOp > 0.02
            }
        }
        Repeater {
            model: root.datos.destellos
            Px {
                ax: modelData[0] + (root.cuerpoX - 352); ay: modelData[1]; aw: 2; color: "#fff4dc"
                opacity: root.cuerpoOp * Math.pow(Math.max(0, Math.sin(Esc.tick * 0.16 + index * 0.9)), 3)
                visible: root.cuerpoOp > 0.02
            }
        }

        // ------------------------------------------------ petalos de cerezo
        Repeater {
            model: root.petalos
            Px {
                ax: (modelData[0] + Esc.tick * modelData[3] + 18 * Math.sin(Esc.tick * 0.03 + modelData[4])) % 660 - 10
                ay: (modelData[1] + Esc.tick * modelData[2]) % 420 - 10
                aw: Math.floor(Esc.tick / 7 + index) % 2 ? 2 : 1
                ah: Math.floor(Esc.tick / 7 + index) % 2 ? 1 : 2
                color: root.colPetalo[modelData[5]]
                visible: ay < 395
            }
        }

        // ------------------------------------------------ luciernagas (de noche)
        Repeater {
            model: root.luciernagas
            Item {
                visible: root.nocheF > 0.3
                property real fx: modelData[0] + 9 * Math.sin(Esc.tick * (0.021 + index * 0.002) + index * 2.3)
                property real fy: modelData[1] + 5 * Math.sin(Esc.tick * (0.017 + index * 0.0015) + index * 1.1)
                property real b: root.nocheF * Math.pow(Math.max(0, Math.sin(Esc.tick * (0.05 + index * 0.004) + index * 1.9)), 2)
                Px { ax: parent.fx - 1; ay: parent.fy - 1; aw: 3; ah: 3; color: "#c9e86a"; opacity: 0.25 * parent.b }
                Px { ax: parent.fx; ay: parent.fy; color: "#eaf5a0"; opacity: 0.2 + 0.8 * parent.b }
            }
        }
    }

    // velo oscuro suave arriba a la izquierda: da contraste a los nombres de los iconos del escritorio
    Shape {
        id: velo
        readonly property real r: Math.max(480, root.width * 0.26)
        width: r; height: r
        ShapePath {
            strokeColor: "transparent"
            fillGradient: RadialGradient {
                centerX: 0; centerY: 0; focalX: 0; focalY: 0; centerRadius: velo.r
                GradientStop { position: 0.0; color: Qt.rgba(0.04, 0.03, 0.09, 0.82) }
                GradientStop { position: 0.5; color: Qt.rgba(0.04, 0.03, 0.09, 0.62) }
                GradientStop { position: 1.0; color: Qt.rgba(0.04, 0.03, 0.09, 0.0) }
            }
            startX: 0; startY: 0
            PathLine { x: velo.r; y: 0 }
            PathLine { x: velo.r; y: velo.r }
            PathLine { x: 0; y: velo.r }
        }
    }
}
