import QtQuick

Rectangle {
    property real ax: 0
    property real ay: 0
    property real aw: 1
    property real ah: 1
    x: Math.round(ax) * Esc.u
    y: Math.round(ay) * Esc.u
    width: aw * Esc.u
    height: ah * Esc.u
    antialiasing: false
}
