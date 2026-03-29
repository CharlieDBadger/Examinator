#!/usr/bin/env python3
"""
EXAM GENERATOR  v1.0  —  PyQt6
Herramienta para crear archivos de preguntas (.json)
compatibles con Exam Simulator.

Dependencia:
    pip install PyQt6
"""

import json
import re
import sys
import subprocess
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QLineEdit, QTextEdit, QRadioButton, QButtonGroup,
    QScrollArea, QSizePolicy, QMessageBox, QFileDialog,
    QComboBox,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon

APP_VERSION   = "1.1"
BANK_DIR_NAME = "questions_bank"

# ── Límites de caracteres ─────────────────────────────────────────────────────
MAX_TITLE       = 80
MAX_DESC        = 300
MAX_QUESTION    = 500
MAX_OPTION      = 200
MAX_EXPLANATION = 400
MAX_CATEGORY    = 60
MIN_OPTIONS     = 2
MAX_OPTIONS     = 6

# ── Paleta ────────────────────────────────────────────────────────────────────
C = dict(
    bg      = "#f4f6f9",
    surf    = "#ffffff",
    surf2   = "#edf0f4",
    border  = "#d0d7e2",
    border2 = "#b8c2d4",
    acc     = "#2563eb",
    acc_l   = "#eff4ff",
    acc_d   = "#1d4ed8",
    ok      = "#2db84d",
    ok_l    = "#edfff1",
    err     = "#e05a47",
    err_l   = "#fff1ee",
    warn    = "#c9961a",
    warn_l  = "#fffaeb",
    text    = "#111827",
    text2   = "#4b5563",
    text3   = "#9ca3af",
)

QSS = """
* { font-family: "Segoe UI", "SF Pro Text", "Helvetica Neue", sans-serif; font-size: 13px; }
QMainWindow, QWidget { background: %(bg)s; color: %(text)s; }
QWidget { background: transparent; }
QMainWindow QWidget { background: %(bg)s; }

QScrollArea { border: none; }
QScrollBar:vertical { background: %(surf2)s; width: 7px; border-radius: 4px; }
QScrollBar::handle:vertical { background: %(border2)s; border-radius: 4px; min-height: 28px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { height: 0; }

QLineEdit {
    background: %(surf)s; color: %(text)s; border: 1px solid %(border)s;
    border-radius: 7px; padding: 8px 12px; selection-background-color: %(acc_l)s;
}
QLineEdit:focus { border-color: %(acc)s; }
QLineEdit:disabled { background: %(surf2)s; color: %(text3)s; }

QTextEdit {
    background: %(surf)s; color: %(text)s; border: 1px solid %(border)s;
    border-radius: 7px; padding: 8px 12px; selection-background-color: %(acc_l)s;
}
QTextEdit:focus { border-color: %(acc)s; }

QRadioButton { color: %(text)s; spacing: 8px; }
QRadioButton::indicator {
    width: 16px; height: 16px; border-radius: 8px;
    border: 1.5px solid %(border2)s; background: %(surf)s;
}
QRadioButton::indicator:checked { background: %(acc)s; border-color: %(acc)s; }
QRadioButton::indicator:hover { border-color: %(acc)s; }

QPushButton {
    background: %(surf)s;
    color: %(text2)s;
    border: 1px solid %(border)s;
    border-radius: 7px;
    padding: 8px 22px;
    font-weight: 500;
}
QPushButton:hover {
    border-color: %(acc)s;
    color: %(acc)s;
    background: %(acc_l)s;
}
QPushButton:pressed { background: %(surf2)s; }
QPushButton:disabled {
    color: %(text3)s;
    border-color: %(border)s;
    background: %(surf2)s;
}

QPushButton[cls="primary"] {
    background: %(acc)s;
    color: #ffffff;
    border: none;
    font-weight: 700;
    padding: 9px 28px;
    border-radius: 7px;
}
QPushButton[cls="primary"]:hover { background: %(acc_d)s; }
QPushButton[cls="primary"]:pressed { background: %(acc_d)s; }
QPushButton[cls="primary"]:disabled {
    background: %(surf2)s;
    color: %(text3)s;
}

QPushButton[cls="danger"] {
    background: transparent;
    color: %(err)s;
    border: 1px solid %(err)s;
    border-radius: 7px;
}
QPushButton[cls="danger"]:hover {
    background: %(err_l)s;
    color: %(err)s;
}
QPushButton[cls="danger"]:disabled { color: %(text3)s; border-color: %(border)s; }

QPushButton[cls="ghost"] {
    background: transparent;
    color: %(text3)s;
    border: 1px solid %(border)s;
    border-radius: 7px;
}
QPushButton[cls="ghost"]:hover { color: %(text2)s; border-color: %(border2)s; background: %(surf2)s; }

QComboBox {
    background: %(surf)s; color: %(text)s; border: 1px solid %(border)s;
    border-radius: 7px; padding: 7px 12px; font-size: 13px; min-width: 160px;
}
QComboBox:focus { border-color: %(acc)s; }
QComboBox::drop-down { border: none; width: 28px; }
QComboBox QAbstractItemView {
    background: %(surf)s; border: 1px solid %(border)s; border-radius: 7px;
    selection-background-color: %(acc_l)s; selection-color: %(acc)s;
    outline: none; padding: 4px;
}

QMessageBox { background: %(surf)s; min-width: 440px; }
QMessageBox QLabel { border: none; background: transparent; color: %(text)s; }
QMessageBox QPushButton {
    min-width: 110px;
    background: %(surf)s;
    color: %(text2)s;
    border: 1px solid %(border)s;
    border-radius: 7px;
    padding: 8px 22px;
    font-weight: 500;
}
QMessageBox QPushButton:hover {
    border-color: %(acc)s;
    color: %(acc)s;
    background: %(acc_l)s;
}
QMessageBox QPushButton:pressed { background: %(surf2)s; }

QPushButton#del_opt {
    background: transparent;
    color: %(border)s;
    border: 1px solid %(border2)s;
    border-radius: 4px;
    font-size: 16px;
    font-weight: 700;
    padding: 0px;
}
QPushButton#del_opt:hover { background: transparent; color: %(err)s; }
QPushButton#del_opt:disabled { color: %(text3)s; background: transparent; }
QMessageBox { background: %(surf)s; min-width: 440px; }
QMessageBox QLabel { border: none; background: transparent; color: %(text)s; }
QMessageBox QPushButton {
    min-width: 130px; padding: 8px 20px; border-radius: 20px;
    background: %(surf2)s; color: %(text2)s; font-weight: 500; border: none;
}
QMessageBox QPushButton:hover { background: %(border)s; color: %(text)s; }
""" % C


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _script_dir() -> Path:
    """
    Devuelve el directorio del ejecutable tanto en modo script (.py)
    como empaquetado con PyInstaller (--onefile).
    """
    if getattr(sys, "frozen", False):
        # Ejecutando como .exe generado por PyInstaller
        return Path(sys.executable).resolve().parent
    # Ejecutando como script .py normal
    return Path(sys.argv[0]).resolve().parent


def _btn(text: str, cls: str = None, min_w: int = None) -> QPushButton:
    b = QPushButton(text)
    if cls:
        b.setProperty("cls", cls)
        b.style().unpolish(b); b.style().polish(b)
    if min_w:
        b.setMinimumWidth(min_w)
    return b


def _label(text: str = "", color: str = None, size: int = 13,
           bold: bool = False, align=None) -> QLabel:
    l = QLabel(text)
    l.setWordWrap(True)
    l.setOpenExternalLinks(False)  # seguridad: sin hipervínculos
    css = f"color: {color or C['text']}; font-size: {size}px;"
    if bold: css += " font-weight: 700;"
    l.setStyleSheet(css)
    if align: l.setAlignment(align)
    return l


def _sect(text: str) -> QLabel:
    """Renderiza etiqueta de sección. El * se pinta en rojo."""
    if "*" in text:
        base, _, _ = text.partition("*")
        rest = text[len(base)+1:]
        # Usar rich-text de Qt para colorear solo el asterisco
        html = (
            f'<span style="color:{C["text3"]};font-size:11px;font-weight:700;'
            f'letter-spacing:2px;text-transform:uppercase;">'
            f'{base.upper()}</span>'
            f'<span style="color:{C["err"]};font-size:12px;font-weight:700;"> *</span>'
            f'<span style="color:{C["text3"]};font-size:11px;font-weight:700;'
            f'letter-spacing:2px;"> {rest.strip().upper()}</span>' if rest.strip() else ""
        )
        l = QLabel()
        l.setTextFormat(Qt.TextFormat.RichText)
        l.setOpenExternalLinks(False)
        l.setText(
            f'<span style="color:{C["text3"]};font-size:11px;font-weight:700;'
            f'letter-spacing:2px;">{base.upper()}</span>'
            f'<span style="color:{C["err"]};font-size:12px;font-weight:700;"> *</span>'
            + (f'<span style="color:{C["text3"]};font-size:11px;font-weight:700;'
               f'letter-spacing:2px;">  {rest.strip().upper()}</span>' if rest.strip() else "")
        )
        return l
    l = QLabel(text.upper())
    l.setOpenExternalLinks(False)
    l.setStyleSheet(f"color: {C['text3']}; font-size: 11px; font-weight: 700; letter-spacing: 2px;")
    return l


def _hline() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet(f"background: {C['border']}; max-height: 1px; border: none;")
    return f


class ConfirmDialog(QWidget):
    """
    Diálogo de confirmación personalizado que respeta el QSS de la app.
    Uso:
        dlg = ConfirmDialog(parent, title, message, buttons)
        # buttons: list of (label, role)  role: "default"|"primary"|"danger"
        result = dlg.exec()   # devuelve el label del botón pulsado o None
    """
    def __init__(self, parent, title: str, message: str,
                 buttons: list[tuple[str, str]]):
        super().__init__(parent, Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint |
                         Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle(title)
        self.setMinimumWidth(420)
        self._result: str | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 20)
        root.setSpacing(0)

        msg_lbl = QLabel(message)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet(
            f"color: {C['text']}; font-size: 13px; "
            "background: transparent; border: none;"
        )
        root.addWidget(msg_lbl)
        root.addSpacing(22)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        for label, role in buttons:
            b = QPushButton(label)
            if role == "primary":
                b.setProperty("cls", "primary")
                b.style().unpolish(b); b.style().polish(b)
            elif role == "danger":
                b.setProperty("cls", "danger")
                b.style().unpolish(b); b.style().polish(b)
            b.clicked.connect(lambda _, l=label: self._pick(l))
            btn_row.addWidget(b)

        root.addLayout(btn_row)
        self.adjustSize()

    def _pick(self, label: str):
        self._result = label
        self.close()

    def exec(self) -> str | None:
        from PyQt6.QtWidgets import QApplication
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.show()
        while self.isVisible():
            QApplication.processEvents()
        return self._result


def _header_bar(title: str, subtitle: str = "",
                right_widget: QWidget = None) -> QFrame:
    """Barra de cabecera consistente con exam_simulator."""
    bar = QFrame()
    bar.setStyleSheet(
        f"QFrame {{ background: {C['surf']}; border-bottom: 1px solid {C['border']}; }}"
    )
    h_l = QHBoxLayout(bar)
    h_l.setContentsMargins(52, 28, 52, 28)
    h_l.setSpacing(0)

    accent = QFrame()
    accent.setFixedSize(4, 36)
    accent.setStyleSheet(f"background: {C['acc']}; border-radius: 2px; border: none;")

    col = QVBoxLayout()
    col.setSpacing(4)
    col.setContentsMargins(16, 0, 0, 0)
    col.addWidget(_label(title, C["text"], size=22, bold=True))
    if subtitle:
        col.addWidget(_label(subtitle, C["text3"], size=12))

    h_l.addWidget(accent)
    h_l.addLayout(col)
    h_l.addStretch()
    if right_widget:
        h_l.addWidget(right_widget)
    return bar


def _bottom_bar(*widgets) -> QFrame:
    """Barra inferior con separador."""
    bar = QFrame()
    bar.setStyleSheet(
        f"QFrame {{ background: {C['surf']}; border-top: 1px solid {C['border']}; }}"
    )
    l = QHBoxLayout(bar)
    l.setContentsMargins(52, 20, 52, 20)
    l.setSpacing(12)
    for w in widgets:
        if w is None:
            l.addStretch()
        else:
            l.addWidget(w)
    return bar


def _counter_label(current: int, maximum: int) -> QLabel:
    l = QLabel(f"{current} / {maximum}")
    l.setAlignment(Qt.AlignmentFlag.AlignRight)
    l.setStyleSheet(f"color: {C['text3']}; font-size: 11px; background: transparent;")
    return l


def _limit_textedit(widget: QTextEdit, max_chars: int, counter: QLabel):
    """Aplica límite de caracteres a QTextEdit y actualiza el contador."""
    def _on_change():
        t = widget.toPlainText()
        if len(t) > max_chars:
            cur = widget.textCursor()
            pos = cur.position()
            widget.blockSignals(True)
            widget.setPlainText(t[:max_chars])
            widget.blockSignals(False)
            cur.setPosition(min(pos, max_chars))
            widget.setTextCursor(cur)
        counter.setText(f"{len(widget.toPlainText())} / {max_chars}")
    widget.textChanged.connect(_on_change)


def sanitize_filename(title: str) -> str:
    """Convierte el título en un nombre de archivo .json válido."""
    name = title.strip()
    # Eliminar caracteres inválidos en Windows y Unix
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name)
    # Espacios → guión bajo
    name = re.sub(r'\s+', '_', name)
    # Solo alfanuméricos, guión bajo, guión
    name = re.sub(r'[^\w\-]', '', name, flags=re.ASCII)
    name = name[:MAX_TITLE]
    return name.lower() or "sin_titulo"


# ══════════════════════════════════════════════════════════════════════════════
#  EXAM DATA
# ══════════════════════════════════════════════════════════════════════════════

class ExamData:
    def __init__(self):
        self.title:          str        = ""
        self.description:    str        = ""
        self.questions:      list[dict] = []
        self.categories:     list[str]  = []
        self.use_difficulty: bool       = False
        self.source_path:    str        = ""   # ruta del JSON importado si aplica

    @property
    def is_empty(self) -> bool:
        return not self.questions

    def to_dict(self) -> dict:
        return {
            "title":       self.title,
            "description": self.description,
            "questions":   self.questions,
        }


# ══════════════════════════════════════════════════════════════════════════════
#  OPTION ROW
# ══════════════════════════════════════════════════════════════════════════════

class OptionRow(QFrame):
    text_changed   = pyqtSignal()
    delete_clicked = pyqtSignal()

    def __init__(self, key: str, text: str = ""):
        super().__init__()
        self._key = key
        self.setStyleSheet(
            f"QFrame {{ background: {C['surf2']}; border: 1px solid {C['border']}; "
            "border-radius: 8px; }}"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 9, 12, 9)
        layout.setSpacing(10)

        self.radio = QRadioButton()
        self.radio.setToolTip("Marcar como respuesta correcta")
        self.radio.setCursor(Qt.CursorShape.PointingHandCursor)
        self.radio.setToolTip("Marcar como correcta")
        self.radio.setStyleSheet(f"""
            QRadioButton {{ background: transparent; spacing: 0px; }}
            QRadioButton::indicator {{
                width: 22px; height: 22px; border-radius: 11px;
                border: 2.5px solid {C['border2']}; background: {C['surf']};
            }}
            QRadioButton::indicator:hover {{
                border-color: {C['ok']}; background: {C['ok_l']};
            }}
            QRadioButton::indicator:checked {{
                border: 2.5px solid {C['ok']};
                background: qradialgradient(
                    cx:0.5, cy:0.5, radius:0.5,
                    fx:0.5, fy:0.5,
                    stop:0 {C['ok']},
                    stop:0.45 {C['ok']},
                    stop:0.5 white,
                    stop:1 white
                );
            }}
        """)

        self._key_lbl = QLabel(key)
        self._key_lbl.setFixedWidth(18)
        self._key_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._key_lbl.setStyleSheet(
            f"color: {C['text2']}; font-weight: 700; font-size: 13px; "
            "background: transparent; border: none;"
        )

        self.edit = QLineEdit(text)
        self.edit.setMaxLength(MAX_OPTION)
        self.edit.setPlaceholderText(f"Texto de la opción {key}")
        self.edit.textChanged.connect(self.text_changed.emit)

        self._del_btn = QPushButton("✕")
        self._del_btn.setObjectName("del_opt")
        self._del_btn.setFixedSize(26, 26)
        self._del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._del_btn.clicked.connect(self.delete_clicked.emit)
        self._del_btn.hide()   # visible solo en hover

        layout.addWidget(self.radio)
        layout.addWidget(self._key_lbl)
        layout.addWidget(self.edit, 1)
        layout.addWidget(self._del_btn)

    @property
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, k: str):
        self._key = k
        self._key_lbl.setText(k)
        self.edit.setPlaceholderText(f"Texto de la opción {k}")

    @property
    def text(self) -> str:
        return self.edit.text()

    @property
    def is_selected(self) -> bool:
        return self.radio.isChecked()

    def set_delete_enabled(self, enabled: bool):
        self._del_btn.setEnabled(enabled)

    def enterEvent(self, event):
        if self._del_btn.isEnabled():
            self._del_btn.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._del_btn.hide()
        super().leaveEvent(event)


# ══════════════════════════════════════════════════════════════════════════════
#  QUESTION FORM
# ══════════════════════════════════════════════════════════════════════════════

class QuestionForm(QWidget):
    validity_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._option_rows: list[OptionRow] = []
        self._radio_group = QButtonGroup(self)
        self._radio_group.setExclusive(True)
        self._build_ui()
        # Iniciar con 2 opciones
        self._add_option_row()
        self._add_option_row()
        self._update_controls()

    # ── Construcción ─────────────────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # Categoría y Dificultad — en la misma fila, arriba a la derecha
        top_row = QHBoxLayout()
        top_row.setSpacing(24)

        cat_col = QVBoxLayout()
        cat_col.setSpacing(8)
        cat_col.addWidget(_sect("Categoría *"))
        self._cat_combo = QComboBox()
        self._cat_combo.setMinimumWidth(160)
        self._cat_combo.currentIndexChanged.connect(self._on_any_change)
        cat_col.addWidget(self._cat_combo)
        top_row.addLayout(cat_col, 1)

        # Dificultad: botones coloreados (ocultos hasta configure)
        self._diff_widget = QWidget()
        diff_inner = QVBoxLayout(self._diff_widget)
        diff_inner.setContentsMargins(0, 0, 0, 0)
        diff_inner.setSpacing(8)
        diff_inner.addWidget(_sect("Dificultad"))
        self._diff_btns_layout = QHBoxLayout()
        self._diff_btns_layout.setSpacing(6)
        self._diff_btn_group = QButtonGroup(self)
        self._diff_btn_group.setExclusive(True)
        self._diff_selected = "medium"
        for level in ("easy", "medium", "hard", "insane"):
            dc = DIFF_COLORS[level]
            b = QPushButton(level)
            b.setCheckable(True)
            b.setChecked(level == "medium")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setProperty("diff_level", level)
            b.setStyleSheet(
                f"QPushButton {{ background: {C['surf2']}; color: {C['text3']}; "
                f"border: 1px solid {C['border']}; border-radius: 6px; "
                "padding: 5px 12px; font-size: 11px; font-weight: 600; }}"
                f"QPushButton:checked {{ background: {dc['bg']}; color: {dc['fg']}; "
                f"border: 2px solid {dc['border']}; }}"
            )
            b.clicked.connect(lambda _, lv=level: self._on_diff_selected(lv))
            self._diff_btn_group.addButton(b)
            self._diff_btns_layout.addWidget(b)
        diff_inner.addLayout(self._diff_btns_layout)
        self._diff_widget.hide()
        top_row.addWidget(self._diff_widget)

        layout.addLayout(top_row)
        layout.addSpacing(10)

        # Pregunta
        layout.addWidget(_sect("Pregunta *"))
        self._q_edit = QTextEdit()
        self._q_edit.setAcceptRichText(False)
        self._q_edit.setPlaceholderText("Escribe aquí el enunciado de la pregunta...")
        self._q_edit.setFixedHeight(90)
        self._q_counter = _counter_label(0, MAX_QUESTION)
        _limit_textedit(self._q_edit, MAX_QUESTION, self._q_counter)
        self._q_edit.textChanged.connect(self._on_any_change)
        q_row = QHBoxLayout()
        q_row.addStretch()
        q_row.addWidget(self._q_counter)
        layout.addWidget(self._q_edit)
        layout.addLayout(q_row)

        # Respuestas
        layout.addWidget(_sect("Respuestas *"))
        instr = QLabel("◉  Marca el radio de la respuesta correcta")
        instr.setStyleSheet(
            f"color: {C['text3']}; font-size: 11px; background: transparent;"
        )
        layout.addWidget(instr)
        layout.addSpacing(4)

        self._opts_layout = QVBoxLayout()
        self._opts_layout.setSpacing(8)
        layout.addLayout(self._opts_layout)

        # Botón añadir opción
        self._add_opt_btn = QPushButton("＋  Añadir opción")
        self._add_opt_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._add_opt_btn.setStyleSheet(
            f"background: {C['acc_l']}; color: {C['acc']}; border: none; "
            "border-radius: 20px; padding: 7px 20px; font-weight: 600;"
        )
        self._add_opt_btn.clicked.connect(self._try_add_option)
        layout.addWidget(self._add_opt_btn)

        # Explicación
        layout.addWidget(_sect("Explicación de la respuesta correcta *"))
        self._exp_edit = QTextEdit()
        self._exp_edit.setAcceptRichText(False)
        self._exp_edit.setPlaceholderText(
            "Explica por qué la respuesta marcada es correcta..."
        )
        self._exp_edit.setFixedHeight(80)
        self._exp_counter = _counter_label(0, MAX_EXPLANATION)
        _limit_textedit(self._exp_edit, MAX_EXPLANATION, self._exp_counter)
        self._exp_edit.textChanged.connect(self._on_any_change)
        exp_row = QHBoxLayout()
        exp_row.addStretch()
        exp_row.addWidget(self._exp_counter)
        layout.addWidget(self._exp_edit)
        layout.addLayout(exp_row)

    # ── Gestión de opciones ───────────────────────────────────────────────────

    def _try_add_option(self):
        """Añade una opción solo si todas las existentes están rellenas y no hay duplicados."""
        for r in self._option_rows:
            if not r.text.strip():
                r.edit.setStyleSheet(
                    f"background: {C['err_l']}; color: {C['text']}; "
                    f"border: 1px solid {C['err']}; border-radius: 7px; padding: 8px 12px;"
                )
                r.edit.setFocus()
                return
        if self._has_duplicates():
            self._show_duplicate_warning()
            return
        self._add_option_row()

    def _has_duplicates(self) -> bool:
        texts = [r.text.strip().lower() for r in self._option_rows if r.text.strip()]
        return len(set(texts)) < len(texts)

    def _show_duplicate_warning(self):
        dlg = ConfirmDialog(
            self.window(),
            "Opciones repetidas",
            "Hay opciones con el mismo texto.\n\nCorrígelas antes de continuar.",
            [("Entendido", "primary")],
        )
        dlg.exec()

    def _add_option_row(self, text: str = ""):
        key = chr(ord('A') + len(self._option_rows))
        row = OptionRow(key, text)
        self._radio_group.addButton(row.radio)
        row.text_changed.connect(self._on_any_change)
        row.edit.textChanged.connect(lambda _, r=row: self._clear_option_error(r))
        row.delete_clicked.connect(lambda: self._remove_option_row(row))
        self._opts_layout.addWidget(row)
        self._option_rows.append(row)
        self._update_controls()
        self._on_any_change()

    def _remove_option_row(self, row: OptionRow):
        if len(self._option_rows) <= MIN_OPTIONS:
            return
        was_selected = row.is_selected
        self._radio_group.removeButton(row.radio)
        self._opts_layout.removeWidget(row)
        row.deleteLater()
        self._option_rows.remove(row)
        # Reasignar claves
        for i, r in enumerate(self._option_rows):
            r.key = chr(ord('A') + i)
        # Si la eliminada era la correcta, deseleccionar
        if was_selected:
            self._radio_group.setExclusive(False)
            for r in self._option_rows:
                r.radio.setChecked(False)
            self._radio_group.setExclusive(True)
        self._update_controls()
        self._on_any_change()

    def _clear_option_error(self, row):
        row.edit.setStyleSheet("")   # restaura el estilo del QSS global

    def _update_controls(self):
        n = len(self._option_rows)
        self._add_opt_btn.setVisible(n < MAX_OPTIONS)
        can_del = n > MIN_OPTIONS
        for r in self._option_rows:
            r.set_delete_enabled(can_del)

    # ── Validación y datos ────────────────────────────────────────────────────

    def _on_any_change(self):
        self._check_duplicates()
        self.validity_changed.emit(self.is_valid())

    def _check_duplicates(self):
        texts = [r.text.strip().lower() for r in self._option_rows if r.text.strip()]
        seen = set()
        duplicates = set()
        for t in texts:
            if t in seen:
                duplicates.add(t)
            seen.add(t)
        for r in self._option_rows:
            if r.text.strip().lower() in duplicates:
                r.edit.setStyleSheet(
                    f"background: {C['warn_l']}; color: {C['text']}; "
                    f"border: 1px solid {C['warn']}; border-radius: 7px; padding: 8px 12px;"
                )
            elif r.edit.styleSheet():  # limpiar si no hay error activo de vacío
                r.edit.setStyleSheet("")

    def is_valid(self) -> bool:
        if not self._q_edit.toPlainText().strip():
            return False
        filled = [r.text.strip() for r in self._option_rows if r.text.strip()]
        if len(filled) < MIN_OPTIONS:
            return False
        # Comprobar duplicados (case-insensitive)
        if len(set(t.lower() for t in filled)) < len(filled):
            return False
        if not any(r.is_selected and r.text.strip() for r in self._option_rows):
            return False
        if not self._exp_edit.toPlainText().strip():
            return False
        return True

    def _on_diff_selected(self, level: str):
        self._diff_selected = level
        self._on_any_change()

    def _selected_category(self) -> str:
        return self._cat_combo.currentText() or "default"

    def get_data(self) -> dict:
        options = {}
        correct = ""
        for r in self._option_rows:
            if r.text.strip():
                options[r.key] = r.text.strip()
            if r.is_selected:
                correct = r.key
        cat = self._selected_category()
        data: dict = {"category": cat}
        if self._diff_widget.isVisible():
            data["difficulty"] = self._diff_selected
        data["question"]    = self._q_edit.toPlainText().strip()
        data["options"]     = options
        data["correct"]     = correct
        data["explanation"] = self._exp_edit.toPlainText().strip()
        return data

    def set_data(self, data: dict):
        """Carga una pregunta existente en el formulario."""
        self._q_edit.setPlainText(data.get("question", ""))
        self._exp_edit.setPlainText(data.get("explanation", ""))
        cat = data.get("category", "default")
        idx = self._cat_combo.findText(cat)
        if idx >= 0:
            self._cat_combo.setCurrentIndex(idx)
        # Dificultad
        if data.get("difficulty") and self._diff_widget.isVisible():
            self._diff_selected = data["difficulty"]
            for btn in self._diff_btn_group.buttons():
                if btn.property("diff_level") == data["difficulty"]:
                    btn.setChecked(True)
                    break

        # Limpiar opciones actuales
        for r in self._option_rows[:]:
            self._radio_group.removeButton(r.radio)
            self._opts_layout.removeWidget(r)
            r.deleteLater()
        self._option_rows.clear()

        options = data.get("options", {})
        correct = data.get("correct", "")
        for key, text in options.items():
            self._add_option_row(text)

        # Seleccionar correcta
        for r in self._option_rows:
            if r.key == correct:
                r.radio.setChecked(True)
                break

        self._update_controls()
        self._on_any_change()

    def clear(self):
        self._q_edit.clear()
        self._exp_edit.clear()
        if self._cat_combo.count() > 0:
            self._cat_combo.setCurrentIndex(0)
        # Reset dificultad a medium
        self._diff_selected = "medium"
        for btn in self._diff_btn_group.buttons():
            btn.setChecked(btn.property("diff_level") == "medium")
        for r in self._option_rows[:]:
            self._radio_group.removeButton(r.radio)
            self._opts_layout.removeWidget(r)
            r.deleteLater()
        self._option_rows.clear()
        self._add_option_row()
        self._add_option_row()
        self._update_controls()


    def configure(self, categories: list, use_difficulty: bool):
        self._cat_combo.clear()
        for cat in categories:
            self._cat_combo.addItem(cat)
        self._diff_widget.setVisible(use_difficulty)
        self._on_any_change()

    def is_valid(self) -> bool:
        if self._cat_combo.count() == 0:
            return False
        if not self._q_edit.toPlainText().strip():
            return False
        filled = [r.text.strip() for r in self._option_rows if r.text.strip()]
        if len(filled) < MIN_OPTIONS:
            return False
        if len(set(t.lower() for t in filled)) < len(filled):
            return False
        if not any(r.is_selected and r.text.strip() for r in self._option_rows):
            return False
        if not self._exp_edit.toPlainText().strip():
            return False
        return True


# ══════════════════════════════════════════════════════════════════════════════
#  PANTALLA 0: HOME
# ══════════════════════════════════════════════════════════════════════════════

class AIPromptDialog(QWidget):
    """Ventana con prompt listo para copiar y guia de uso."""

    PROMPT = (
        "Eres un asistente especializado en crear examenes de seleccion multiple. "
        "Cuando el usuario te hable, primero preguntale:\n\n"
        "\u00bfQuieres que genere un examen a partir de preguntas que ya tienes, "
        "o prefieres que lo cree yo a partir de una tematica que me indiques?\n\n"
        "- Si tiene preguntas: pidele que las pegue en el chat. "
        "Extrae la pregunta, las opciones, la respuesta correcta y la explicacion. "
        "Si no especifica cual es la correcta o la explicacion, infierelas tu.\n\n"
        "- Si quiere que tu lo generes: preguntale el tema, el nivel aproximado "
        "y cuantas preguntas quiere.\n\n"
        "En ambos casos, cuando tengas toda la informacion, responde UNICAMENTE "
        "con el resultado dentro de un bloque de codigo markdown con etiqueta json, "
        "exactamente asi:\n\n"
        "```json\n"
        "{ ... el JSON aqui ... }\n"
        "```\n\n"
        "Sin ningun texto adicional antes ni despues del bloque. "
        "IMPORTANTE: No uses ninguna funcionalidad propia de generacion de tests o cuestionarios. "
        "No respondas con formularios, interfaces ni herramientas integradas. "
        "Tu unica tarea es devolver el bloque de codigo JSON con el formato indicado. Nada mas.\n\n"
        "El formato exacto del JSON debe ser:\n\n"
        "{\n"
        "  \"title\": \"Titulo del examen\",\n"
        "  \"description\": \"Descripcion breve del contenido\",\n"
        "  \"questions\": [\n"
        "    {\n"
        "      \"category\": \"Tema de la pregunta\",\n"
        "      \"difficulty\": \"medium\",\n"
        "      \"question\": \"Texto de la pregunta\",\n"
        "      \"options\": { \"A\": \"...\", \"B\": \"...\", \"C\": \"...\", \"D\": \"...\" },\n"
        "      \"correct\": \"A\",\n"
        "      \"explanation\": \"Por que esta opcion es la correcta\"\n"
        "    }\n"
        "  ]\n"
        "}"
    )

    STEPS = (
        "Una vez que la IA te devuelva el resultado, sigue estos pasos:\n\n"
        "1.  Copia todo el texto que te haya dado — empieza por { y termina por }\n"
        "2.  Abre el Bloc de notas (Windows) o TextEdit (Mac)\n"
        "3.  Pega el texto ahi\n"
        "4.  Ve a  Archivo \u2192 Guardar como\n"
        "5.  En el nombre escribe lo que quieras seguido de  .json\n"
        "       Por ejemplo:  mi_examen.json\n"
        "6.  Guardalo dentro de la carpeta  questions_bank  que esta junto al simulador\n"
        "7.  Vuelve al Exam Simulator, pulsa  \U0001f504 Refresh  y ya aparecera en el listado"
    )

    def __init__(self, parent):
        super().__init__(parent, Qt.WindowType.Dialog |
                         Qt.WindowType.WindowTitleHint |
                         Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("Generar examen con IA")
        self.setMinimumWidth(640)
        self.setMinimumHeight(560)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(_header_bar(
            "Generar con IA",
            "Copia el prompt y usalo en ChatGPT, Claude, Gemini o cualquier IA"
        ))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"background: {C['bg']}; border: none;")

        content = QWidget()
        content.setStyleSheet(f"background: {C['bg']};")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(36, 32, 36, 32)
        cl.setSpacing(20)

        # Seccion 1: Prompt
        cl.addWidget(_sect("Paso 1 — Copia este prompt y pegalo en tu IA"))

        prompt_frame = QFrame()
        prompt_frame.setStyleSheet(
            f"QFrame {{ background: {C['surf']}; border: 1px solid {C['border']}; "
            "border-radius: 10px; }}"
        )
        pf_l = QVBoxLayout(prompt_frame)
        pf_l.setContentsMargins(20, 16, 20, 16)
        pf_l.setSpacing(12)

        prompt_text = self.PROMPT.replace("\\n", "\n")
        prompt_lbl = QLabel(prompt_text)
        prompt_lbl.setWordWrap(True)
        prompt_lbl.setOpenExternalLinks(False)
        prompt_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        prompt_lbl.setStyleSheet(
            f"color: {C['text2']}; font-size: 12px; "
            "background: transparent; border: none;"
        )
        pf_l.addWidget(prompt_lbl)

        self._btn_copy = QPushButton("\U0001f4cb  Copiar prompt")
        self._btn_copy.setStyleSheet(
            f"background: {C['acc']}; color: #ffffff; border: none; "
            "border-radius: 7px; padding: 9px 28px; font-weight: 700; font-size: 13px;"
        )
        self._btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_copy.clicked.connect(self._copy_prompt)
        copy_row = QHBoxLayout()
        copy_row.addStretch()
        copy_row.addWidget(self._btn_copy)
        pf_l.addLayout(copy_row)
        cl.addWidget(prompt_frame)

        # Seccion 2: Instrucciones
        cl.addWidget(_sect("Paso 2 — Guarda el resultado como archivo"))

        steps_frame = QFrame()
        steps_frame.setStyleSheet(
            f"QFrame {{ background: {C['surf']}; border: 1px solid {C['border']}; "
            "border-radius: 10px; }}"
        )
        sf_l = QVBoxLayout(steps_frame)
        sf_l.setContentsMargins(20, 16, 20, 16)

        steps_text = self.STEPS.replace("\\n", "\n")
        steps_lbl = QLabel(steps_text)
        steps_lbl.setWordWrap(True)
        steps_lbl.setOpenExternalLinks(False)
        steps_lbl.setStyleSheet(
            f"color: {C['text']}; font-size: 13px; "
            "background: transparent; border: none;"
        )
        sf_l.addWidget(steps_lbl)
        cl.addWidget(steps_frame)
        cl.addStretch()

        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        btn_close = _btn("Cerrar")
        btn_close.clicked.connect(self.close)
        root.addWidget(_bottom_bar(None, btn_close))

    def _copy_prompt(self):
        text = self.PROMPT.replace("\\n", "\n")
        QApplication.clipboard().setText(text)
        self._btn_copy.setText("\u2714  Copiado!")
        QTimer.singleShot(2000, lambda: self._btn_copy.setText("\U0001f4cb  Copiar prompt"))

    def show_centered(self):
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        if self.parent():
            pg = self.parent().geometry()
            self.move(
                pg.x() + (pg.width()  - self.width())  // 2,
                pg.y() + (pg.height() - self.height()) // 2,
            )
        self.show()


# Colores de dificultad (usados en config, editor y revisión)
DIFF_COLORS = {
    "easy":   {"fg": "#16a34a", "bg": "#edfff1", "border": "#16a34a"},
    "medium": {"fg": "#b45309", "bg": "#fffbeb", "border": "#d97706"},
    "hard":   {"fg": "#e05a47", "bg": "#fff1ee", "border": "#e05a47"},
    "insane": {"fg": "#9d174d", "bg": "#fdf2f8", "border": "#be185d"},
}


class ToggleSwitch(QWidget):
    """Switch pill."""
    toggled = pyqtSignal(bool)
    def __init__(self, checked=True, parent=None):
        super().__init__(parent)
        self._checked = checked
        self.setFixedSize(48, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    def isChecked(self): return self._checked
    def setChecked(self, val):
        self._checked = val; self.update()
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._checked = not self._checked
            self.toggled.emit(self._checked); self.update()
    def paintEvent(self, event):
        from PyQt6.QtGui import QPainter, QColor, QPainterPath
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height(); r = h / 2
        track = QColor(C["ok"]) if self._checked else QColor(C["border2"])
        path = QPainterPath(); path.addRoundedRect(0, 0, w, h, r, r)
        p.fillPath(path, track)
        pad = 3; thumb_x = w - h + pad if self._checked else pad
        p.setBrush(QColor("white")); p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(thumb_x), pad, h - pad*2, h - pad*2); p.end()


class ExamConfigScreen(QWidget):
    confirmed = pyqtSignal(list, bool)
    back      = pyqtSignal()
    discard   = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._categories: list[str] = []
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(_header_bar("Configurar examen",
                                   "Define las categorias y opciones antes de empezar"))
        body = QWidget()
        body.setStyleSheet(f"background: {C['bg']};")
        body_l = QVBoxLayout(body)
        body_l.setContentsMargins(52, 36, 52, 36)
        body_l.setSpacing(0)

        # ── Categorias ────────────────────────────────────────────────────────
        cat_hdr = QHBoxLayout()
        cat_sect = _sect("Categorias *")
        cat_min  = QLabel("Minimo 1")
        cat_min.setStyleSheet(f"color: {C['text3']}; font-size: 11px; background: transparent;")
        cat_hdr.addWidget(cat_sect)
        cat_hdr.addSpacing(8)
        cat_hdr.addWidget(cat_min)
        cat_hdr.addStretch()
        body_l.addLayout(cat_hdr)
        body_l.addSpacing(10)

        add_row = QHBoxLayout()
        add_row.setSpacing(10)
        self._cat_input = QLineEdit()
        self._cat_input.setMaxLength(MAX_CATEGORY)
        self._cat_input.setPlaceholderText("Nombre de la categoria...")
        self._cat_input.returnPressed.connect(self._add_category)
        add_row.addWidget(self._cat_input, 1)
        btn_add = _btn("Anadir")
        btn_add.clicked.connect(self._add_category)
        add_row.addWidget(btn_add)
        body_l.addLayout(add_row)
        body_l.addSpacing(12)

        # Contenedor de lista — mismo ancho que el input
        self._cat_list_layout = QVBoxLayout()
        self._cat_list_layout.setSpacing(6)
        body_l.addLayout(self._cat_list_layout)

        self._no_cats_lbl = _label("Anade al menos una categoria para continuar.", C["text3"], size=12)
        body_l.addWidget(self._no_cats_lbl)
        body_l.addSpacing(28)

        # ── Dificultad ────────────────────────────────────────────────────────
        body_l.addWidget(_hline())
        body_l.addSpacing(20)
        body_l.addWidget(_sect("Niveles de dificultad"))
        body_l.addSpacing(10)

        diff_row = QHBoxLayout()
        diff_row.setSpacing(10)
        diff_lbl = _label("Activar insercion de niveles de dificultad", C["text"], size=13)
        diff_lbl.setWordWrap(False)
        self._diff_toggle = ToggleSwitch(checked=True)
        self._diff_toggle.toggled.connect(self._on_toggle)
        diff_row.addWidget(diff_lbl)
        diff_row.addWidget(self._diff_toggle)
        diff_row.addStretch()
        body_l.addLayout(diff_row)
        body_l.addSpacing(6)

        self._off_warn = _label(
            "Advertencia: sin niveles de dificultad este examen no sera compatible con Chronicator.",
            C["err"], size=12
        )
        self._off_warn.hide()
        body_l.addWidget(self._off_warn)
        body_l.addSpacing(10)

        badges_row = QHBoxLayout()
        badges_row.setSpacing(8)
        for level in ("easy", "medium", "hard", "insane"):
            dc = DIFF_COLORS[level]
            b = QLabel(level)
            b.setStyleSheet(
                f"color: {dc['fg']}; background: {dc['bg']}; "
                f"border: 1px solid {dc['border']}; border-radius: 5px; "
                "padding: 3px 10px; font-size: 11px; font-weight: 700;"
            )
            badges_row.addWidget(b)
        badges_row.addStretch()
        body_l.addLayout(badges_row)
        body_l.addStretch()
        root.addWidget(body, 1)

        self._btn_back     = _btn("Volver")
        self._btn_continue = _btn("Continuar", cls="primary", min_w=160)
        self._btn_back.clicked.connect(self.back.emit)
        self._btn_continue.clicked.connect(self._on_continue)
        self._btn_continue.setEnabled(False)
        root.addWidget(_bottom_bar(None, self._btn_back, self._btn_continue))

    def _add_category(self):
        text = self._cat_input.text().strip()
        if not text:
            return
        if text.lower() in [c.lower() for c in self._categories]:
            self._cat_input.setStyleSheet(
                f"background: {C['warn_l']}; border: 1px solid {C['warn']}; "
                "border-radius: 7px; padding: 7px 12px;"
            )
            return
        self._cat_input.setStyleSheet("")
        self._cat_input.clear()
        self._categories.append(text)
        self._rebuild_list()

    def _remove_category(self, name: str):
        self._categories = [c for c in self._categories if c != name]
        self._rebuild_list()

    def _rebuild_list(self, counters=None):
        while self._cat_list_layout.count():
            item = self._cat_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        has = bool(self._categories)
        self._no_cats_lbl.setVisible(not has)
        self._btn_continue.setEnabled(has)
        for cat in self._categories:
            row = QFrame()
            row.setStyleSheet(
                f"QFrame {{ background: {C['surf']}; border: 1px solid {C['border']}; "
                "border-radius: 7px; }}"
            )
            rl = QHBoxLayout(row)
            rl.setContentsMargins(14, 8, 8, 8)
            rl.setSpacing(10)
            lbl = QLabel(cat)
            lbl.setStyleSheet(
                f"color: {C['text']}; font-size: 13px; background: transparent; border: none;"
            )
            rl.addWidget(lbl, 1)
            if counters and cat in counters:
                n = counters[cat]
                cnt = QLabel(f"{n} p")
                cnt.setStyleSheet(
                    f"color: {C['acc']}; font-size: 11px; font-weight: 600; "
                    "background: transparent; border: none;"
                )
                rl.addWidget(cnt)
            btn_del = QPushButton("x")
            btn_del.setObjectName("del_opt")
            btn_del.setFixedSize(26, 26)
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.clicked.connect(lambda _, c=cat: self._remove_category(c))
            rl.addWidget(btn_del)
            wrap = QHBoxLayout()
            wrap.setContentsMargins(0, 0, 0, 0)
            wrap.addWidget(row, 1)
            wrap.addSpacing(80)
            self._cat_list_layout.addLayout(wrap)

    def update_counters(self, questions):
        from collections import Counter
        c = Counter(q.get('category', 'default') for q in questions)
        self._rebuild_list(counters=dict(c))

    def _on_toggle(self, checked: bool):
        self._off_warn.setVisible(not checked)

    def _on_continue(self):
        if not self._categories:
            return
        self.confirmed.emit(self._categories[:], self._diff_toggle.isChecked())

    def load_from_json(self, questions: list[dict], force_difficulty: bool = False):
        cats, has_diff = [], False
        for q in questions:
            cat = q.get("category", "")
            if cat and cat != "default" and cat not in cats:
                cats.append(cat)
            if q.get("difficulty"):
                has_diff = True
        if not cats:
            cats = ["General"]
        self._categories = cats
        self._rebuild_list()
        # Si viene del Simulator forzar dificultad ON, si no respetar lo que tiene el JSON
        diff_on = True if force_difficulty else has_diff
        self._diff_toggle.setChecked(diff_on)
        self._off_warn.setVisible(not diff_on)
        self._btn_continue.setEnabled(True)

    def reset(self):
        self._categories = []
        self._cat_input.clear()
        self._cat_input.setStyleSheet("")
        self._rebuild_list()
        self._diff_toggle.setChecked(True)
        self._off_warn.hide()


class HomeScreen(QWidget):
    start          = pyqtSignal(str, str)   # title, description
    back_simulator = pyqtSignal()
    import_json    = pyqtSignal(dict)        # data dict del JSON importado

    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        back_btn = _btn("← Simulador", cls="ghost")
        back_btn.clicked.connect(self.back_simulator.emit)
        root.addWidget(_header_bar("Nuevo examen", f"Exam Generator  v{APP_VERSION}",
                                   right_widget=back_btn))

        # Cuerpo
        body = QWidget()
        body.setStyleSheet(f"background: {C['bg']};")
        body_l = QVBoxLayout(body)
        body_l.setContentsMargins(52, 40, 52, 40)
        body_l.setSpacing(14)

        # Título
        body_l.addWidget(_sect("Título del examen *"))
        self._title_edit = QLineEdit()
        self._title_edit.setMaxLength(MAX_TITLE)
        self._title_edit.setPlaceholderText("Ej: Pentesting & OSINT — Módulo 1")
        self._title_counter = _counter_label(0, MAX_TITLE)
        self._title_edit.textChanged.connect(self._on_title_change)
        title_row = QHBoxLayout()
        title_row.addStretch()
        title_row.addWidget(self._title_counter)
        body_l.addWidget(self._title_edit)
        body_l.addLayout(title_row)
        body_l.addSpacing(6)

        # Descripción
        body_l.addWidget(_sect("Descripción *"))
        self._desc_edit = QTextEdit()
        self._desc_edit.setAcceptRichText(False)
        self._desc_edit.setFixedHeight(90)
        self._desc_edit.setPlaceholderText("Breve descripción del contenido del examen...")
        self._desc_counter = _counter_label(0, MAX_DESC)
        _limit_textedit(self._desc_edit, MAX_DESC, self._desc_counter)
        self._desc_edit.textChanged.connect(self._on_any_change)
        desc_row = QHBoxLayout()
        desc_row.addStretch()
        desc_row.addWidget(self._desc_counter)
        body_l.addWidget(self._desc_edit)
        body_l.addLayout(desc_row)

        body_l.addStretch()
        root.addWidget(body, 1)

        # Barra inferior
        self._import_btn = _btn("📂  Importar JSON", min_w=160)
        self._import_btn.clicked.connect(self._on_import)
        self._ai_btn = _btn("🤖  Generar con IA", min_w=160)
        self._ai_btn.clicked.connect(self._on_ai_prompt)
        self._start_btn = _btn("Empezar  →", cls="primary", min_w=160)
        self._start_btn.setEnabled(False)
        self._start_btn.clicked.connect(self._on_start)
        root.addWidget(_bottom_bar(self._import_btn, self._ai_btn, None, self._start_btn))

    def _on_title_change(self, text: str):
        self._title_counter.setText(f"{len(text)} / {MAX_TITLE}")
        self._on_any_change()

    def _on_any_change(self):
        ok = (
            bool(self._title_edit.text().strip()) and
            bool(self._desc_edit.toPlainText().strip())
        )
        self._start_btn.setEnabled(ok)

    def _on_start(self):
        self.start.emit(
            self._title_edit.text().strip(),
            self._desc_edit.toPlainText().strip()
        )

    def _on_ai_prompt(self):
        dlg = AIPromptDialog(self.window())
        dlg.show_centered()

    def _on_import(self):
        bank_dir = _script_dir() / BANK_DIR_NAME
        bank_dir.mkdir(parents=True, exist_ok=True)
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Importar archivo JSON",
            str(bank_dir),
            "Archivos JSON (*.json)"
        )
        if not path_str:
            return
        try:
            with open(path_str, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            dlg = ConfirmDialog(
                self, "Error al importar",
                f"No se pudo leer el archivo:\n\n{e}",
                [("Cerrar", "default")]
            )
            dlg.exec()
            return

        # Normalizar estructura
        if isinstance(data, list):
            questions = data
            title = Path(path_str).stem
            description = ""
        elif isinstance(data, dict):
            questions = data.get("questions", [])
            title     = data.get("title", Path(path_str).stem)
            description = data.get("description", "")
        else:
            dlg = ConfirmDialog(
                self, "Formato no reconocido",
                "El archivo no tiene el formato esperado de Exam Simulator.",
                [("Cerrar", "default")]
            )
            dlg.exec()
            return

        if not questions:
            dlg = ConfirmDialog(
                self, "Sin preguntas",
                "El archivo no contiene preguntas válidas.",
                [("Cerrar", "default")]
            )
            dlg.exec()
            return

        self.import_json.emit({
            "title":       title,
            "description": description,
            "questions":   questions,
            "_source_path": path_str,
        })

    def clear(self):
        self._title_edit.clear()
        self._desc_edit.clear()
        self._start_btn.setEnabled(False)


# ══════════════════════════════════════════════════════════════════════════════
#  PANTALLA 1: EDITOR DE PREGUNTAS
# ══════════════════════════════════════════════════════════════════════════════

class EditorScreen(QWidget):
    finished   = pyqtSignal(list)   # list[dict]
    discard    = pyqtSignal()
    go_config  = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._questions: list[dict] = []
        self._current:   int        = 0
        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        self._hdr_bar = _header_bar("Pregunta 1 de 1", "")
        root.addWidget(self._hdr_bar)
        # Guardamos referencia a los labels para actualizarlos
        # Los extraemos del layout del header
        self._hdr_title = None  # se actualiza con _refresh_header

        # Scroll con el formulario
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"background: {C['bg']};")

        wrap = QWidget()
        wrap.setStyleSheet(f"background: {C['bg']};")
        wrap_l = QVBoxLayout(wrap)
        wrap_l.setContentsMargins(52, 36, 52, 36)
        wrap_l.setSpacing(0)

        self._form = QuestionForm()
        self._form.validity_changed.connect(self._on_validity)
        wrap_l.addWidget(self._form)
        wrap_l.addStretch()
        scroll.setWidget(wrap)
        root.addWidget(scroll, 1)

        # Barra inferior
        self._btn_prev     = _btn("← Anterior")
        self._btn_next     = _btn("Siguiente →")
        self._btn_add      = _btn("＋  Añadir")
        self._btn_finish   = _btn("✓  Finalizar", cls="primary", min_w=150)
        self._btn_discard  = _btn("Descartar", cls="danger")
        self._btn_config   = _btn("⚙  Config")

        self._btn_prev.clicked.connect(self._go_prev)
        self._btn_next.clicked.connect(self._go_next)
        self._btn_add.clicked.connect(self._save_and_new)
        self._btn_finish.clicked.connect(self._finish)
        self._btn_discard.clicked.connect(self._ask_discard)
        self._btn_config.clicked.connect(self.go_config)

        root.addWidget(_bottom_bar(
            self._btn_discard, self._btn_config, None,
            self._btn_prev, self._btn_next, None,
            self._btn_add, self._btn_finish,
        ))

    # ── Control ───────────────────────────────────────────────────────────────

    def start_new(self, categories: list = None, use_difficulty: bool = False):
        """Inicia el editor con una pregunta vacía."""
        self._questions = [{}]
        self._current   = 0
        self._form.configure(categories or ["General"], use_difficulty)
        self._form.clear()
        self._refresh_header()
        self._refresh_nav()

    def load_for_edit(self, questions: list[dict], index: int,
                      categories: list = None, use_difficulty: bool = False):
        """Carga una lista de preguntas existente y posiciona en index."""
        self._questions = [dict(q) for q in questions]
        self._current   = index
        self._form.configure(categories or ["General"], use_difficulty)
        self._form.set_data(self._questions[index])
        self._refresh_header()
        self._refresh_nav()

    def _save_current(self):
        """Guarda el estado actual del formulario en la lista."""
        if self._form.is_valid():
            self._questions[self._current] = self._form.get_data()

    def _go_prev(self):
        if self._current <= 0:
            return
        self._save_current()
        self._current -= 1
        q = self._questions[self._current]
        if q:
            self._form.set_data(q)
        else:
            self._form.clear()
        self._refresh_header()
        self._refresh_nav()

    def _go_next(self):
        if self._current >= len(self._questions) - 1:
            return
        self._save_current()
        self._current += 1
        q = self._questions[self._current]
        if q:
            self._form.set_data(q)
        else:
            self._form.clear()
        self._refresh_header()
        self._refresh_nav()

    def _save_and_new(self):
        if self._form._has_duplicates():
            self._form._show_duplicate_warning()
            return
        if not self._form.is_valid():
            return
        self._questions[self._current] = self._form.get_data()
        # Eliminar posibles huecos vacíos al final
        while len(self._questions) > self._current + 1 and not self._questions[-1]:
            self._questions.pop()
        self._questions.append({})
        self._current = len(self._questions) - 1
        self._form.clear()
        self._refresh_header()
        self._refresh_nav()

    def _finish(self):
        if self._form._has_duplicates():
            self._form._show_duplicate_warning()
            return
        if not self._form.is_valid():
            return
        self._questions[self._current] = self._form.get_data()
        # Filtrar preguntas vacías o incompletas
        valid = [q for q in self._questions if q and _is_question_valid(q)]
        if not valid:
            return
        self.finished.emit(valid)

    def _ask_discard(self):
        n = len([q for q in self._questions if q])
        dlg = ConfirmDialog(
            self,
            "Descartar examen",
            f"Tienes {n} pregunta(s) sin guardar.\n\n¿Qué quieres hacer?",
            [("Seguir editando", "default"), ("Descartar y salir", "danger")],
        )
        if dlg.exec() == "Descartar y salir":
            self.discard.emit()

    def _on_validity(self, valid: bool):
        self._btn_add.setEnabled(valid)
        self._btn_finish.setEnabled(valid)

    def _refresh_header(self):
        total = len(self._questions)
        idx   = self._current + 1
        # Actualizar el primer label del header (el título)
        bar   = self._hdr_bar
        frame_l = bar.layout()
        if frame_l and frame_l.count() >= 2:
            col_item = frame_l.itemAt(1)
            if col_item and col_item.layout():
                title_item = col_item.layout().itemAt(0)
                if title_item and title_item.widget():
                    title_item.widget().setText(f"Pregunta {idx} de {total}")

    def _refresh_nav(self):
        total = len(self._questions)
        self._btn_prev.setEnabled(self._current > 0)
        self._btn_next.setEnabled(self._current < total - 1)
        valid = self._form.is_valid()
        self._btn_add.setEnabled(valid)
        self._btn_finish.setEnabled(valid)


def _is_question_valid(q: dict) -> bool:
    return (
        bool(q.get("question", "").strip()) and
        len(q.get("options", {})) >= MIN_OPTIONS and
        bool(q.get("correct", "")) and
        q.get("correct") in q.get("options", {}) and
        bool(q.get("explanation", "").strip())
    )


# ══════════════════════════════════════════════════════════════════════════════
#  PANTALLA 2: REVISIÓN
# ══════════════════════════════════════════════════════════════════════════════

def _review_card(index: int, data: dict,
                 on_edit, on_delete, can_delete: bool,
                 on_move_up=None, on_move_down=None, on_duplicate=None,
                 can_move_up: bool = True, can_move_down: bool = True) -> QFrame:
    """
    Tarjeta de revisión al estilo del simulador:
    pregunta visible + opciones marcadas + explicación.
    """
    frame = QFrame()
    frame.setStyleSheet(
        f"QFrame {{ background: {C['surf']}; border: 1px solid {C['border']}; "
        "border-radius: 10px; }}"
    )
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(20, 16, 20, 16)
    layout.setSpacing(8)

    base_css = "background: transparent; border: none;"

    # ── Badges encima de la pregunta: categoría + dificultad en fila ──────────
    cat = data.get("category", "default")
    cat_text = cat if cat and cat != "default" else "no assigned"
    cat_badge = QLabel(cat_text)
    cat_badge.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    cat_badge.setStyleSheet(
        f"color: {C['text2']}; background: {C['surf2']}; border: 1px solid {C['border2']}; "
        "border-radius: 10px; padding: 3px 12px; font-size: 10px; font-weight: 500;"
    )

    diff = data.get("difficulty", "")
    if diff and diff in DIFF_COLORS:
        dc = DIFF_COLORS[diff]
        diff_text = diff
    else:
        dc = {"fg": C["text3"], "bg": C["surf2"], "border": C["border"]}
        diff_text = "no assigned"
    diff_badge = QLabel(diff_text)
    diff_badge.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    diff_badge.setStyleSheet(
        f"color: {dc['fg']}; background: {dc['bg']}; border: 1px solid {dc['border']}; "
        "border-radius: 10px; padding: 3px 12px; font-size: 10px; font-weight: 700;"
    )

    badges_row = QHBoxLayout()
    badges_row.setSpacing(6)
    badges_row.addWidget(cat_badge)
    badges_row.addWidget(diff_badge)
    badges_row.addStretch()
    layout.addLayout(badges_row)
    layout.addSpacing(4)

    # ── Número + pregunta ─────────────────────────────────────────────────────
    top_row = QHBoxLayout()
    top_row.setSpacing(8)
    num_q = QLabel(f"{index + 1}.")
    num_q.setFixedWidth(28)
    num_q.setStyleSheet(f"color: {C['text3']}; font-weight: 700; font-size: 13px; {base_css}")
    top_row.addWidget(num_q)
    q_lbl = QLabel(data.get("question", ""))
    q_lbl.setWordWrap(True)
    q_lbl.setOpenExternalLinks(False)
    q_lbl.setStyleSheet(f"color: {C['text']}; font-size: 13px; font-weight: 600; {base_css}")
    top_row.addWidget(q_lbl, 1)
    layout.addLayout(top_row)
    layout.addSpacing(4)

    # ── Opciones ──────────────────────────────────────────────────────────────
    correct_key  = data.get("correct", "")
    correct_text = data.get("options", {}).get(correct_key, "")

    for k, v in data.get("options", {}).items():
        is_correct = (v == correct_text)
        row = QHBoxLayout()
        row.setSpacing(12)

        key_lbl = QLabel(k)
        key_lbl.setFixedWidth(20)
        key_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        val_lbl = QLabel(v)
        val_lbl.setWordWrap(True)
        val_lbl.setOpenExternalLinks(False)

        tag_lbl = QLabel()
        tag_lbl.setFixedWidth(80)
        tag_lbl.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        if is_correct:
            key_lbl.setStyleSheet(
                f"color: {C['ok']}; font-weight: 700; {base_css}"
            )
            val_lbl.setStyleSheet(
                f"color: {C['ok']}; font-weight: 600; {base_css}"
            )
            tag_lbl.setText("✔ correcta")
            tag_lbl.setStyleSheet(f"color: {C['ok']}; font-size: 11px; {base_css}")
        else:
            key_lbl.setStyleSheet(f"color: {C['text3']}; {base_css}")
            val_lbl.setStyleSheet(f"color: {C['text2']}; {base_css}")
            tag_lbl.setText("·")
            tag_lbl.setStyleSheet(f"color: {C['text3']}; font-size: 18px; {base_css}")

        row.addWidget(key_lbl)
        row.addWidget(val_lbl, 1)
        row.addWidget(tag_lbl)
        layout.addLayout(row)

    # ── Explicación ───────────────────────────────────────────────────────────
    explanation = data.get("explanation", "").strip()
    if explanation:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(
            f"background: {C['border']}; max-height: 1px; border: none;"
        )
        layout.addSpacing(4)
        layout.addWidget(sep)
        layout.addSpacing(4)

        exp_row = QHBoxLayout()
        exp_row.setSpacing(10)
        exp_icon = QLabel("ℹ")
        exp_icon.setFixedWidth(16)
        exp_icon.setAlignment(Qt.AlignmentFlag.AlignTop)
        exp_icon.setStyleSheet(
            f"color: {C['acc']}; font-size: 14px; font-weight: 700; {base_css}"
        )
        exp_lbl = QLabel(explanation)
        exp_lbl.setWordWrap(True)
        exp_lbl.setOpenExternalLinks(False)
        exp_lbl.setStyleSheet(
            f"color: {C['text2']}; font-size: 12px; font-style: italic; {base_css}"
        )
        exp_row.addWidget(exp_icon)
        exp_row.addWidget(exp_lbl, 1)
        layout.addLayout(exp_row)

    # ── Botones de acción ───────────────────
    layout.addSpacing(6)
    btn_row = QHBoxLayout()
    btn_row.setSpacing(6)

    def _nav_btn(txt, enabled):
        b = QPushButton(txt)
        b.setEnabled(enabled)
        b.setCursor(Qt.CursorShape.PointingHandCursor if enabled else Qt.CursorShape.ArrowCursor)
        b.setStyleSheet(
            f"background: transparent; "
            f"color: {C['text2'] if enabled else C['text3']}; "
            f"border: 1px solid {C['border']}; "
            "border-radius: 6px; padding: 5px 14px; font-size: 12px; font-weight: 500;"
        )
        return b

    up_btn = _nav_btn('Mover arriba', can_move_up)
    dn_btn = _nav_btn('Mover abajo',  can_move_down)
    if on_move_up:   up_btn.clicked.connect(lambda: on_move_up(index))
    if on_move_down: dn_btn.clicked.connect(lambda: on_move_down(index))

    edit_btn = QPushButton('Editar')
    edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    edit_btn.setStyleSheet(
        f"background: {C['acc_l']}; color: {C['acc']}; border: 1px solid {C['acc']}; "
        "border-radius: 6px; padding: 5px 16px; font-size: 12px; font-weight: 600;"
    )
    edit_btn.clicked.connect(lambda: on_edit(index))

    del_btn = QPushButton('Borrar')
    del_btn.setCursor(Qt.CursorShape.PointingHandCursor if can_delete else Qt.CursorShape.ArrowCursor)
    del_btn.setEnabled(can_delete)
    del_btn.setStyleSheet(
        f"background: transparent; color: {C['err'] if can_delete else C['text3']}; "
        f"border: 1px solid {C['err'] if can_delete else C['border']}; "
        "border-radius: 6px; padding: 5px 16px; font-size: 12px; font-weight: 600;"
    )
    del_btn.clicked.connect(lambda: _ask_and_delete(del_btn, index, on_delete))

    dup_btn = QPushButton('Duplicar')
    dup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    dup_btn.setStyleSheet(
        f"background: transparent; color: {C['text2']}; "
        f"border: 1px solid {C['border']}; "
        "border-radius: 6px; padding: 5px 16px; font-size: 12px; font-weight: 500;"
    )
    if on_duplicate: dup_btn.clicked.connect(lambda: on_duplicate(index))

    btn_row.addWidget(up_btn)
    btn_row.addWidget(dn_btn)
    btn_row.addStretch()
    btn_row.addWidget(dup_btn)
    btn_row.addWidget(edit_btn)
    btn_row.addWidget(del_btn)
    layout.addLayout(btn_row)
    return frame


def _ask_and_delete(parent_btn, index: int, callback):
    dlg = ConfirmDialog(
        parent_btn.window(),
        "Borrar pregunta",
        "¿Estás seguro de que quieres borrar esta pregunta?",
        [("Cancelar", "default"), ("Borrar", "danger")],
    )
    if dlg.exec() == "Borrar":
        callback(index)


class ReviewScreen(QWidget):
    edit_question = pyqtSignal(int)
    export        = pyqtSignal(list)
    discard       = pyqtSignal()
    go_config     = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._questions: list[dict] = []
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._hdr = _header_bar("Revisión", "")
        root.addWidget(self._hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"background: {C['bg']};")

        self._cards_widget = QWidget()
        self._cards_widget.setStyleSheet(f"background: {C['bg']};")
        self._cards_l = QVBoxLayout(self._cards_widget)
        self._cards_l.setContentsMargins(52, 32, 52, 32)
        self._cards_l.setSpacing(12)
        scroll.setWidget(self._cards_widget)
        root.addWidget(scroll, 1)

        self._btn_discard   = _btn("Descartar", cls="danger")
        self._btn_config    = _btn("⚙  Config")
        self._btn_export    = _btn("Exportar  →", cls="primary", min_w=160)
        self._btn_discard.clicked.connect(self._ask_discard)
        self._btn_config.clicked.connect(self.go_config.emit)
        self._btn_export.clicked.connect(lambda: self.export.emit(self._questions))
        root.addWidget(_bottom_bar(self._btn_discard, self._btn_config, None, self._btn_export))

    def load(self, questions: list[dict]):
        self._questions = list(questions)
        self._rebuild()
        self._update_header()

    def _rebuild(self):
        while self._cards_l.count():
            item = self._cards_l.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        n = len(self._questions)
        can_del = n > 1
        for i, q in enumerate(self._questions):
            card = _review_card(i, q,
                                on_edit=self.edit_question.emit,
                                on_delete=self._delete_question,
                                can_delete=can_del,
                                on_move_up=self._move_up,
                                on_move_down=self._move_down,
                                on_duplicate=self._duplicate,
                                can_move_up=(i > 0),
                                can_move_down=(i < n - 1))
            self._cards_l.addWidget(card)
        self._cards_l.addStretch()

    def _move_up(self, index: int):
        if index <= 0: return
        q = self._questions
        q[index - 1], q[index] = q[index], q[index - 1]
        self._rebuild(); self._update_header()

    def _move_down(self, index: int):
        if index >= len(self._questions) - 1: return
        q = self._questions
        q[index], q[index + 1] = q[index + 1], q[index]
        self._rebuild(); self._update_header()

    def _duplicate(self, index: int):
        import copy
        self._questions.insert(index + 1, copy.deepcopy(self._questions[index]))
        self._rebuild(); self._update_header()

    def _update_header(self):
        bar_l = self._hdr.layout()
        if bar_l and bar_l.count() >= 2:
            col = bar_l.itemAt(1)
            if col and col.layout() and col.layout().count() >= 2:
                sub = col.layout().itemAt(1).widget()
                if sub:
                    n = len(self._questions)
                    sub.setText(f"{n} pregunta{'s' if n != 1 else ''}")

    def _delete_question(self, index: int):
        self._questions.pop(index)
        self._rebuild()
        self._update_header()

    def _ask_discard(self):
        dlg = ConfirmDialog(
            self,
            "Descartar examen",
            f"Se descartarán {len(self._questions)} pregunta(s).\n"
            "No se generará ningún archivo.\n\n¿Confirmar?",
            [("Cancelar", "default"), ("Descartar todo", "danger")],
        )
        if dlg.exec() == "Descartar todo":
            self.discard.emit()

# ══════════════════════════════════════════════════════════════════════════════
#  PANTALLA 3: CONFIRMAR EXPORTACIÓN
# ══════════════════════════════════════════════════════════════════════════════

class ExportConfirmScreen(QWidget):
    confirmed = pyqtSignal(Path)   # ruta del archivo generado
    back      = pyqtSignal()
    discard   = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._title      = ""
        self._desc       = ""
        self._questions: list[dict] = []
        self._dest_path: Path | None = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(_header_bar("Confirmar exportación",
                                   "Revisa los detalles antes de guardar"))

        body = QWidget()
        body.setStyleSheet(f"background: {C['bg']};")
        body_l = QVBoxLayout(body)
        body_l.setContentsMargins(52, 40, 52, 40)
        body_l.setSpacing(16)
        body_l.addStretch()

        # Tarjeta resumen
        card = QFrame()
        card.setStyleSheet(
            f"QFrame {{ background: {C['surf']}; border: 1px solid {C['border']}; "
            "border-radius: 12px; }}"
        )
        card_l = QVBoxLayout(card)
        card_l.setContentsMargins(32, 28, 32, 28)
        card_l.setSpacing(14)

        for key, attr in (("📄  Archivo", "_fname_lbl"),
                           ("📁  Destino", "_dest_lbl"),
                           ("❓  Preguntas", "_count_lbl"),
                           ("📝  Título", "_title_lbl"),):
            row = QHBoxLayout()
            row.setSpacing(16)
            cap = _label(key, C["text3"], size=12)
            cap.setFixedWidth(100)
            val = _label("—", C["text"], size=13, bold=True)
            setattr(self, attr, val)
            row.addWidget(cap)
            row.addWidget(val, 1)
            card_l.addLayout(row)

        body_l.addWidget(card)
        body_l.addStretch()
        root.addWidget(body, 1)

        self._btn_back    = _btn("← Revisión")
        self._btn_discard = _btn("Descartar", cls="danger")
        self._btn_confirm = _btn("✓  Exportar y guardar", cls="primary", min_w=200)
        self._btn_back.clicked.connect(self.back.emit)
        self._btn_discard.clicked.connect(self._ask_discard)
        self._btn_confirm.clicked.connect(self._do_export)
        root.addWidget(_bottom_bar(
            self._btn_discard, self._btn_back, None, self._btn_confirm
        ))

    def load(self, title: str, description: str, questions: list[dict]):
        self._title     = title
        self._desc      = description
        self._questions = questions

        fname     = sanitize_filename(title) + ".json"
        bank_dir  = _script_dir() / BANK_DIR_NAME
        dest_path = bank_dir / fname
        self._dest_path = dest_path

        self._fname_lbl.setText(fname)
        self._dest_lbl.setText(str(bank_dir))
        self._count_lbl.setText(
            f"{len(questions)} pregunta{'s' if len(questions) != 1 else ''}"
        )
        self._title_lbl.setText(title)

    def _do_export(self):
        if not self._dest_path:
            return
        try:
            self._dest_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "title":       self._title,
                "description": self._desc,
                "questions":   self._questions,
            }
            with open(self._dest_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.confirmed.emit(self._dest_path)
        except OSError as e:
            QMessageBox.critical(self, "Error al guardar", str(e))

    def _ask_discard(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Descartar examen")
        dlg.setText(
            "Se descartará todo el trabajo y no se generará ningún archivo.\n\n"
            "¿Confirmar?"
        )
        dlg.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)
        dlg.addButton("Descartar todo", QMessageBox.ButtonRole.DestructiveRole)
        dlg.exec()
        if dlg.clickedButton() and dlg.clickedButton().text() == "Descartar todo":
            self.discard.emit()


# ══════════════════════════════════════════════════════════════════════════════
#  PANTALLA 4: ÉXITO
# ══════════════════════════════════════════════════════════════════════════════

class SuccessScreen(QWidget):
    new_exam       = pyqtSignal()
    back_simulator = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._path: Path | None = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(_header_bar("Examen generado", "Exam Generator"))

        body = QWidget()
        body.setStyleSheet(f"background: {C['bg']};")
        body_l = QVBoxLayout(body)
        body_l.setContentsMargins(52, 48, 52, 48)
        body_l.setSpacing(0)
        body_l.addStretch()

        card = QFrame()
        card.setStyleSheet(
            f"QFrame {{ background: {C['surf']}; border: 1px solid {C['border']}; "
            "border-radius: 12px; }}"
        )
        card_l = QVBoxLayout(card)
        card_l.setContentsMargins(40, 36, 40, 36)
        card_l.setSpacing(0)

        # Icono
        icon = QLabel("✓")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            f"color: {C['ok']}; font-size: 40px; font-weight: 800; "
            "background: transparent; border: none;"
        )
        card_l.addWidget(icon)
        card_l.addSpacing(12)

        # Mensaje
        msg = QLabel("El archivo se ha guardado correctamente.")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setStyleSheet(
            f"color: {C['text']}; font-size: 15px; font-weight: 700; "
            "background: transparent; border: none;"
        )
        card_l.addWidget(msg)
        card_l.addSpacing(24)

        # Detalles del examen — apilados (etiqueta encima, valor debajo)
        base_css = "background: transparent; border: none;"
        for key, attr in (
            ("Título",      "_lbl_title"),
            ("Descripción", "_lbl_desc"),
            ("Preguntas",   "_lbl_count"),
        ):
            col = QVBoxLayout()
            col.setSpacing(3)
            cap = QLabel(key.upper())
            cap.setStyleSheet(
                f"color: {C['text3']}; font-size: 10px; font-weight: 700; "
                f"letter-spacing: 1px; {base_css}"
            )
            val = QLabel("—")
            val.setWordWrap(True)
            val.setStyleSheet(
                f"color: {C['text']}; font-size: 13px; font-weight: 600; {base_css}"
            )
            setattr(self, attr, val)
            col.addWidget(cap)
            col.addWidget(val)
            card_l.addLayout(col)
            card_l.addSpacing(14)

        body_l.addWidget(card)
        body_l.addStretch()
        root.addWidget(body, 1)

        self._btn_open = _btn("📂  Abrir ubicación", min_w=180)
        self._btn_open.clicked.connect(self._open_location)
        btn_new = _btn("＋  Crear otro examen", min_w=180)
        btn_sim = _btn("← Volver al Simulador", cls="primary", min_w=200)
        btn_new.clicked.connect(self.new_exam.emit)
        btn_sim.clicked.connect(self.back_simulator.emit)
        root.addWidget(_bottom_bar(self._btn_open, btn_new, None, btn_sim))

    def _open_location(self):
        if not self._path:
            return
        import subprocess, platform
        system = platform.system()
        if system == "Windows":
            subprocess.Popen(["explorer", "/select,", str(self._path)])
        elif system == "Darwin":
            subprocess.Popen(["open", "-R", str(self._path)])
        else:
            subprocess.Popen(["xdg-open", str(self._path.parent)])

    def load(self, path: Path, title: str = "", description: str = "", count: int = 0):
        self._path = path
        self._lbl_title.setText(title or path.stem)
        self._lbl_desc.setText(description or "—")
        self._lbl_count.setText(
            f"{count} pregunta{'s' if count != 1 else ''}"
        )


# ══════════════════════════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

class GeneratorWindow(QMainWindow):
    # Estados
    S_HOME    = 0
    S_CONFIG  = 1
    S_EDITOR  = 2
    S_REVIEW  = 3
    S_SUCCESS = 4

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Exam Generator  v{APP_VERSION}")
        self.setMinimumSize(820, 560)
        self.resize(920, 680)

        self._exam      = ExamData()
        self._exported  = False          # ¿ya se exportó en esta sesión?
        self._exp_file: Path | None = None

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home_s    = HomeScreen()
        self.config_s  = ExamConfigScreen()
        self.editor_s  = EditorScreen()
        self.review_s  = ReviewScreen()
        self.success_s = SuccessScreen()

        for s in (self.home_s, self.config_s, self.editor_s,
                  self.review_s, self.success_s):
            self.stack.addWidget(s)

        self.home_s.start.connect(self._on_start)
        self.home_s.back_simulator.connect(self._back_to_simulator)
        self.home_s.import_json.connect(self._on_import_json)

        self.config_s.confirmed.connect(self._on_config_confirmed)
        self.config_s.back.connect(self._on_config_back)
        self.config_s.discard.connect(self._discard_and_home)

        self.editor_s.finished.connect(self._on_editor_finished)
        self.editor_s.discard.connect(self._discard_and_home)
        self.editor_s.go_config.connect(self._on_editor_go_config)

        self.review_s.edit_question.connect(self._on_edit_question)
        self.review_s.export.connect(self._on_review_export)
        self.review_s.discard.connect(self._discard_and_home)
        self.review_s.go_config.connect(self._on_review_go_config)

        self.success_s.new_exam.connect(self._new_exam)
        self.success_s.back_simulator.connect(self._back_to_simulator)

        self.stack.setCurrentIndex(self.S_HOME)

    # ── Navegación ────────────────────────────────────────────────────────────

    def _on_start(self, title: str, description: str):
        self._exam.title       = title
        self._exam.description = description
        self._exam.questions   = []
        self._exported         = False
        self._exp_file         = None
        self._import_pending   = False
        self.config_s.reset()
        self.stack.setCurrentIndex(self.S_CONFIG)

    def _on_config_back(self):
        if getattr(self, "_from_review", False):
            self._from_review = False
            self.stack.setCurrentIndex(self.S_REVIEW)
        elif getattr(self, "_from_editor", False):
            self._from_editor = False
            self.stack.setCurrentIndex(self.S_EDITOR)
        else:
            self.stack.setCurrentIndex(self.S_HOME)

    def _on_editor_go_config(self):
        self._exam.questions = list(self.editor_s._questions)
        self._from_editor    = True
        diff_on = self._exam.use_difficulty
        self.config_s._diff_toggle.setChecked(diff_on)
        self.config_s._off_warn.setVisible(not diff_on)
        self.config_s._btn_continue.setEnabled(bool(self.config_s._categories))
        from collections import Counter
        _cnt = dict(Counter(q.get('category','default') for q in self._exam.questions))
        self.config_s._rebuild_list(counters=_cnt)
        self.stack.setCurrentIndex(self.S_CONFIG)

    def _on_review_go_config(self):
        # Guarda preguntas actuales y va a config SIN resetearla
        self._exam.questions = list(self.review_s._questions)
        self._from_review    = True
        # Añadir categorias de las preguntas que aún no estén en config
        for q in self._exam.questions:
            cat = q.get("category", "")
            if cat and cat != "default" and cat not in self.config_s._categories:
                self.config_s._categories.append(cat)
        from collections import Counter
        _cnt = dict(Counter(q.get('category','default') for q in self._exam.questions))
        self.config_s._rebuild_list(counters=_cnt)
        # Actualizar diff toggle según estado actual
        diff_on = self._exam.use_difficulty
        self.config_s._diff_toggle.setChecked(diff_on)
        self.config_s._off_warn.setVisible(not diff_on)
        self.config_s._btn_continue.setEnabled(bool(self.config_s._categories))
        self.stack.setCurrentIndex(self.S_CONFIG)

    def _on_config_confirmed(self, categories: list, use_difficulty: bool):
        self._exam.categories     = categories
        self._exam.use_difficulty = use_difficulty
        if getattr(self, "_import_pending", False):
            self._import_pending = False
            # Importación: editor desde la primera pregunta
            self.editor_s.load_for_edit(
                self._exam.questions, 0, categories, use_difficulty
            )
            self.stack.setCurrentIndex(self.S_EDITOR)
        elif getattr(self, "_from_review", False):
            self._from_review = False
            # Revisión → config → continuar: volver al editor con preguntas
            self.editor_s.load_for_edit(
                self._exam.questions, 0, categories, use_difficulty
            )
            self.stack.setCurrentIndex(self.S_EDITOR)
        elif getattr(self, "_from_editor", False):
            self._from_editor = False
            # Editor → config → continuar: volver al editor con preguntas
            self.editor_s.load_for_edit(
                self._exam.questions, 0, categories, use_difficulty
            )
            self.stack.setCurrentIndex(self.S_EDITOR)
        else:
            # Examen nuevo desde Home: empezar desde cero
            self.editor_s.start_new(categories, use_difficulty)
            self.stack.setCurrentIndex(self.S_EDITOR)

    def _on_import_json(self, data: dict):
        """Importa JSON: pasa por ExamConfigScreen para revisar/editar categorias."""
        self._exam.title       = data.get("title", "")
        self._exam.description = data.get("description", "")
        self._exam.questions   = data.get("questions", [])
        self._exported         = False
        self._exp_file         = None
        self._import_pending   = True
        self._exam.source_path = data.get("_source_path", "")  # ruta del archivo original
        self.config_s.reset()
        # Si viene del Simulator via --import-file, forzar dificultad ON
        force_diff = bool(data.get("_source_path"))
        self.config_s.load_from_json(self._exam.questions, force_difficulty=force_diff)
        self.stack.setCurrentIndex(self.S_CONFIG)

    def _on_editor_finished(self, questions: list[dict]):
        self._exam.questions = questions
        self.review_s.load(self._exam.questions)
        self.stack.setCurrentIndex(self.S_REVIEW)

    def _on_edit_question(self, index: int):
        self._exam.questions = list(self.review_s._questions)
        self.editor_s.load_for_edit(
            self._exam.questions, index,
            self._exam.categories, self._exam.use_difficulty
        )
        self.stack.setCurrentIndex(self.S_EDITOR)

    def _on_review_export(self, questions: list[dict]):
        import json as _json
        self._exam.questions = questions

        bank_dir = _script_dir() / BANK_DIR_NAME
        bank_dir.mkdir(parents=True, exist_ok=True)

        # Si viene de un JSON importado, ofrecer sobreescribir o guardar nuevo
        source = Path(self._exam.source_path) if self._exam.source_path else None
        if source and source.exists():
            dlg = ConfirmDialog(
                self,
                "Exportar examen",
                f"Este examen fue importado desde:\n{source.name}\n\n"
                "¿Quieres sobreescribirlo o guardarlo como archivo nuevo?",
                [
                    ("Sobreescribir", "danger"),
                    ("Guardar como nuevo", "primary"),
                    ("Cancelar", "default"),
                ]
            )
            result = dlg.exec()
            if result == "Cancelar" or result is None:
                return
            if result == "Sobreescribir":
                self._do_save(Path(self._exam.source_path), _json)
                return

        # Guardar como nuevo: diálogo nativo
        suggested = sanitize_filename(self._exam.title) + ".json"
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar examen como",
            str(bank_dir / suggested),
            "Archivos JSON (*.json)"
        )
        if not path_str:
            return
        dest_path = Path(path_str)
        if dest_path.suffix.lower() != ".json":
            dest_path = dest_path.with_suffix(".json")
        self._do_save(dest_path, _json)

    def _do_save(self, dest_path: Path, _json):
        try:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "title":       self._exam.title,
                "description": self._exam.description,
                "questions":   self._exam.questions,
            }
            with open(dest_path, "w", encoding="utf-8") as f:
                _json.dump(data, f, ensure_ascii=False, indent=2)
            self._on_exported(dest_path)
        except OSError as e:
            QMessageBox.critical(self, "Error al guardar", str(e))

    def _on_exported(self, path: Path):
        self._exported = True
        self._exp_file = path
        self.success_s.load(
            path,
            title=self._exam.title,
            description=self._exam.description,
            count=len(self._exam.questions),
        )
        self.stack.setCurrentIndex(self.S_SUCCESS)

    def _discard_and_home(self):
        self._exam           = ExamData()
        self._exported       = False
        self._exp_file       = None
        self._import_pending = False
        self._from_review    = False
        self._from_editor    = False
        self.home_s.clear()
        self.stack.setCurrentIndex(self.S_HOME)

    def _new_exam(self):
        self._exam           = ExamData()
        self._exported       = False
        self._exp_file       = None
        self._import_pending = False
        self._from_review    = False
        self._from_editor    = False
        self.home_s.clear()
        self.stack.setCurrentIndex(self.S_HOME)

    def _back_to_simulator(self):
        sim = _script_dir() / "exam_simulator.py"
        if not sim.exists():
            QMessageBox.warning(
                self, "Archivo no encontrado",
                "No se encontró exam_simulator.py junto al generador.\n\n"
                + str(sim)
            )
            return
        subprocess.Popen([sys.executable, str(sim)])
        QApplication.instance().quit()

    # ── closeEvent ────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        # Si ya exportó → cerrar sin preguntar
        if self._exported:
            event.accept()
            return

        # Si no hay preguntas ni datos → cerrar sin preguntar
        current = self.stack.currentIndex()
        has_work = (
            bool(self._exam.questions) or
            (current in (self.S_CONFIG, self.S_EDITOR, self.S_REVIEW))
        )
        if not has_work:
            event.accept()
            return

        # Hay trabajo sin guardar → preguntar
        dlg = ConfirmDialog(
            self,
            "Salir",
            "Tienes trabajo sin exportar. Si cierras ahora se perderá todo.\n\n¿Qué quieres hacer?",
            [
                ("Seguir editando",    "primary"),
                ("Volver al Simulador","default"),
                ("Descartar y cerrar", "danger"),
            ],
        )
        result = dlg.exec()
        if result == "Seguir editando" or result is None:
            event.ignore()
        elif result == "Volver al Simulador":
            event.accept()
            self._back_to_simulator()
        else:
            event.accept()


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    icon_path = _script_dir() / "resources" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    app.setApplicationName("Exam Generator")
    app.setApplicationVersion(APP_VERSION)
    app.setStyleSheet(QSS)
    win = GeneratorWindow()
    win.show()

    # Detectar --import-file <ruta> pasado por el Simulator
    import_path: Path | None = None
    args = sys.argv[1:]
    if "--import-file" in args:
        idx = args.index("--import-file")
        if idx + 1 < len(args):
            import_path = Path(args[idx + 1])

    if import_path and import_path.exists():
        try:
            with open(import_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                payload = {
                    "title":        import_path.stem,
                    "description":  "",
                    "questions":    data,
                    "_source_path": str(import_path),
                }
            elif isinstance(data, dict):
                payload = {
                    "title":        data.get("title", import_path.stem),
                    "description":  data.get("description", ""),
                    "questions":    data.get("questions", []),
                    "_source_path": str(import_path),
                }
            else:
                payload = None

            if payload and payload["questions"]:
                # Diferir para que la ventana esté completamente renderizada
                QTimer.singleShot(100, lambda: win._on_import_json(payload))
        except (OSError, json.JSONDecodeError):
            pass   # si falla, abre normalmente en Home

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
