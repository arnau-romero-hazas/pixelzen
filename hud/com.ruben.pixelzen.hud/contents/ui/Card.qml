import QtQuick
import org.kde.ksvg as KSvg

Item {
    id: card
    property string kanji: ""
    property string title: ""
    property string meta: ""
    property color metaColor: Pal.dim
    property int pad: 11
    default property alias content: body.data

    KSvg.FrameSvgItem {
        anchors.fill: parent
        imagePath: "widgets/translucentbackground"
    }
    Row {
        x: card.pad; y: 7; spacing: 7
        Text { text: card.kanji; font.family: Pal.jp; font.pixelSize: 14; color: Pal.rosa; renderType: Text.NativeRendering }
        Text { text: card.title; font.family: Pal.mono; font.pixelSize: 11; font.letterSpacing: 1; color: Pal.dim; y: 3; renderType: Text.NativeRendering }
    }
    Text {
        anchors.right: parent.right; anchors.rightMargin: card.pad; y: 8
        text: card.meta; font.family: Pal.mono; font.pixelSize: 12; color: card.metaColor; renderType: Text.NativeRendering
    }
    Row {  // linea punteada
        x: card.pad; y: 27; spacing: 2
        Repeater {
            model: Math.floor((card.width - 2 * card.pad) / 4)
            Rectangle { width: 2; height: 1; color: Pal.line }
        }
    }
    Item { id: body; x: card.pad; y: 34; width: card.width - 2 * card.pad; height: card.height - 34 - card.pad }
}
