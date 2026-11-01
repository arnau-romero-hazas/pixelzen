import QtQuick

Item {
    id: bar
    property real value: 0        // 0..100
    property int segs: 22
    property color c1: Pal.green
    property color c2: Pal.amber
    property color c3: Pal.hot
    property bool invert: false   // true: pocas = rojo (bateria)
    height: 9
    function tono(f) {
        if (invert) return f < 0.2 ? c3 : f < 0.4 ? c2 : c1
        return f < 0.6 ? c1 : f < 0.85 ? c2 : c3
    }
    Row {
        spacing: 2
        Repeater {
            model: bar.segs
            Rectangle {
                width: Math.floor((bar.width - (bar.segs - 1) * 2) / bar.segs); height: bar.height
                property bool on: index < Math.round(Math.max(0, Math.min(100, bar.value)) / 100 * bar.segs)
                color: on ? bar.tono((index + 1) / bar.segs) : Pal.track
            }
        }
    }
}
