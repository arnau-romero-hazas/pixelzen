import QtQuick
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami

Kirigami.FormLayout {
    id: root
    twinFormLayouts: parentLayout
    property alias formLayout: root
    property alias cfg_Animar: animar.checked
    property alias cfg_Fps: fps.value
    property double cfg_HoraSimulada: -1
    property bool cfg_CicloRapido: false
    QQC2.CheckBox { id: animar; Kirigami.FormData.label: "Animación:"; text: "Animar el paisaje" }
    QQC2.SpinBox { id: fps; Kirigami.FormData.label: "Cuadros por segundo:"; from: 2; to: 24 }
    QQC2.CheckBox { id: real; Kirigami.FormData.label: "Hora:"; text: "Usar la hora real"; checked: root.cfg_HoraSimulada < 0
        onToggled: root.cfg_HoraSimulada = checked ? -1 : hora.value }
    QQC2.Slider { id: hora; Kirigami.FormData.label: "Hora simulada:"; from: 0; to: 24; stepSize: 0.25; enabled: !real.checked
        value: root.cfg_HoraSimulada >= 0 ? root.cfg_HoraSimulada : 12; onMoved: root.cfg_HoraSimulada = value }
    QQC2.CheckBox { Kirigami.FormData.label: "Demostración:"; text: "Ciclo rápido (24 h en 90 s)"; checked: root.cfg_CicloRapido; onToggled: root.cfg_CicloRapido = checked }
}
