pragma Singleton
import QtQuick

QtObject {
    property real u: 3        // pixeles de pantalla por pixel de arte
    property int tick: 0
    function osc(f, p) { return 0.5 + 0.5 * Math.sin(Esc.tick * f + p) }
}
