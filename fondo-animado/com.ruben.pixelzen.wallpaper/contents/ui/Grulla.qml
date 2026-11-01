import QtQuick

Item {
    property real cx: 0
    property real cy: 0
    readonly property var alas: [
        [[-5, -2], [-4, -2], [-3, -1], [-2, -1], [-1, 0], [0, 0], [1, 0], [2, -1], [3, -1], [4, -2], [5, -2]],
        [[-5, 1], [-4, 1], [-3, 1], [-2, 0], [-1, 0], [0, 0], [1, 0], [2, 0], [3, 1], [4, 1], [5, 1]],
        [[-5, 2], [-4, 1], [-3, 1], [-2, 0], [-1, 0], [0, 1], [1, 0], [2, 0], [3, 1], [4, 1], [5, 2]]]
    property int cuadro: [0, 1, 2, 1][Math.floor(Esc.tick / 5) % 4]
    Repeater {
        model: parent.alas[parent.cuadro]
        Px { ax: parent.cx + modelData[0]; ay: parent.cy + modelData[1]; color: "#120c26" }
    }
    Px { ax: parent.cx; ay: parent.cy + 1; color: "#120c26" }
}
