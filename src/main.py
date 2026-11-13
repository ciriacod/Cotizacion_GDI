"""Sistema de Gestión de Cotizaciones JP - Versión B (prototipo visual).

Esta versión contiene únicamente la interfaz gráfica. Los botones y elementos
navegables son visuales: todavía no ejecutan operaciones ni se conectan a MySQL.
Requiere Python 3.10+ y PySide6.
"""

import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
    QProgressBar,
)


APP_STYLE = """
* {
    font-family: 'Segoe UI', 'Inter', sans-serif;
}
QMainWindow, QWidget#centralWidget {
    background: #F4F6FA;
    color: #1F2937;
}
QFrame#sidebar {
    background: #172B4D;
    border: none;
}
QLabel#brandTitle {
    color: #FFFFFF;
    font-size: 17px;
    font-weight: 800;
    letter-spacing: 0.5px;
}
QLabel#brandSubtitle {
    color: #A9B8CC;
    font-size: 10px;
    letter-spacing: 1.2px;
}
QLabel#menuCaption {
    color: #8295B1;
    font-size: 10px;
    font-weight: 700;
    padding: 18px 10px 7px 10px;
    letter-spacing: 1.1px;
}
QPushButton#navButton {
    background: transparent;
    color: #C8D3E2;
    border: none;
    border-radius: 8px;
    text-align: left;
    padding: 11px 13px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#navButton:hover {
    background: #233B60;
    color: white;
}
QPushButton#navButton[active="true"] {
    background: #2B4770;
    color: #FFFFFF;
    border-left: 3px solid #48C99A;
    padding-left: 10px;
}
QLabel#sidebarFooter {
    color: #8295B1;
    font-size: 10px;
}
QFrame#topbar {
    background: #FFFFFF;
    border: 1px solid #E7EBF1;
    border-radius: 12px;
}
QLabel#pageTitle {
    color: #172B4D;
    font-size: 24px;
    font-weight: 800;
}
QLabel#muted {
    color: #7B8798;
    font-size: 12px;
}
QLabel#sectionTitle {
    color: #243247;
    font-size: 15px;
    font-weight: 750;
}
QLabel#sectionHint {
    color: #8994A4;
    font-size: 11px;
}
QFrame#contentCard, QFrame#metricCard {
    background: #FFFFFF;
    border: 1px solid #E8ECF2;
    border-radius: 13px;
}
QLabel#metricLabel {
    color: #7B8798;
    font-size: 11px;
    font-weight: 600;
}
QLabel#metricValue {
    color: #172B4D;
    font-size: 25px;
    font-weight: 800;
}
QLabel#metricNote {
    color: #7B8798;
    font-size: 10px;
}
QPushButton#primaryButton {
    background: #1D9B70;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 12px;
    font-weight: 700;
}
QPushButton#primaryButton:hover { background: #17845F; }
QPushButton#secondaryButton {
    background: #F2F5F9;
    color: #39516F;
    border: 1px solid #E3E8EF;
    border-radius: 7px;
    padding: 7px 11px;
    font-size: 11px;
    font-weight: 650;
}
QPushButton#secondaryButton:hover { background: #E9EEF5; }
QTableWidget {
    background: #FFFFFF;
    border: none;
    gridline-color: #EEF1F5;
    selection-background-color: #EAF5F0;
    selection-color: #203448;
    font-size: 11px;
}
QHeaderView::section {
    background: #F7F9FC;
    color: #758195;
    border: none;
    border-bottom: 1px solid #E9EDF3;
    padding: 11px 8px;
    font-size: 10px;
    font-weight: 750;
}
QTableWidget::item {
    border-bottom: 1px solid #F0F2F6;
    padding: 7px;
}
QProgressBar {
    background: #EEF1F5;
    border: none;
    border-radius: 4px;
    min-height: 7px;
    max-height: 7px;
    text-align: center;
}
QProgressBar::chunk {
    background: #2CB889;
    border-radius: 4px;
}
"""


class CotizacionesJPWindow(QMainWindow):
    """Ventana principal del prototipo; no contiene lógica de negocio."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("JP Ingeniería | Gestión de Cotizaciones")
        self.resize(1440, 900)
        self.setMinimumSize(1120, 720)
        self.setStyleSheet(APP_STYLE)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        workspace = QWidget()
        workspace_layout = QVBoxLayout(workspace)
        workspace_layout.setContentsMargins(28, 22, 28, 22)
        workspace_layout.setSpacing(20)
        workspace_layout.addWidget(self._build_topbar())
        workspace_layout.addWidget(self._build_page_heading())
        workspace_layout.addLayout(self._build_metrics())
        workspace_layout.addLayout(self._build_main_content(), 1)
        root.addWidget(workspace, 1)

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(245)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(17, 25, 17, 18)
        layout.setSpacing(5)

        brand_row = QHBoxLayout()
        brand_mark = QLabel("JP")
        brand_mark.setFixedSize(43, 43)
        brand_mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_mark.setStyleSheet(
            "background:#2B4770;color:#FFFFFF;border:1px solid #46658F;"
            "border-radius:11px;font-size:17px;font-weight:900;"
        )
        brand_text = QVBoxLayout()
        title = QLabel("JP INGENIERÍA")
        title.setObjectName("brandTitle")
        subtitle = QLabel("GESTIÓN DE COTIZACIONES")
        subtitle.setObjectName("brandSubtitle")
        brand_text.addWidget(title)
        brand_text.addWidget(subtitle)
        brand_row.addWidget(brand_mark)
        brand_row.addSpacing(10)
        brand_row.addLayout(brand_text, 1)
        layout.addLayout(brand_row)
        layout.addSpacing(29)

        layout.addWidget(self._menu_caption("GENERAL"))
        nav_items = [
            ("▦", "Panel general", True),
            ("▤", "Cotizaciones", False),
        ]
        for icon, text, active in nav_items:
            layout.addWidget(self._nav_button(icon, text, active))

        layout.addWidget(self._menu_caption("GESTIÓN"))
        for icon, text in [
            ("♙", "Clientes"),
            ("♧", "Empleados"),
            ("▣", "Productos y servicios"),
            ("⚙", "Parámetros"),
        ]:
            layout.addWidget(self._nav_button(icon, text, False))

        layout.addWidget(self._menu_caption("INFORMACIÓN"))
        layout.addWidget(self._nav_button("▥", "Reportes", False))
        layout.addStretch(1)

        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background:#2B4262;border:none;")
        layout.addWidget(separator)
        layout.addSpacing(12)
        layout.addWidget(self._nav_button("⚙", "Configuración", False))
        footer = QLabel("JP INGENIERÍA Y SERVICIOS S.R.L.\nPrototipo visual · Versión B")
        footer.setObjectName("sidebarFooter")
        footer.setContentsMargins(10, 15, 10, 0)
        footer.setWordWrap(True)
        layout.addWidget(footer)
        return sidebar

    @staticmethod
    def _menu_caption(text):
        label = QLabel(text)
        label.setObjectName("menuCaption")
        return label

    @staticmethod
    def _nav_button(icon, text, active=False):
        button = QPushButton(f"{icon}    {text}")
        button.setObjectName("navButton")
        button.setProperty("active", "true" if active else "false")
        button.setCursor(Qt.CursorShape.ArrowCursor)
        button.setMinimumHeight(40)
        # Intencionalmente no se conecta ninguna acción: es una maqueta visual.
        return button

    def _build_topbar(self):
        bar = QFrame()
        bar.setObjectName("topbar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(17, 11, 17, 11)

        breadcrumb = QLabel("JP /  Panel general")
        breadcrumb.setObjectName("muted")
        layout.addWidget(breadcrumb)
        layout.addStretch(1)

        status = QLabel("●  Entorno de demostración")
        status.setStyleSheet(
            "color:#23845F;background:#EAF7F1;border-radius:12px;"
            "padding:7px 10px;font-size:10px;font-weight:700;"
        )
        layout.addWidget(status)
        layout.addSpacing(13)

        avatar = QLabel("AC")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFixedSize(35, 35)
        avatar.setStyleSheet(
            "background:#E9EEF8;color:#29466B;border-radius:17px;"
            "font-size:11px;font-weight:800;"
        )
        user_text = QVBoxLayout()
        user_text.setSpacing(1)
        user_name = QLabel("Asistente Comercial")
        user_name.setStyleSheet("font-size:11px;font-weight:750;color:#27364A;")
        user_role = QLabel("Usuario de demostración")
        user_role.setStyleSheet("font-size:9px;color:#8994A4;")
        user_text.addWidget(user_name)
        user_text.addWidget(user_role)
        layout.addWidget(avatar)
        layout.addSpacing(8)
        layout.addLayout(user_text)
        return bar

    def _build_page_heading(self):
        wrapper = QWidget()
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        left = QVBoxLayout()
        left.setSpacing(5)
        title = QLabel("Panel general")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Resumen de la actividad comercial y las cotizaciones registradas.")
        subtitle.setObjectName("muted")
        left.addWidget(title)
        left.addWidget(subtitle)
        layout.addLayout(left)
        layout.addStretch(1)
        button = QPushButton("＋  Nueva cotización")
        button.setObjectName("primaryButton")
        button.setMinimumHeight(39)
        button.setCursor(Qt.CursorShape.ArrowCursor)
        # Botón visual sin acción en esta versión.
        layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignVCenter)
        return wrapper

    def _build_metrics(self):
        row = QHBoxLayout()
        row.setSpacing(14)
        metrics = [
            ("COTIZACIONES EMITIDAS", "128", "Total acumulado de demostración", "▤", "#EAF1FC", "#4169A8"),
            ("EN REVISIÓN", "14", "Propuestas por revisar", "◷", "#FFF5E5", "#C58A2A"),
            ("APROBADAS", "76", "Propuestas aceptadas", "✓", "#E8F7F0", "#23966B"),
            ("PRÓXIMAS A VENCER", "08", "Dentro de su vigencia", "◷", "#FCEEEE", "#C65F5F"),
        ]
        for label, value, note, symbol, bg, fg in metrics:
            row.addWidget(self._metric_card(label, value, note, symbol, bg, fg), 1)
        return row

    @staticmethod
    def _metric_card(label_text, value_text, note_text, symbol, icon_bg, icon_fg):
        card = QFrame()
        card.setObjectName("metricCard")
        card.setMinimumHeight(135)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(17, 15, 17, 14)
        layout.setSpacing(7)

        top = QHBoxLayout()
        label = QLabel(label_text)
        label.setObjectName("metricLabel")
        icon = QLabel(symbol)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setFixedSize(31, 31)
        icon.setStyleSheet(
            f"background:{icon_bg};color:{icon_fg};border-radius:9px;"
            "font-size:15px;font-weight:800;"
        )
        top.addWidget(label, 1)
        top.addWidget(icon)
        value = QLabel(value_text)
        value.setObjectName("metricValue")
        note = QLabel(note_text)
        note.setObjectName("metricNote")
        layout.addLayout(top)
        layout.addWidget(value)
        layout.addWidget(note)
        return card

    def _build_main_content(self):
        row = QHBoxLayout()
        row.setSpacing(15)
        row.addWidget(self._build_quotes_card(), 7)
        row.addWidget(self._build_side_panel(), 3)
        return row

    def _build_quotes_card(self):
        card = QFrame()
        card.setObjectName("contentCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 17, 18, 15)
        layout.setSpacing(12)

        heading = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(3)
        title = QLabel("Cotizaciones recientes")
        title.setObjectName("sectionTitle")
        hint = QLabel("Registros de ejemplo para visualizar la presentación del módulo.")
        hint.setObjectName("sectionHint")
        title_box.addWidget(title)
        title_box.addWidget(hint)
        heading.addLayout(title_box)
        heading.addStretch(1)
        all_button = QPushButton("Ver todas")
        all_button.setObjectName("secondaryButton")
        all_button.setCursor(Qt.CursorShape.ArrowCursor)
        heading.addWidget(all_button, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addLayout(heading)

        table = QTableWidget(6, 5)
        table.setHorizontalHeaderLabels(["N° COTIZACIÓN", "CLIENTE", "FECHA", "IMPORTE", "ESTADO"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        table.setShowGrid(False)
        table.setAlternatingRowColors(False)
        table.setMinimumHeight(370)
        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        table.verticalHeader().setDefaultSectionSize(53)

        sample_rows = [
            ("JP.260900014", "Servicios Mineros del Sur S.A.C.", "08/09/2026", "S/ 18,450.00", "Enviada"),
            ("JP.260900013", "Clínica San Gabriel", "07/09/2026", "S/  7,820.00", "Aprobada"),
            ("JP.260900012", "Industrias del Pacífico S.R.L.", "06/09/2026", "S/ 12,600.00", "En revisión"),
            ("JP.260900011", "Corporación Andina E.I.R.L.", "05/09/2026", "S/  4,350.00", "Rechazada"),
            ("JP.260900010", "Hotel Los Portales", "04/09/2026", "S/  9,780.00", "Aprobada"),
            ("JP.260900009", "Constructora del Valle S.A.C.", "03/09/2026", "S/ 21,300.00", "Enviada"),
        ]
        status_colors = {
            "Enviada": ("#EAF1FC", "#4169A8"),
            "Aprobada": ("#E8F7F0", "#23845F"),
            "En revisión": ("#FFF5E5", "#A97520"),
            "Rechazada": ("#FCEEEE", "#B84F4F"),
        }
        for r, values in enumerate(sample_rows):
            for c, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                if c == 0:
                    item.setForeground(Qt.GlobalColor.darkBlue)
                    item.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
                elif c == 3:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    item.setForeground(Qt.GlobalColor.darkGray)
                elif c == 2:
                    item.setForeground(Qt.GlobalColor.gray)
                if c == 4:
                    bg, fg = status_colors[value]
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setBackground(Qt.GlobalColor.white)
                    item.setForeground(Qt.GlobalColor.white)
                    table.setItem(r, c, item)
                    pill = QLabel(value)
                    pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    pill.setStyleSheet(
                        f"background:{bg};color:{fg};border-radius:9px;"
                        "padding:5px 8px;font-size:9px;font-weight:750;"
                    )
                    table.setCellWidget(r, c, pill)
                else:
                    table.setItem(r, c, item)
        layout.addWidget(table, 1)

        footer = QLabel("Vista ilustrativa · Los registros y montos mostrados son ficticios.")
        footer.setStyleSheet("color:#98A2B1;font-size:10px;")
        layout.addWidget(footer)
        return card

    def _build_side_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        distribution = QFrame()
        distribution.setObjectName("contentCard")
        d_layout = QVBoxLayout(distribution)
        d_layout.setContentsMargins(16, 16, 16, 17)
        d_layout.setSpacing(13)
        d_title = QLabel("Estado de cotizaciones")
        d_title.setObjectName("sectionTitle")
        d_hint = QLabel("Distribución referencial")
        d_hint.setObjectName("sectionHint")
        d_layout.addWidget(d_title)
        d_layout.addWidget(d_hint)

        bars = [
            ("Aprobadas", 59, "76", "#2CB889"),
            ("Enviadas", 22, "28", "#5D8CCB"),
            ("En revisión", 11, "14", "#E0A23B"),
            ("Otros estados", 8, "10", "#A0A9B7"),
        ]
        for name, value, count, color in bars:
            line = QHBoxLayout()
            label = QLabel(name)
            label.setStyleSheet("font-size:10px;color:#637084;font-weight:600;")
            number = QLabel(count)
            number.setStyleSheet("font-size:10px;color:#26364A;font-weight:750;")
            line.addWidget(label)
            line.addStretch(1)
            line.addWidget(number)
            d_layout.addLayout(line)
            progress = QProgressBar()
            progress.setRange(0, 100)
            progress.setValue(value)
            progress.setTextVisible(False)
            progress.setStyleSheet(
                f"QProgressBar::chunk{{background:{color};border-radius:4px;}}"
            )
            d_layout.addWidget(progress)
        layout.addWidget(distribution)

        shortcuts = QFrame()
        shortcuts.setObjectName("contentCard")
        s_layout = QVBoxLayout(shortcuts)
        s_layout.setContentsMargins(16, 16, 16, 16)
        s_layout.setSpacing(10)
        s_title = QLabel("Accesos del sistema")
        s_title.setObjectName("sectionTitle")
        s_hint = QLabel("Secciones disponibles en el diseño")
        s_hint.setObjectName("sectionHint")
        s_layout.addWidget(s_title)
        s_layout.addWidget(s_hint)
        for icon, label in [
            ("＋", "Registrar cliente"),
            ("▤", "Crear cotización"),
            ("▣", "Consultar catálogo"),
        ]:
            shortcut = QPushButton(f"{icon}    {label}                          ›")
            shortcut.setObjectName("secondaryButton")
            shortcut.setMinimumHeight(36)
            shortcut.setCursor(Qt.CursorShape.ArrowCursor)
            # Accesos representativos, todavía sin navegación implementada.
            s_layout.addWidget(shortcut)
        layout.addWidget(shortcuts)

        note = QFrame()
        note.setStyleSheet(
            "QFrame{background:#EDF5FF;border:1px solid #DDEBFA;border-radius:11px;}"
        )
        n_layout = QVBoxLayout(note)
        n_layout.setContentsMargins(14, 12, 14, 12)
        note_title = QLabel("Versión B · Prototipo")
        note_title.setStyleSheet("color:#315C8C;font-size:11px;font-weight:800;")
        note_text = QLabel(
            "Interfaz estática para validar la distribución visual. "
            "Aún no guarda datos ni se conecta a la base de datos."
        )
        note_text.setWordWrap(True)
        note_text.setStyleSheet("color:#58718D;font-size:10px;line-height:1.4;")
        n_layout.addWidget(note_title)
        n_layout.addWidget(note_text)
        layout.addWidget(note)
        layout.addStretch(1)
        return panel


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Sistema de Cotizaciones JP")
    app.setStyle("Fusion")
    window = CotizacionesJPWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
