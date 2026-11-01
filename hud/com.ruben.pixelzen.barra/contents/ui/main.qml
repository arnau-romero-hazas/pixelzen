import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.plasma5support as P5Support

PlasmoidItem {
    id: root
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground
    preferredRepresentation: fullRepresentation

    readonly property string script: Qt.resolvedUrl("../code/datos.py").toString().replace("file://", "")
    property var d: ({ cpu: 0, ram: { pct: 0, usado: 0 }, temp: 0, bat: null, net: { rx: 0, tx: 0, vpn: {} } })
    function tasa(b) { return b >= 1048576 ? (b / 1048576).toFixed(1) + "M" : b >= 1024 ? Math.round(b / 1024) + "K" : b + "B" }
    function horas(m) { return m > 0 ? Math.floor(m / 60) + "h" + (m % 60 < 10 ? "0" : "") + (m % 60) : "" }

    P5Support.DataSource {
        id: sh
        engine: "executable"; interval: 0; connectedSources: []
        onNewData: function (source, data) {
            disconnectSource(source)
            if (source.indexOf("rapido") >= 0) { try { root.d = JSON.parse(data["stdout"]) } catch (e) {} }
        }
    }
    Timer { interval: 2000; running: true; repeat: true; triggeredOnStart: true; onTriggered: sh.connectSource("python3 -I " + root.script + " rapido barra") }

    component Seg: Row {
        property real v: 0
        property color c1: Pal.green
        property color c2: Pal.amber
        property color c3: Pal.hot
        spacing: 1
        Repeater {
            model: 6
            Rectangle {
                width: 4; height: 9; anchors.verticalCenter: parent.verticalCenter
                property real f: (index + 1) / 6
                color: f <= Math.round(v / 100 * 6) / 6 + 0.001 && v > 3 ? (f < 0.6 ? c1 : f < 0.85 ? c2 : c3) : Pal.track
            }
        }
    }
    component Etq: Text { font.family: Pal.mono; font.pixelSize: 11; color: Pal.dim; renderType: Text.NativeRendering; anchors.verticalCenter: parent.verticalCenter }
    component Val: Text { font.family: Pal.mono; font.pixelSize: 12; color: Pal.text; renderType: Text.NativeRendering; anchors.verticalCenter: parent.verticalCenter }

    fullRepresentation: Item {
        implicitWidth: row.implicitWidth + 12
        implicitHeight: 28
        Layout.minimumWidth: row.implicitWidth + 12
        Layout.preferredWidth: row.implicitWidth + 12
        Row {
            id: row
            x: 6; spacing: 16
            anchors.verticalCenter: parent.verticalCenter
            Row { spacing: 5; Etq { text: "CPU" } Seg { v: root.d.cpu; anchors.verticalCenter: parent.verticalCenter } Val { width: 28; text: Math.round(root.d.cpu) + "%" } }
            Row { spacing: 5; Etq { text: "RAM" } Seg { v: root.d.ram.pct; anchors.verticalCenter: parent.verticalCenter } Val { text: root.d.ram.usado + "G" } }
            Row { spacing: 5; Etq { text: "TMP" } Val { text: (root.d.temp ? Math.round(root.d.temp) : "--") + "°"; color: root.d.temp > 75 ? Pal.hot : root.d.temp > 60 ? Pal.amber : Pal.text } }
            Row { spacing: 5
                Etq { text: "↓" } Val { width: 34; text: root.tasa(root.d.net.rx ? root.d.net.rx : 0); color: Pal.cyan }
                Etq { text: "↑" } Val { width: 34; text: root.tasa(root.d.net.tx ? root.d.net.tx : 0); color: Pal.rosa }
            }
            Row { spacing: 5
                visible: !!(root.d.net.vpn && root.d.net.vpn.on)
                Rectangle { width: 7; height: 7; color: Pal.green; anchors.verticalCenter: parent.verticalCenter }
                Etq { text: "VPN" }
            }
            Row { spacing: 5
                visible: root.d.bat !== null && root.d.bat !== undefined
                Etq { text: root.d.bat && root.d.bat.estado === "Charging" ? "CAR" : "BAT" }
                Seg { v: root.d.bat ? root.d.bat.pct : 0; anchors.verticalCenter: parent.verticalCenter; c1: Pal.green; c3: Pal.hot }
                Val { text: root.d.bat ? root.d.bat.pct + "% " + root.horas(root.d.bat.min) : "" }
            }
        }
        MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: sh.connectSource("setsid -f alacritty --title btop -e btop") }
    }
}
