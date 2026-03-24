#!/usr/bin/env python3
"""
EXAM SIMULATOR  v2.1  —  PyQt6
Simulador de examen de selección múltiple con interfaz gráfica.

Dependencia:
    pip install PyQt6

Estructura junto al ejecutable:
    exam_simulator.py
    questions_bank/
    ├── archivo.json
    ├── carpeta_tema/
    │   ├── parte_a.json
    │   └── parte_b.json
    └── ...
"""

import hashlib
import json
import sys
import random
import time
import uuid
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSpinBox, QCheckBox,
    QListWidget, QListWidgetItem, QProgressBar,
    QTabWidget, QSizePolicy, QMessageBox, QFileDialog,
    QDialog, QLineEdit,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

# ══════════════════════════════════════════════════════════════════════════════
#  PALETA Y ESTILOS  —  Light theme
# ══════════════════════════════════════════════════════════════════════════════

BANK_DIR_NAME    = "questions_bank"
PLAYERS_DIR_NAME = "players"
APP_VERSION      = "2.2"

DIFF_COLORS = {
    "easy":   {"fg": "#16a34a", "bg": "#edfff1", "border": "#16a34a"},
    "medium": {"fg": "#b45309", "bg": "#fffbeb", "border": "#d97706"},
    "hard":   {"fg": "#e05a47", "bg": "#fff1ee", "border": "#e05a47"},
    "insane": {"fg": "#9d174d", "bg": "#fdf2f8", "border": "#be185d"},
}

C = dict(
    bg       = "#f4f6f9",       # fondo general — gris muy suave
    surf     = "#ffffff",       # superficies / tarjetas
    surf2    = "#edf0f4",       # superficies secundarias / hover
    border   = "#d0d7e2",       # bordes normales
    border2  = "#b8c2d4",       # bordes énfasis
    acc      = "#2563eb",       # azul primario
    acc_l    = "#eff4ff",       # azul muy claro (fondo tint)
    acc_d    = "#1d4ed8",       # azul hover/pressed
    ok       = "#2db84d",       # verde  #82F592 base
    ok_l     = "#edfff1",       # verde claro
    err      = "#e05a47",       # coral  #FE9C8E base
    err_l    = "#fff1ee",       # coral claro
    warn     = "#c9961a",       # ámbar  #FFD97D base
    warn_l   = "#fffaeb",       # ámbar claro
    skip     = "#1ab8b3",       # teal   #7CEBE9 base
    skip_l   = "#eafcfb",       # teal claro
    text     = "#111827",       # texto principal
    text2    = "#4b5563",       # texto secundario
    text3    = "#9ca3af",       # texto muted / placeholder
    shadow   = "rgba(0,0,0,0.06)",
)

QSS = """
* {
    font-family: "Segoe UI", "SF Pro Text", "Helvetica Neue", sans-serif;
    font-size: 13px;
}
QMainWindow, QWidget#root {
    background: %(bg)s;
}
QWidget {
    background: transparent;
    color: %(text)s;
}
QMainWindow QWidget {
    background: %(bg)s;
}

/* ── Scrollbars ── */
QScrollArea { border: none; }
QScrollBar:vertical {
    background: %(surf2)s;
    width: 7px;
    border-radius: 4px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: %(border2)s;
    border-radius: 4px;
    min-height: 28px;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { height: 0; }

/* ── Progress bar ── */
QProgressBar {
    background: %(surf2)s;
    border: none;
    border-radius: 3px;
    max-height: 5px;
}
QProgressBar::chunk {
    background: %(acc)s;
    border-radius: 3px;
}

/* ── List widget ── */
QListWidget {
    background: %(surf)s;
    border: 1px solid %(border)s;
    border-radius: 10px;
    outline: none;
    padding: 6px;
}
QListWidget::item {
    color: %(text)s;
    padding: 12px 16px;
    border-radius: 7px;
    margin: 2px 0;
}
QListWidget::item:hover {
    background: %(surf2)s;
}
QListWidget::item:selected {
    background: %(acc_l)s;
    color: %(acc)s;
    border: 1px solid %(acc)s;
    font-weight: 600;
}

/* ── SpinBox ── */
QSpinBox {
    background: %(surf)s;
    color: %(text)s;
    border: 1px solid %(border)s;
    border-radius: 7px;
    padding: 7px 12px;
    font-size: 14px;
    min-width: 80px;
    selection-background-color: %(acc_l)s;
}
QSpinBox:focus { border-color: %(acc)s; }
QSpinBox::up-button, QSpinBox::down-button {
    width: 0px;
    border: none;
    background: transparent;
}
QSpinBox::up-arrow, QSpinBox::down-arrow {
    width: 0px;
    height: 0px;
}

/* ── CheckBox ── */
QCheckBox {
    color: %(text)s;
    spacing: 12px;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 22px;
    height: 22px;
    border-radius: 11px;
    border: 2.5px solid %(border2)s;
    background: %(surf)s;
}
QCheckBox::indicator:hover {
    border-color: %(acc)s;
    background: %(acc_l)s;
}
QCheckBox::indicator:checked {
    border: 2.5px solid %(acc)s;
    background: qradialgradient(
        cx:0.5, cy:0.5, radius:0.5,
        fx:0.5, fy:0.5,
        stop:0 %(acc)s,
        stop:0.45 %(acc)s,
        stop:0.5 white,
        stop:1 white
    );
}

/* ── Tabs ── */
QTabWidget::pane {
    border: 1px solid %(border)s;
    border-top: none;
    background: %(surf)s;
    border-radius: 0 0 8px 8px;
}
QTabBar::tab {
    background: %(surf2)s;
    color: %(text2)s;
    padding: 9px 22px;
    border: 1px solid %(border)s;
    border-bottom: none;
    border-radius: 7px 7px 0 0;
    margin-right: 3px;
    font-size: 12px;
}
QTabBar::tab:selected {
    background: %(surf)s;
    color: %(acc)s;
    font-weight: 600;
    border-color: %(border)s;
    border-bottom-color: %(surf)s;
}
QTabBar::tab:hover:!selected { color: %(text)s; background: %(border)s; }

/* ── Buttons (default) ── */
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

/* ── Button: primary ── */
QPushButton[cls="primary"] {
    background: %(acc)s;
    color: #ffffff;
    border: none;
    font-weight: 700;
    padding: 9px 28px;
}
QPushButton[cls="primary"]:hover { background: %(acc_d)s; }
QPushButton[cls="primary"]:pressed { background: %(acc_d)s; }
QPushButton[cls="primary"]:disabled {
    background: %(surf2)s;
    color: %(text3)s;
}

/* ── Button: danger ── */
QPushButton[cls="danger"] {
    background: transparent;
    color: %(err)s;
    border: 1px solid %(err)s;
}
QPushButton[cls="danger"]:hover {
    background: %(err_l)s;
    color: %(err)s;
}

/* ── Message box ── */
QMessageBox { background: %(surf)s; }
QMessageBox QPushButton { min-width: 80px; }
""" % C


# ══════════════════════════════════════════════════════════════════════════════
#  LÓGICA CORE
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


def _validate_question(q: dict) -> str | None:
    for field in ("question", "options", "correct"):
        if field not in q:
            return f"falta el campo '{field}'"
    if not isinstance(q["question"], str) or not q["question"].strip():
        return "el campo 'question' está vacío"
    if not isinstance(q["options"], dict):
        return f"'options' debe ser un objeto JSON (se recibió {type(q['options']).__name__})"
    if len(q["options"]) < 2:
        return f"'options' necesita al menos 2 entradas (tiene {len(q['options'])})"
    for k, v in q["options"].items():
        if not isinstance(v, str) or not v.strip():
            return f"la opción '{k}' está vacía o no es texto"
    if q["correct"].upper() not in {k.upper() for k in q["options"]}:
        return f"'correct' = '{q['correct']}' no coincide con ninguna clave de 'options'"
    return None


def load_json(filepath: Path) -> tuple[list[dict], list[str]]:
    try:
        data = json.loads(filepath.read_text(encoding="utf-8"))
    except OSError as e:
        return [], [f"No se pudo leer {filepath.name}: {e}"]
    except json.JSONDecodeError as e:
        return [], [f"JSON inválido en {filepath.name} (línea {e.lineno}): {e.msg}"]

    if isinstance(data, list):
        raw, title = data, filepath.stem
    elif isinstance(data, dict):
        title = data.get("title") or filepath.stem
        raw   = data.get("questions")
        if not isinstance(raw, list):
            return [], [f"{filepath.name}: se esperaba clave 'questions' con una lista"]
    else:
        return [], [f"{filepath.name}: formato no reconocido"]

    valid, warns = [], []
    for i, q in enumerate(raw or [], 1):
        if not isinstance(q, dict):
            warns.append(f"{title} #{i}: no es un objeto"); continue
        err = _validate_question(q)
        if err:
            warns.append(f"{title} #{i}: {err}"); continue
        q = dict(q)
        q["correct"]   = next(k for k in q["options"] if k.upper() == q["correct"].upper())
        q["_source"]   = title           # título del examen (puede repetirse)
        q["_filename"] = filepath.stem   # nombre del archivo (siempre único)
        valid.append(q)

    return valid, warns


def load_files(paths: list[Path]) -> tuple[list[dict], list[str]]:
    all_q, all_w = [], []
    for p in paths:
        qs, ws = load_json(p)
        all_q.extend(qs); all_w.extend(ws)
    return all_q, all_w


def discover_bank() -> dict:
    bank = _script_dir() / BANK_DIR_NAME
    if not bank.exists() or not bank.is_dir():
        return {"error": (
            f"No se encontró la carpeta '{BANK_DIR_NAME}' junto al ejecutable.\n\n"
            "Créala y coloca dentro tus archivos .json."
        )}
    loose = sorted(p for p in bank.iterdir() if p.is_file() and p.suffix.lower() == ".json")
    folders: dict[str, list[Path]] = {}
    for sub in sorted(p for p in bank.iterdir() if p.is_dir()):
        jsons = sorted(p for p in sub.iterdir() if p.is_file() and p.suffix.lower() == ".json")
        if jsons:
            folders[sub.name] = jsons
    if not loose and not folders:
        return {"error": (
            f"La carpeta '{BANK_DIR_NAME}' no contiene ningún archivo .json\n"
            "(ni en la raíz ni en subcarpetas)."
        )}
    return {"loose": loose, "folders": folders}


class ExamEngine:
    def __init__(self, questions: list[dict], shuffle_options: bool = False):
        self.total        = len(questions)
        self.answers:     list[dict] = []
        self.current_idx: int = 0
        self.start_time:  float = time.time()
        self.end_time:    float | None = None
        self._items:      list[dict] = []
        self._q_start:    float = time.time()   # timestamp inicio pregunta actual

        for q in questions:
            keys         = list(q["options"].keys())
            values       = list(q["options"].values())
            correct_text = q["options"][q["correct"]]
            if shuffle_options:
                random.shuffle(values)
            display_opts = dict(zip(keys, values))
            # Mapa: clave_mostrada → clave_original del JSON
            # Permite exportar siempre claves originales a Chronicator
            shown_to_original = {}
            for orig_key, orig_val in q["options"].items():
                for shown_key, shown_val in display_opts.items():
                    if orig_val == shown_val:
                        shown_to_original[shown_key] = orig_key
                        break
            self._items.append({
                "q":                q,
                "display_opts":     display_opts,
                "correct_text":     correct_text,
                "shown_to_original": shown_to_original,
            })

    @property
    def current(self) -> dict:
        return self._items[self.current_idx]

    @property
    def done(self) -> bool:
        return self.current_idx >= self.total

    def submit(self, chosen_key: str | None) -> bool:
        item         = self.current
        correct_text = item["correct_text"]
        time_seconds = int(time.time() - self._q_start)
        if chosen_key is not None:
            chosen_text = item["display_opts"].get(chosen_key, "")
            is_correct  = (chosen_text == correct_text)
            # Traducir clave mostrada a clave original del JSON
            original_chosen = item["shown_to_original"].get(chosen_key, chosen_key)
        else:
            is_correct      = False
            original_chosen = None
        # Clave correcta original (siempre desde el JSON)
        original_correct = item["q"].get("correct", "")
        self.answers.append({
            "question":        item["q"],
            "display_opts":    item["display_opts"],
            "chosen":          chosen_key,
            "correct_text":    correct_text,
            "is_correct":      is_correct,
            "time_seconds":    time_seconds,
            "original_chosen": original_chosen,
            "original_correct":original_correct,
        })
        self.current_idx += 1
        self._q_start = time.time()   # reset para la siguiente pregunta
        if self.done:
            self.end_time = time.time()
        return is_correct

    def results(self) -> dict:
        answered  = [a for a in self.answers if a["chosen"] is not None]
        correct   = [a for a in answered if a["is_correct"]]
        incorrect = [a for a in answered if not a["is_correct"]]
        skipped   = [a for a in self.answers if a["chosen"] is None]
        pct       = len(correct) / self.total * 100 if self.total else 0
        elapsed   = int((self.end_time or time.time()) - self.start_time)
        return dict(
            total=self.total, correct=correct, incorrect=incorrect,
            skipped=skipped, pct=pct, elapsed=elapsed,
        )


# ══════════════════════════════════════════════════════════════════════════════
#  UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _label(text: str = "", color: str = None, size: int = 13,
           bold: bool = False, italic: bool = False,
           align: Qt.AlignmentFlag = None) -> QLabel:
    lbl = QLabel(text)
    lbl.setWordWrap(True)
    css = f"color: {color or C['text']}; font-size: {size}px;"
    if bold:   css += " font-weight: 700;"
    if italic: css += " font-style: italic;"
    lbl.setStyleSheet(css)
    if align:
        lbl.setAlignment(align)
    return lbl


def _btn(text: str, cls: str = None, min_w: int = None) -> QPushButton:
    b = QPushButton(text)
    if cls:
        b.setProperty("cls", cls)
        b.style().unpolish(b)
        b.style().polish(b)
    if min_w:
        b.setMinimumWidth(min_w)
    return b


def _hline() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet(f"background: {C['border']}; max-height: 1px; border: none;")
    return f


def _vline() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.VLine)
    f.setStyleSheet(f"background: {C['border']}; max-width: 1px; border: none;")
    return f


def _card(radius: int = 10, bg: str = None, border: str = None) -> QFrame:
    f = QFrame()
    bg_    = bg or C["surf"]
    bdr_   = border or C["border"]
    f.setStyleSheet(
        f"QFrame {{ background: {bg_}; border: 1px solid {bdr_}; "
        f"border-radius: {radius}px; }}"
    )
    return f


# ── Botón de opción con word-wrap ─────────────────────────────────────────────

class OptionButton(QFrame):
    clicked = pyqtSignal(str)

    _STATES = {
        "":       (C["surf"],  C["border"],  C["text"],  C["text2"],  "500", "1px"),
        "sel":    (C["acc_l"], C["acc"],     C["acc"],   C["acc"],    "700", "2px"),
        "ok":     (C["ok_l"],  C["ok"],      C["ok"],    C["ok"],     "700", "2px"),
        "err":    (C["err_l"], C["err"],     C["err"],   C["err"],    "700", "2px"),
        "reveal": (C["ok_l"],  C["ok"],      C["ok"],    C["ok"],     "600", "2px"),
    }

    def __init__(self, key: str, text: str):
        super().__init__()
        self._key    = key
        self._active = True
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(50)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 13, 18, 13)
        layout.setSpacing(16)

        self._key_lbl = QLabel(key)
        self._key_lbl.setFixedWidth(22)
        self._key_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._text_lbl = QLabel(text)
        self._text_lbl.setWordWrap(True)
        self._text_lbl.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        layout.addWidget(self._key_lbl)
        layout.addWidget(self._text_lbl, 1)
        self.set_state("")

    @property
    def key(self) -> str:
        return self._key

    def set_state(self, state: str):
        bg, bdr, key_c, txt_c, fw, bdr_w = self._STATES.get(state, self._STATES[""])
        hover = (
            f"QFrame:hover {{ background: {C['surf2']}; border-color: {C['acc']}; }}"
            if not state else ""
        )
        self.setStyleSheet(
            f"QFrame {{ background: {bg}; border: {bdr_w} solid {bdr}; border-radius: 9px; }} "
            + hover
        )
        base = "background: transparent; border: none;"
        self._key_lbl.setStyleSheet(
            f"color: {key_c}; font-weight: {fw}; font-size: 14px; {base}"
        )
        self._text_lbl.setStyleSheet(
            f"color: {txt_c}; font-size: 13px; {base}"
        )

    def set_active(self, active: bool):
        self._active = active
        self.setCursor(
            Qt.CursorShape.ArrowCursor if not active else Qt.CursorShape.PointingHandCursor
        )

    def mousePressEvent(self, event):
        if self._active and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._key)


# ══════════════════════════════════════════════════════════════════════════════
#  BANCO DE PREGUNTAS  (pantalla 1)
# ══════════════════════════════════════════════════════════════════════════════

class BankScreen(QWidget):
    files_selected = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self._all_paths: list[Path] = []
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(52, 48, 52, 48)
        root.setSpacing(0)

        # ── Cabecera ──────────────────────────────────────────────────────────
        logo_row = QHBoxLayout()
        logo_row.setSpacing(0)

        accent_bar = QFrame()
        accent_bar.setFixedWidth(4)
        accent_bar.setStyleSheet(
            f"background: {C['acc']}; border-radius: 2px; border: none;"
        )
        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        title_col.setContentsMargins(16, 2, 0, 2)

        title_col.addWidget(_label("Exam Simulator", C["text"], size=26, bold=True))
        title_col.addWidget(_label(
            f"v{APP_VERSION}  ·  Simulador de examen de selección múltiple",
            C["text3"], size=12
        ))
        logo_row.addWidget(accent_bar)
        logo_row.addLayout(title_col)
        logo_row.addStretch()
        root.addLayout(logo_row)
        root.addSpacing(32)
        root.addWidget(_hline())
        root.addSpacing(26)

        # ── Sección banco ─────────────────────────────────────────────────────
        sect_row = QHBoxLayout()
        sect_lbl = _label("BANCO DE PREGUNTAS", C["text3"], size=11, bold=True)
        sect_lbl.setStyleSheet(sect_lbl.styleSheet() + " letter-spacing: 2px;")
        self.btn_refresh = _btn("🔄  Refresh")
        self.btn_refresh.clicked.connect(self._refresh)
        sect_row.addWidget(sect_lbl)
        sect_row.addStretch()
        sect_row.addWidget(self.btn_refresh)
        root.addLayout(sect_row)
        root.addSpacing(10)

        self.err_lbl = _label("", C["err"], size=13)
        self.err_lbl.hide()
        root.addWidget(self.err_lbl)

        self.list_widget = QListWidget()
        self.list_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.list_widget.itemDoubleClicked.connect(self._on_load_selected)
        root.addWidget(self.list_widget, 1)

        root.addSpacing(24)

        # ── Botones ───────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.btn_all  = _btn("Cargar todo", min_w=130)
        self.btn_load = _btn("Cargar seleccionado  →", cls="primary", min_w=210)
        self.btn_all.setEnabled(False)
        self.btn_load.setEnabled(False)

        self.btn_all.clicked.connect(self._on_load_all)
        self.btn_load.clicked.connect(self._on_load_selected)

        self.btn_open = _btn("📂  Abrir banco")
        self.btn_open.clicked.connect(self._open_bank_folder)

        self.btn_import = _btn("⬆  Importar JSON")
        self.btn_import.clicked.connect(self._import_json)

        self.btn_gen = _btn("✏  Generar examen")
        self.btn_gen.clicked.connect(self._open_generator)

        btn_row.addWidget(self.btn_open)
        btn_row.addWidget(self.btn_import)
        btn_row.addWidget(self.btn_gen)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_all)
        btn_row.addWidget(self.btn_load)
        root.addLayout(btn_row)

        self.list_widget.itemSelectionChanged.connect(
            lambda: self.btn_load.setEnabled(bool(self.list_widget.selectedItems()))
        )

    def _open_generator(self, import_file: Path | None = None):
        import subprocess, sys
        if getattr(sys, "frozen", False):
            target = _script_dir() / "exam_generator.exe"
        else:
            target = _script_dir() / "exam_generator.py"
        if not target.exists():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, "Archivo no encontrado",
                f"No se encontró {target.name} junto al ejecutable."
            )
            return
        cmd = [str(target)] if getattr(sys, "frozen", False) else [sys.executable, str(target)]
        if import_file:
            cmd += ["--import-file", str(import_file)]
        subprocess.Popen(cmd)
        # Diferir quit() para que subprocess arranque antes de que Qt limpie todo
        QTimer.singleShot(200, QApplication.instance().quit)

    def _import_json(self):
        """Abre diálogo, importa un JSON y lo carga directamente en configuración."""
        bank = _script_dir() / BANK_DIR_NAME
        bank.mkdir(exist_ok=True)
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Importar archivo JSON",
            str(bank),
            "Archivos JSON (*.json)"
        )
        if not path_str:
            return
        try:
            with open(path_str, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error al importar")
            msg.setText(f"No se pudo leer el archivo:\n\n{e}")
            msg.exec()
            return

        if isinstance(data, list):
            questions, warnings = [], []
            for i, q in enumerate(data, 1):
                qs, ws = [q], []
                if isinstance(q, dict):
                    err = _validate_question(q)
                    if err:
                        warnings.append(f"#{i}: {err}")
                        continue
                    q = dict(q)
                    q["correct"] = next(k for k in q["options"] if k.upper() == q["correct"].upper())
                    q["_source"] = Path(path_str).stem
                    questions.append(q)
                else:
                    warnings.append(f"#{i}: no es un objeto")
        elif isinstance(data, dict):
            questions, warnings = load_json(Path(path_str))
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Formato no reconocido")
            msg.setText("El archivo no tiene el formato esperado de Exam Simulator.")
            msg.exec()
            return

        if not questions:
            msg = QMessageBox(self)
            msg.setWindowTitle("Sin preguntas válidas")
            msg.setText(
                "El archivo no contiene preguntas válidas.\n\n"
                + ("\n".join(warnings[:5]) if warnings else "")
            )
            msg.exec()
            return

        # Emitir como si el usuario hubiera seleccionado archivos normales
        self.files_selected.emit([Path(path_str)])

    def _open_bank_folder(self):
        import subprocess, platform
        bank = _script_dir() / BANK_DIR_NAME
        bank.mkdir(exist_ok=True)
        system = platform.system()
        if system == "Windows":
            subprocess.Popen(["explorer", str(bank)])
        elif system == "Darwin":
            subprocess.Popen(["open", str(bank)])
        else:
            subprocess.Popen(["xdg-open", str(bank)])

    def _refresh(self):
        self.list_widget.clear()
        self._all_paths.clear()
        self.err_lbl.hide()

        bank = discover_bank()
        if "error" in bank:
            self.err_lbl.setText(bank["error"])
            self.err_lbl.show()
            self.btn_all.setEnabled(False)
            return

        for name, paths in bank.get("folders", {}).items():
            n    = len(paths)
            item = QListWidgetItem(
                f"   📁   {name}    —    {n} archivo{'s' if n != 1 else ''}"
            )
            item.setData(Qt.ItemDataRole.UserRole, paths)
            self.list_widget.addItem(item)
            self._all_paths.extend(paths)

        for p in bank.get("loose", []):
            item = QListWidgetItem(f"   📄   {p.stem}")
            item.setData(Qt.ItemDataRole.UserRole, [p])
            self.list_widget.addItem(item)
            self._all_paths.append(p)

        self.btn_all.setEnabled(bool(self._all_paths))

    def _on_load_selected(self):
        items = self.list_widget.selectedItems()
        if not items:
            return
        self.files_selected.emit(items[0].data(Qt.ItemDataRole.UserRole))

    def _on_load_all(self):
        self.files_selected.emit(self._all_paths)


# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN  (pantalla 2)
# ══════════════════════════════════════════════════════════════════════════════

class SetupScreen(QWidget):
    exam_ready = pyqtSignal(object)
    back       = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._questions: list[dict] = []
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header (coherente con BankScreen) ────────────────────────────────
        header = QFrame()
        header.setStyleSheet(
            f"QFrame {{ background: {C['surf']}; border-bottom: 1px solid {C['border']}; }}"
        )
        h_l = QHBoxLayout(header)
        h_l.setContentsMargins(52, 28, 52, 28)
        h_l.setSpacing(0)

        accent_bar = QFrame()
        accent_bar.setFixedWidth(4)
        accent_bar.setFixedHeight(36)
        accent_bar.setStyleSheet(
            f"background: {C['acc']}; border-radius: 2px; border: none;"
        )
        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        title_col.setContentsMargins(16, 0, 0, 0)
        title_col.addWidget(_label("Configurar examen", C["text"], size=22, bold=True))
        self.source_lbl = _label("", C["text3"], size=12)
        title_col.addWidget(self.source_lbl)

        h_l.addWidget(accent_bar)
        h_l.addLayout(title_col)
        h_l.addStretch()
        root.addWidget(header)

        # ── Cuerpo ────────────────────────────────────────────────────────────
        body = QWidget()
        body.setStyleSheet(f"background: {C['bg']};")
        body_l = QVBoxLayout(body)
        body_l.setContentsMargins(52, 40, 52, 40)
        body_l.setSpacing(0)

        # Número de preguntas
        row_n = QHBoxLayout()
        row_n.setSpacing(12)
        row_n.addWidget(_label("Número de preguntas:", size=13))
        self.spin = QSpinBox()
        self.spin.setMinimum(1)
        self._total_lbl = _label("de —", C["text3"], size=13)
        self.spin.valueChanged.connect(self._on_spin_change)
        row_n.addWidget(self.spin)
        row_n.addWidget(self._total_lbl)
        row_n.addStretch()
        body_l.addLayout(row_n)
        body_l.addSpacing(28)

        self.chk_q = QCheckBox("Mezclar preguntas")
        self.chk_q.setChecked(True)
        self.chk_o = QCheckBox("Mezclar orden de opciones")
        self.chk_o.setChecked(False)
        body_l.addWidget(self.chk_q)
        body_l.addSpacing(12)
        body_l.addWidget(self.chk_o)
        body_l.addSpacing(20)

        self.warn_lbl = _label("", C["warn"], size=12)
        self.warn_lbl.hide()
        body_l.addWidget(self.warn_lbl)
        body_l.addStretch()
        root.addWidget(body, 1)

        # ── Barra inferior ────────────────────────────────────────────────────
        bottom = QFrame()
        bottom.setStyleSheet(
            f"QFrame {{ background: {C['surf']}; border-top: 1px solid {C['border']}; }}"
        )
        bot_l = QHBoxLayout(bottom)
        bot_l.setContentsMargins(52, 20, 52, 20)
        bot_l.setSpacing(12)
        self.btn_back  = _btn("← Volver")
        self.btn_start = _btn("Comenzar  →", cls="primary", min_w=160)
        self.btn_back.clicked.connect(self.back.emit)
        self.btn_start.clicked.connect(self._start)
        bot_l.addWidget(self.btn_back)
        bot_l.addStretch()
        bot_l.addWidget(self.btn_start)
        root.addWidget(bottom)

    def load_questions(self, questions: list[dict], warnings: list[str] = None):
        self._questions = questions
        n = len(questions)
        self.spin.setMaximum(n)
        self.spin.setValue(n)
        self._total_lbl.setText(f"de {n} pregunta{'s' if n != 1 else ''}")
        self.source_lbl.setText(
            f"{n} pregunta{'s' if n != 1 else ''} disponible{'s' if n != 1 else ''}"
        )
        if warnings:
            self.warn_lbl.setText("⚠   " + "\n".join(warnings[:6]))
            self.warn_lbl.show()
        else:
            self.warn_lbl.hide()

    def _on_spin_change(self, value: int):
        total = self.spin.maximum()
        self._total_lbl.setText(f"de {total} pregunta{'s' if total != 1 else ''}")

    def _start(self):
        qs = self._questions[:]
        if self.chk_q.isChecked():
            random.shuffle(qs)
        qs = qs[:self.spin.value()]
        self.exam_ready.emit(ExamEngine(qs, shuffle_options=self.chk_o.isChecked()))


# ══════════════════════════════════════════════════════════════════════════════
#  EXAMEN  (pantalla 3)
# ══════════════════════════════════════════════════════════════════════════════

class ExamScreen(QWidget):
    exam_finished = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self._engine:      ExamEngine | None = None
        self._selected_key: str | None       = None
        self._opt_buttons: list[OptionButton] = []
        self._elapsed = 0
        self._timer   = QTimer()
        self._timer.timeout.connect(self._tick)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Barra superior ────────────────────────────────────────────────────
        top = QFrame()
        top.setStyleSheet(
            f"QFrame {{ background: {C['surf']}; border-bottom: 1px solid {C['border']}; }}"
        )
        top_l = QHBoxLayout(top)
        top_l.setContentsMargins(32, 20, 32, 20)
        top_l.setSpacing(16)

        self.lbl_prog   = _label("", C["text"],  size=13, bold=True)
        self.lbl_source = _label("", C["text3"], size=11)
        self.lbl_timer  = QLabel("00:00")
        self.lbl_timer.setStyleSheet(
            f"color: {C['acc']}; font-size: 13px; font-weight: 700; "
            "font-family: 'Consolas', 'Courier New', monospace;"
        )
        self.lbl_timer.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        top_l.addWidget(self.lbl_prog)
        top_l.addWidget(self.lbl_source)
        top_l.addStretch()
        top_l.addWidget(self.lbl_timer)
        root.addWidget(top)

        # Barra de progreso
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(4)
        root.addWidget(self.progress)

        # ── Área scrollable ───────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"background: {C['bg']};")

        content = QWidget()
        content.setStyleSheet(f"background: {C['bg']};")
        self.cl = QVBoxLayout(content)
        self.cl.setContentsMargins(52, 40, 52, 36)
        self.cl.setSpacing(0)

        # Badge de categoría (sin dificultad)
        self.badge_row = QHBoxLayout()
        self.badge_row.setSpacing(8)
        self.badge_row.setContentsMargins(0, 0, 0, 14)
        self.lbl_cat = QLabel()
        self.lbl_cat.hide()
        self.badge_row.addWidget(self.lbl_cat)
        self.badge_row.addStretch()
        self.cl.addLayout(self.badge_row)

        # Tarjeta de pregunta
        self.lbl_q = QLabel()
        self.lbl_q.setWordWrap(True)
        self.lbl_q.setStyleSheet(
            f"color: {C['text']}; font-size: 15px; font-weight: 600; "
            f"background: {C['surf']}; "
            f"border: 1px solid {C['border']}; "
            "border-radius: 10px; padding: 22px 26px; line-height: 1.5;"
        )
        self.cl.addWidget(self.lbl_q)
        self.cl.addSpacing(20)

        # Opciones
        self.opts_layout = QVBoxLayout()
        self.opts_layout.setSpacing(9)
        self.cl.addLayout(self.opts_layout)
        self.cl.addSpacing(16)

        # Explicación — visible solo tras confirmar
        self.explanation_box = QFrame()
        self.explanation_box.setStyleSheet(
            f"QFrame {{ background: #f0f7ff; border: 1px solid {C['acc']}; border-radius: 8px; }}"
        )
        exp_l = QHBoxLayout(self.explanation_box)
        exp_l.setContentsMargins(16, 12, 16, 12)
        exp_l.setSpacing(12)
        exp_icon = QLabel("ℹ")
        exp_icon.setAlignment(Qt.AlignmentFlag.AlignTop)
        exp_icon.setFixedWidth(18)
        exp_icon.setStyleSheet(
            f"color: {C['acc']}; font-size: 15px; font-weight: 700; "
            "background: transparent; border: none;"
        )
        self.lbl_explanation = QLabel()
        self.lbl_explanation.setWordWrap(True)
        self.lbl_explanation.setStyleSheet(
            f"color: {C['text2']}; font-size: 13px; font-style: italic; "
            "background: transparent; border: none;"
        )
        exp_l.addWidget(exp_icon)
        exp_l.addWidget(self.lbl_explanation, 1)
        self.explanation_box.hide()
        self.cl.addWidget(self.explanation_box)
        self.cl.addStretch()

        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        # ── Barra inferior ────────────────────────────────────────────────────
        bottom = QFrame()
        bottom.setStyleSheet(
            f"QFrame {{ background: {C['surf']}; border-top: 1px solid {C['border']}; }}"
        )
        bot_l = QHBoxLayout(bottom)
        bot_l.setContentsMargins(32, 18, 32, 18)
        bot_l.setSpacing(12)

        self.lbl_feedback = QLabel("")
        self.lbl_feedback.setStyleSheet("font-size: 13px; font-weight: 700;")

        self.btn_skip    = _btn("Saltar")
        self.btn_confirm = _btn("Confirmar", cls="primary", min_w=140)
        self.btn_next    = _btn("Siguiente  →", cls="primary", min_w=160)
        self.btn_confirm.setEnabled(False)
        self.btn_next.hide()

        self.btn_skip.clicked.connect(self._skip)
        self.btn_confirm.clicked.connect(self._confirm)
        self.btn_next.clicked.connect(self._advance)

        bot_l.addWidget(self.lbl_feedback, 1)
        bot_l.addWidget(self.btn_skip)
        bot_l.addWidget(self.btn_confirm)
        bot_l.addWidget(self.btn_next)
        root.addWidget(bottom)

    def start_exam(self, engine: ExamEngine):
        self._engine  = engine
        self._elapsed = 0
        self._timer.start(1000)
        self._load_question()

    def _tick(self):
        self._elapsed += 1
        m, s = divmod(self._elapsed, 60)
        self.lbl_timer.setText(f"{m:02d}:{s:02d}")

    def _load_question(self):
        e = self._engine
        if e.done:
            self._finish(); return

        self._selected_key = None
        item = e.current
        q    = item["q"]
        idx  = e.current_idx + 1

        self.progress.setMaximum(e.total)
        self.progress.setValue(idx - 1)
        self.lbl_prog.setText(f"Pregunta  {idx} / {e.total}")
        self.lbl_source.setText(q.get("_source", ""))

        # Categoría (sin dificultad)
        cat = q.get("category", "")
        if cat:
            self.lbl_cat.setText(cat)
            self.lbl_cat.setStyleSheet(
                f"color: {C['text2']}; background: {C['surf2']}; "
                f"border: 1px solid {C['border']}; "
                "border-radius: 5px; padding: 3px 12px; font-size: 11px;"
            )
            self.lbl_cat.show()
        else:
            self.lbl_cat.hide()

        self.lbl_q.setText(q["question"])

        self._clear_opts()
        for key, text in item["display_opts"].items():
            btn = OptionButton(key, text)
            btn.clicked.connect(self._select_option)
            self.opts_layout.addWidget(btn)
            self._opt_buttons.append(btn)

        self.lbl_feedback.setText("")
        self.explanation_box.hide()
        self.btn_skip.show()
        self.btn_confirm.setEnabled(False)
        self.btn_confirm.show()
        self.btn_next.hide()

    def _clear_opts(self):
        for b in self._opt_buttons:
            b.deleteLater()
        self._opt_buttons.clear()

    def _select_option(self, key: str):
        if self.btn_next.isVisible():
            return
        self._selected_key = key
        for b in self._opt_buttons:
            b.set_state("sel" if b.key == key else "")
        self.btn_confirm.setEnabled(True)

    def _confirm(self):
        if self._selected_key is None:
            return
        e            = self._engine
        item         = e.current
        is_ok        = e.submit(self._selected_key)
        correct_text = item["correct_text"]

        for b in self._opt_buttons:
            v = item["display_opts"].get(b.key, "")
            if b.key == self._selected_key:
                b.set_state("ok" if is_ok else "err")
            elif v == correct_text:
                b.set_state("reveal")
            else:
                b.set_state("")
            b.set_active(False)

        if is_ok:
            self.lbl_feedback.setText("✔   ¡Correcto!")
            self.lbl_feedback.setStyleSheet(
                f"color: {C['ok']}; font-size: 13px; font-weight: 700;"
            )
        else:
            self.lbl_feedback.setText("✗   Incorrecto")
            self.lbl_feedback.setStyleSheet(
                f"color: {C['err']}; font-size: 13px; font-weight: 700;"
            )

        self.btn_skip.hide()
        self.btn_confirm.hide()
        self.btn_next.setText("Ver resultados  →" if e.done else "Siguiente  →")
        self.btn_next.show()

        # Explicación (si existe)
        explanation = item["q"].get("explanation", "").strip()
        if explanation:
            self.lbl_explanation.setText(explanation)
            self.explanation_box.show()
        else:
            self.explanation_box.hide()

    def _skip(self):
        self._engine.submit(None)
        self.lbl_feedback.setText("")
        if self._engine.done:
            self._finish()
        else:
            self._load_question()

    def _advance(self):
        if self._engine.done:
            self._finish()
        else:
            self._load_question()

    def _finish(self):
        self._timer.stop()
        self._clear_opts()
        self.exam_finished.emit(self._engine)


# ══════════════════════════════════════════════════════════════════════════════
#  DONUT CHART
# ══════════════════════════════════════════════════════════════════════════════

from PyQt6.QtGui import QPainter, QPen, QColor, QConicalGradient
from PyQt6.QtCore import QRectF, QEasingCurve

class DonutChart(QWidget):
    """
    Gráfico de dona animado. Muestra el porcentaje de acierto como un arco
    que se llena desde 0 hasta el valor final al llamar a set_value().
    """
    def __init__(self, size: int = 200, thickness: int = 18):
        super().__init__()
        self._size      = size
        self._thickness = thickness
        self._value     = 0.0        # porcentaje actual (0-100), animado
        self._target    = 0.0
        self._color     = C["acc"]
        self._pct_lbl   = QLabel("0%", self)
        self._pct_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_lbl  = QLabel("", self)
        self._icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(size, size)

        self._timer = QTimer()
        self._timer.setInterval(12)   # ~80 fps
        self._timer.timeout.connect(self._step)

    def set_value(self, pct: float, color: str):
        self._target = pct
        self._color  = color
        self._value  = 0.0
        font_size = min(self._size // 6, 32)
        self._pct_lbl.setStyleSheet(
            f"color: {color}; font-size: {font_size}px; font-weight: 800; "
            "background: transparent; border: none;"
        )
        icon = "🏆" if pct == 100 else ("✔" if pct >= 70 else ("⚠" if pct >= 50 else "✗"))
        icon_size = min(self._size // 10, 20)
        self._icon_lbl.setStyleSheet(
            f"color: {color}; font-size: {icon_size}px; "
            "background: transparent; border: none;"
        )
        self._icon_lbl.setText(icon)
        self._pct_lbl.setText("0%")
        self._reposition_labels()
        self._timer.start()

    def _reposition_labels(self):
        cx = self._size // 2
        cy = self._size // 2
        # Ancho generoso para que "100.0%" no se corte nunca
        w      = self._size * 72 // 100
        h_pct  = self._size // 6 + 8
        h_icon = self._size // 10 + 6
        total_h = h_pct + 4 + h_icon
        self._pct_lbl.setFixedWidth(w)
        self._pct_lbl.setFixedHeight(h_pct)
        self._pct_lbl.move(cx - w // 2, cy - total_h // 2)
        self._icon_lbl.setFixedWidth(w)
        self._icon_lbl.setFixedHeight(h_icon)
        self._icon_lbl.move(cx - w // 2, cy - total_h // 2 + h_pct + 4)

    def _step(self):
        step = max(0.5, (self._target - self._value) * 0.08)
        self._value = min(self._value + step, self._target)
        self._pct_lbl.setText(f"{self._value:.1f}%")
        self.update()
        if self._value >= self._target:
            self._value = self._target
            self._pct_lbl.setText(f"{self._target:.1f}%")
            self._timer.stop()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        t   = self._thickness
        pad = t // 2 + 2
        rect = QRectF(pad, pad, self._size - pad * 2, self._size - pad * 2)

        # Pista de fondo
        pen = QPen(QColor(C["surf2"]))
        pen.setWidth(t)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        p.setPen(pen)
        p.drawArc(rect, 0, 360 * 16)

        # Arco de progreso
        if self._value > 0:
            pen.setColor(QColor(self._color))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            span = int(self._value / 100 * 360 * 16)
            p.drawArc(rect, 90 * 16, -span)

        p.end()


# ── Panel de resumen reutilizable (izquierdo en modo revisión, centrado en modo resultados)

def _build_summary_panel(
    results: dict,
    btn_repeat: QPushButton,
    btn_new: QPushButton,
    btn_review: QPushButton,
    donut_size: int = 220,
    compact: bool = False,
    btn_extra: QPushButton | None = None,
) -> tuple[QWidget, DonutChart]:
    """
    Construye el panel de resumen con dona + estadísticas + botones de acción.
    Devuelve (widget, donut) para poder animar la dona después.
    """
    margins = 20 if compact else 36
    panel = QWidget()
    panel.setStyleSheet(f"background: {C['bg']};")
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(margins, margins, margins, margins)
    layout.setSpacing(0)

    # Dona
    donut = DonutChart(size=donut_size, thickness=20 if not compact else 15)
    donut_row = QHBoxLayout()
    donut_row.addStretch()
    donut_row.addWidget(donut)
    donut_row.addStretch()
    layout.addLayout(donut_row)
    layout.addSpacing(16 if compact else 24)

    # Estadísticas en chips
    pct = results["pct"]
    if pct >= 70:   clr = C["ok"]
    elif pct >= 50: clr = C["warn"]
    else:           clr = C["err"]

    m, s = divmod(results["elapsed"], 60)

    # En compacto: chips más estrechos para caber en 300px de panel
    chip_w      = 72  if compact else 100
    chip_pad    = 6   if compact else 14
    val_size    = 15  if compact else 18
    cap_size    = 9   if compact else 10
    chip_space  = 6   if compact else 10

    def _chip(text: str, color: str) -> QFrame:
        f = QFrame()
        f.setStyleSheet(
            f"QFrame {{ background: {C['surf']}; border: 1px solid {C['border']}; "
            "border-radius: 8px; }}"
        )
        f.setFixedWidth(chip_w)
        l = QVBoxLayout(f)
        l.setContentsMargins(chip_pad, 7, chip_pad, 7)
        l.setSpacing(2)
        val, cap = text.split("|")
        v = QLabel(val)
        v.setStyleSheet(
            f"color: {color}; font-size: {val_size}px; font-weight: 800; "
            "background: transparent; border: none;"
        )
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c = QLabel(cap)
        c.setStyleSheet(
            f"color: {C['text3']}; font-size: {cap_size}px; background: transparent; border: none;"
        )
        c.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(v); l.addWidget(c)
        return f

    chips = QHBoxLayout()
    chips.setSpacing(chip_space)
    chips.setContentsMargins(0, 0, 0, 0)
    chips.addStretch()
    chips.addWidget(_chip(f"{len(results['correct'])}|Correctas",   C["ok"]))
    chips.addWidget(_chip(f"{len(results['incorrect'])}|Incorrectas", C["err"]))
    chips.addWidget(_chip(f"{len(results['skipped'])}|Saltadas",    C["warn"]))
    chips.addStretch()
    layout.addLayout(chips)
    layout.addSpacing(8)

    # Tiempo y total
    meta_row = QHBoxLayout()
    meta_row.addStretch()
    meta_row.addWidget(_label(
        f"{results['total']} preguntas  ·  {m:02d}:{s:02d}",
        C["text3"], size=12,
        align=Qt.AlignmentFlag.AlignCenter
    ))
    meta_row.addStretch()
    layout.addLayout(meta_row)
    layout.addSpacing(32)

    # Botones de acción
    btns = [btn_repeat, btn_new, btn_review]
    if btn_extra:
        btns.append(btn_extra)
    for btn in btns:
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        layout.addSpacing(8)

    layout.addStretch()

    # Disparar animación de la dona
    QTimer.singleShot(120, lambda: donut.set_value(pct, clr))

    return panel, donut


# ══════════════════════════════════════════════════════════════════════════════
#  RESULTADOS  (pantalla 4)
# ══════════════════════════════════════════════════════════════════════════════

class ChroniCatorExportDialog(QDialog):
    """
    Diálogo modal nativo (QDialog) para exportar sesión a Chronicator.
    Usa exec() para gestión correcta del event loop en Windows.
    """
    def __init__(self, parent, engine: ExamEngine):
        super().__init__(parent)
        self.setWindowTitle("Exportar a Chronicator")
        self.setMinimumWidth(480)
        self.setModal(True)
        self._engine   = engine
        self._selected: str | None = None
        self._export_ok = False   # resultado tras exec()
        self._build_ui()
        self._load_players()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(14)

        title = QLabel("Exportar a Chronicator")
        title.setStyleSheet(
            f"color: {C['text']}; font-size: 16px; font-weight: 700; "
            "background: transparent; border: none;"
        )
        root.addWidget(title)

        sub = QLabel("Selecciona un jugador o crea uno nuevo.")
        sub.setStyleSheet(
            f"color: {C['text3']}; font-size: 12px; "
            "background: transparent; border: none;"
        )
        root.addWidget(sub)

        self._list_widget = QListWidget()
        self._list_widget.setStyleSheet(
            f"QListWidget {{ background: {C['surf']}; border: 1px solid {C['border']}; "
            "border-radius: 8px; padding: 4px; }}"
            f"QListWidget::item {{ padding: 10px 14px; border-radius: 6px; }}"
            f"QListWidget::item:selected {{ background: {C['acc_l']}; color: {C['acc']}; }}"
            f"QListWidget::item:hover {{ background: {C['surf2']}; }}"
        )
        self._list_widget.itemSelectionChanged.connect(self._on_selection)
        self._list_widget.setMinimumHeight(140)
        root.addWidget(self._list_widget)

        new_row = QHBoxLayout()
        new_row.setSpacing(8)
        self._new_input = QLineEdit()
        self._new_input.setMaxLength(40)
        self._new_input.setPlaceholderText("Nombre del nuevo jugador...")
        self._new_input.returnPressed.connect(self._create_player)
        new_row.addWidget(self._new_input, 1)
        btn_create = _btn("＋  Crear")
        btn_create.clicked.connect(self._create_player)
        new_row.addWidget(btn_create)
        root.addLayout(new_row)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = _btn("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        self._btn_confirm = _btn("Exportar  →", cls="primary", min_w=140)
        self._btn_confirm.setEnabled(False)
        self._btn_confirm.clicked.connect(self._do_export)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(self._btn_confirm)
        root.addLayout(btn_row)

    # ── Lógica ────────────────────────────────────────────────────────────────

    def _players_dir(self) -> Path:
        return _script_dir() / PLAYERS_DIR_NAME

    def _load_players(self):
        self._list_widget.clear()
        pd = self._players_dir()
        if pd.exists():
            for p in sorted(pd.iterdir()):
                if p.is_dir():
                    self._list_widget.addItem(p.name)

    def _on_selection(self):
        items = self._list_widget.selectedItems()
        self._selected = items[0].text() if items else None
        self._btn_confirm.setEnabled(bool(self._selected))

    def _create_player(self):
        import re as _re
        name = _re.sub(r"[<>:/|?*]", "", self._new_input.text()).strip()
        if not name:
            return
        (self._players_dir() / name / "sessions").mkdir(parents=True, exist_ok=True)
        self._new_input.clear()
        self._load_players()
        for i in range(self._list_widget.count()):
            if self._list_widget.item(i).text() == name:
                self._list_widget.setCurrentRow(i)
                break

    def _do_export(self):
        if not self._selected:
            return
        sessions_dir = self._players_dir() / self._selected / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        n = 1
        while (sessions_dir / f"{today}_{n:03d}.json").exists():
            n += 1
        session_file = sessions_dir / f"{today}_{n:03d}.json"

        results_export = []
        for a in self._engine.answers:
            q    = a["question"]
            q_id = hashlib.sha256(q["question"].encode()).hexdigest()[:16]
            results_export.append({
                "question_id":  q_id,
                "category":     q.get("category", "default"),
                "difficulty":   q.get("difficulty", ""),
                "selected":     a.get("original_chosen") or "",
                "correct":      a.get("original_correct") or q.get("correct", ""),
                "time_seconds": a.get("time_seconds", 0),
            })

        session_data = {
            "session_id":  (f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
                            f"-{str(uuid.uuid4())[:8]}"),
            "exported_at": datetime.now().isoformat(timespec="seconds"),
            "exam_title":  (self._engine.answers[0]["question"].get("_source", "Examen")
                            if self._engine.answers else "Examen"),
            "results":     results_export,
        }

        try:
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            QMessageBox.critical(self, "Error al exportar", str(e))
            return

        # Guardar info para el mensaje post-cierre
        self._export_player = self._selected
        self._export_file   = session_file.name
        self._export_ok     = True
        self.accept()   # cierra el diálogo de forma limpia


class ResultsScreen(QWidget):
    action              = pyqtSignal(str)
    export_chronicator  = pyqtSignal(object)  # engine   # "repeat" | "new" | "exit"

    def __init__(self):
        super().__init__()
        self._results: dict = {}
        self._build_ui()

    def _build_ui(self):
        # Root layout — contiene el stack interno (resumen / revisión) + barra inferior
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header consistente con el resto de pantallas ──────────────────────
        header = QFrame()
        header.setStyleSheet(
            f"QFrame {{ background: {C['surf']}; border-bottom: 1px solid {C['border']}; }}"
        )
        h_l = QHBoxLayout(header)
        h_l.setContentsMargins(52, 28, 52, 28)
        h_l.setSpacing(0)

        accent_bar = QFrame()
        accent_bar.setFixedWidth(4)
        accent_bar.setFixedHeight(36)
        accent_bar.setStyleSheet(
            f"background: {C['acc']}; border-radius: 2px; border: none;"
        )
        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        title_col.setContentsMargins(16, 0, 0, 0)
        title_col.addWidget(_label("Resultados", C["text"], size=22, bold=True))
        self._header_source_lbl = _label("Exam Simulator", C["text3"], size=12)
        self._header_source_lbl.setWordWrap(False)
        self._header_source_lbl.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        title_col.addWidget(self._header_source_lbl)

        h_l.addWidget(accent_bar)
        h_l.addLayout(title_col)
        h_l.addStretch()
        root.addWidget(header)

        # Stack interno: 0 = pantalla resumen, 1 = pantalla revisión
        self._inner = QStackedWidget()
        root.addWidget(self._inner, 1)

        # ── Barra inferior fija ────────────────────────────────────────────────
        bottom = QFrame()
        bottom.setStyleSheet(
            f"QFrame {{ background: {C['surf']}; border-top: 1px solid {C['border']}; }}"
        )
        bot_l = QHBoxLayout(bottom)
        bot_l.setContentsMargins(32, 20, 32, 20)
        self._btn_exit = _btn("Salir", cls="danger")
        self._btn_exit.clicked.connect(lambda: self.action.emit("exit"))
        bot_l.addStretch()
        bot_l.addWidget(self._btn_exit)
        root.addWidget(bottom)

        # Las dos pantallas se construyen en load_results()
        # porque necesitan los datos del examen.

    def load_results(self, engine: ExamEngine):
        self._results = engine.results()
        self._engine  = engine
        r = self._results

        # Nombre del examen en el header
        source = ""
        if engine.answers:
            source = engine.answers[0]["question"].get("_source", "")
        self._header_source_lbl.setText(source or "Exam Simulator")

        # Limpiar pantallas anteriores
        while self._inner.count():
            w = self._inner.widget(0)
            self._inner.removeWidget(w)
            w.deleteLater()

        # Botones compartidos (se añaden a la pantalla resumen)
        btn_repeat = _btn("⟳   Repetir", min_w=180)
        btn_new    = _btn("⊕   Nuevo test", min_w=180)
        btn_review = QPushButton("Ver revisión  →")
        btn_review.setMinimumWidth(200)
        btn_review.setStyleSheet(
            f"background: {C['acc']}; color: #ffffff; border: none; "
            "border-radius: 7px; padding: 9px 28px; font-weight: 700; font-size: 13px;")
        btn_review.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_repeat.clicked.connect(lambda: self.action.emit("repeat"))
        btn_new.clicked.connect(lambda: self.action.emit("new"))
        btn_review.clicked.connect(self._show_review)

        # ── Pantalla 0: Resumen (pantalla completa) ───────────────────────────
        summary_w, _ = _build_summary_panel(
            r, btn_repeat, btn_new, btn_review,
            donut_size=240, compact=False
        )
        self._inner.addWidget(summary_w)

        # ── Pantalla 1: Revisión (split) ──────────────────────────────────────
        review_w = QWidget()
        review_w.setStyleSheet(f"background: {C['bg']};")
        split = QHBoxLayout(review_w)
        split.setContentsMargins(0, 0, 0, 0)
        split.setSpacing(0)

        # Panel izquierdo fijo
        left_panel = QWidget()
        left_panel.setFixedWidth(300)
        left_panel.setStyleSheet(
            f"background: {C['surf']}; border-right: 1px solid {C['border']};"
        )

        def _styled_btn(text, min_w=160):
            b = QPushButton(text)
            b.setMinimumWidth(min_w)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(
                f"QPushButton {{ background: {C['surf2']}; color: {C['text2']}; "
                f"border: 1px solid {C['border']}; border-radius: 7px; "
                "padding: 8px 22px; font-weight: 500; }}"
                f"QPushButton:hover {{ border-color: {C['acc']}; color: {C['acc']}; "
                f"background: {C['acc_l']}; }}"
                f"QPushButton:pressed {{ background: {C['surf2']}; }}"
            )
            return b

        btn_repeat2 = _styled_btn("⟳   Repetir")
        btn_new2    = _styled_btn("⊕   Nuevo test")
        btn_back    = _styled_btn("← Resultados")

        btn_repeat2.clicked.connect(lambda: self.action.emit("repeat"))
        btn_new2.clicked.connect(lambda: self.action.emit("new"))
        btn_back.clicked.connect(lambda: self._inner.setCurrentIndex(0))

        # Botón Chronicator — definido ANTES de usarlo en el panel
        btn_chron = QPushButton("📊  Exportar a Chronicator")
        btn_chron.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_chron.setStyleSheet(
            f"QPushButton {{ background: {C['surf2']}; color: {C['text2']}; "
            f"border: 1px solid {C['border']}; border-radius: 7px; "
            "padding: 8px 18px; font-weight: 500; }}"
            f"QPushButton:hover {{ border-color: {C['acc']}; color: {C['acc']}; "
            f"background: {C['acc_l']}; }}"
        )
        btn_chron.clicked.connect(lambda: self._open_chronicator_export(engine))

        left_w, _ = _build_summary_panel(
            r, btn_repeat2, btn_new2, btn_back,
            donut_size=160, compact=True,
            btn_extra=btn_chron
        )
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_scroll.setStyleSheet(f"background: {C['surf']}; border: none;")
        left_scroll.setWidget(left_w)

        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        left_layout.addWidget(left_scroll)



        # Panel derecho: tabs de revisión
        right_panel = QWidget()
        right_panel.setStyleSheet(f"background: {C['bg']};")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        tabs = QTabWidget()
        all_a = r["correct"] + r["incorrect"] + r["skipped"]
        tabs.addTab(self._build_tab(all_a),           f"Todas  ({r['total']})")
        tabs.addTab(self._build_tab(r["correct"]),    f"Correctas  ({len(r['correct'])})")
        tabs.addTab(self._build_tab(r["incorrect"]),  f"Incorrectas  ({len(r['incorrect'])})")
        tabs.addTab(self._build_tab(r["skipped"]),    f"Saltadas  ({len(r['skipped'])})")
        right_layout.addWidget(tabs)

        split.addWidget(left_panel)
        split.addWidget(right_panel, 1)
        self._inner.addWidget(review_w)

        # Mostrar resumen primero
        self._inner.setCurrentIndex(0)

    def _show_review(self):
        self._inner.setCurrentIndex(1)

    def _open_chronicator_export(self, engine: ExamEngine):
        dlg = ChroniCatorExportDialog(self, engine)
        dlg.exec()   # bloqueante y seguro — QDialog gestiona su propio event loop
        if dlg._export_ok:
            msg = QMessageBox(self)
            msg.setWindowTitle("Exportado a Chronicator")
            msg.setText(
                f"Sesión guardada correctamente.\n\n"
                f"Jugador: {dlg._export_player}\n"
                f"Archivo: {dlg._export_file}"
            )
            msg.setIcon(QMessageBox.Icon.NoIcon)   # sin icono → sin sonido del sistema
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

    def _build_tab(self, answers: list[dict]) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"background: {C['bg']}; border: none;")

        container = QWidget()
        container.setStyleSheet(f"background: {C['bg']};")
        layout = QVBoxLayout(container)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 16, 20, 16)

        if not answers:
            ph = _label(
                "No hay preguntas en esta categoría.",
                C["text3"], size=13,
                align=Qt.AlignmentFlag.AlignCenter
            )
            ph.setStyleSheet(ph.styleSheet() + " padding: 48px; background: transparent;")
            layout.addWidget(ph)
        else:
            for i, a in enumerate(answers, 1):
                layout.addWidget(self._answer_card(i, a))

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def _answer_card(self, index: int, answer: dict) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(
            f"QFrame {{ background: {C['surf']}; border: 1px solid {C['border']}; "
            "border-radius: 10px; }}"
        )
        layout = QVBoxLayout(frame)
        layout.setSpacing(7)
        layout.setContentsMargins(20, 16, 20, 16)

        q = answer["question"]
        base_meta = "background: transparent; border: none;"

        # Badge de categoría encima de la pregunta
        cat = q.get("category", "")
        cat_text = cat if (cat and cat != "default") else "no assigned"
        cat_badge = QLabel(cat_text)
        cat_badge.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        cat_badge.setStyleSheet(
            f"color: {C['text2']}; background: {C['surf2']}; "
            f"border: 1px solid {C['border2']}; border-radius: 10px; "
            "padding: 3px 12px; font-size: 11px; font-weight: 500;"
        )
        badge_row = QHBoxLayout()
        badge_row.addWidget(cat_badge)
        badge_row.addStretch()
        layout.addLayout(badge_row)
        layout.addSpacing(6)

        # Pregunta
        q_lbl = QLabel(f"{index}. {q['question']}")
        q_lbl.setWordWrap(True)
        q_lbl.setStyleSheet(
            f"color: {C['text']}; font-size: 13px; font-weight: 600; "
            "background: transparent; border: none;"
        )
        layout.addWidget(q_lbl)
        layout.addSpacing(6)

        correct_text = answer["correct_text"]
        chosen_key   = answer["chosen"]
        base_css     = "background: transparent; border: none;"

        # Usar display_opts (orden visto durante el examen) en vez de q["options"] (orden JSON original)
        opts_to_show = answer.get("display_opts", q["options"])
        for k, v in opts_to_show.items():
            is_correct = (v == correct_text)
            is_chosen  = chosen_key is not None and k.upper() == chosen_key.upper()

            row = QHBoxLayout()
            row.setSpacing(12)
            key_lbl = QLabel(k); key_lbl.setFixedWidth(20); key_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            val_lbl = QLabel(v); val_lbl.setWordWrap(True)
            tag_lbl = QLabel();  tag_lbl.setFixedWidth(148); tag_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            if is_correct and is_chosen:
                css = f"color: {C['ok']}; font-weight: 700; {base_css}"
                key_lbl.setStyleSheet(css); val_lbl.setStyleSheet(css)
                tag_lbl.setText("✔ correcta / elegida")
                tag_lbl.setStyleSheet(f"color: {C['ok']}; font-size: 11px; {base_css}")
            elif is_correct:
                css = f"color: {C['ok']}; font-weight: 600; {base_css}"
                key_lbl.setStyleSheet(css); val_lbl.setStyleSheet(css)
                tag_lbl.setText("✔ correcta")
                tag_lbl.setStyleSheet(f"color: {C['ok']}; font-size: 11px; {base_css}")
            elif is_chosen:
                css = f"color: {C['err']}; {base_css}"
                key_lbl.setStyleSheet(css); val_lbl.setStyleSheet(css)
                tag_lbl.setText("✗ tu respuesta")
                tag_lbl.setStyleSheet(f"color: {C['err']}; font-size: 11px; {base_css}")
            else:
                dim = f"color: {C['text3']}; {base_css}"
                key_lbl.setStyleSheet(dim); val_lbl.setStyleSheet(dim)
                tag_lbl.setText("·")
                tag_lbl.setStyleSheet(f"color: {C['text3']}; font-size: 18px; {base_css}")

            row.addWidget(key_lbl); row.addWidget(val_lbl, 1); row.addWidget(tag_lbl)
            layout.addLayout(row)

        if chosen_key is None:
            sl = QLabel("→ Saltada")
            sl.setStyleSheet(
                f"color: {C['warn']}; font-size: 12px; background: transparent; border: none;"
            )
            layout.addWidget(sl)

        if "explanation" in q:
            layout.addWidget(_hline())
            exp = QLabel(f"ℹ   {q['explanation']}")
            exp.setWordWrap(True)
            exp.setStyleSheet(
                f"color: {C['text2']}; font-size: 12px; font-style: italic; "
                "background: transparent; border: none;"
            )
            layout.addWidget(exp)

        return frame


# ══════════════════════════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Exam Simulator  v{APP_VERSION}")
        self.setMinimumSize(1080, 780)
        self.resize(1080, 780)
        self._questions: list[dict] = []

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.bank_s    = BankScreen()
        self.setup_s   = SetupScreen()
        self.exam_s    = ExamScreen()
        self.results_s = ResultsScreen()

        for s in (self.bank_s, self.setup_s, self.exam_s, self.results_s):
            self.stack.addWidget(s)

        self.bank_s.files_selected.connect(self._on_files_selected)
        self.setup_s.back.connect(lambda: self.stack.setCurrentIndex(0))
        self.setup_s.exam_ready.connect(self._on_exam_ready)
        self.exam_s.exam_finished.connect(self._on_exam_finished)
        self.results_s.action.connect(self._on_action)

        self.stack.setCurrentIndex(0)

    def _on_files_selected(self, paths: list):
        questions, warnings = load_files(paths)
        if not questions:
            msg = QMessageBox(self)
            msg.setWindowTitle("Sin preguntas válidas")
            msg.setText(
                "No se cargaron preguntas válidas.\n\n"
                "Revisa el formato de los archivos seleccionados."
            )
            if warnings:
                msg.setDetailedText("\n".join(warnings))
            msg.exec()
            return

        # ── Detectar incompatibilidad por archivo ────────────────────────────
        # Agrupar preguntas por _source para saber qué archivos tienen problemas
        from collections import defaultdict
        # Agrupar por _filename (único) no por _source (puede repetirse)
        by_file: dict = defaultdict(list)
        for q in questions:
            by_file[q.get("_filename", q.get("_source", "?"))].append(q)

        bad_files = []   # (filename, title, lista_campos_faltantes)
        for filename, qs in by_file.items():
            file_missing = []
            if not all(
                q.get("difficulty") and q["difficulty"] in ("easy","medium","hard","insane")
                for q in qs
            ):
                file_missing.append("dificultad")
            if not all(
                q.get("category") and q["category"] != "default"
                for q in qs
            ):
                file_missing.append("categoría")
            if file_missing:
                title_str = qs[0].get("_source", filename)
                bad_files.append((filename, title_str, file_missing))

        if bad_files:
            dlg = QDialog(self)
            dlg.setWindowTitle("Compatibilidad con Chronicator")
            dlg.setMinimumWidth(520)
            dlg.setModal(True)
            dlg_l = QVBoxLayout(dlg)
            dlg_l.setContentsMargins(28, 24, 28, 20)
            dlg_l.setSpacing(14)

            info_lbl = QLabel(
                f"Los siguientes archivos tienen campos incompletos. "
                f"Sus resultados no podrán usarse para el análisis "
                f"de estadísticas del Chronicator."
            )
            info_lbl.setWordWrap(True)
            info_lbl.setStyleSheet(
                f"color: {C['text']}; font-size: 13px; "
                "background: transparent; border: none;"
            )
            dlg_l.addWidget(info_lbl)

            # Lista con nombre de archivo + título + qué falta
            list_frame = QFrame()
            list_frame.setStyleSheet(
                f"QFrame {{ background: {C['surf2']}; border: 1px solid {C['border']}; "
                "border-radius: 8px; }}"
            )
            list_l = QVBoxLayout(list_frame)
            list_l.setContentsMargins(14, 10, 14, 10)
            list_l.setSpacing(6)
            for filename, title_str, file_miss in bad_files:
                # Nombre del archivo
                name_lbl = QLabel(f"📄  {filename}.json")
                name_lbl.setStyleSheet(
                    f"color: {C['text']}; font-size: 12px; font-weight: 500; "
                    "background: transparent; border: none;"
                )
                # Título si es distinto del nombre de archivo
                detail_parts = []
                if title_str != filename:
                    detail_parts.append(f'"{title_str}"')
                detail_parts.append(f"falta: {' y '.join(file_miss)}")
                detail_lbl = QLabel("     " + "  ·  ".join(detail_parts))
                detail_lbl.setStyleSheet(
                    f"color: {C['text3']}; font-size: 11px; "
                    "background: transparent; border: none;"
                )
                list_l.addWidget(name_lbl)
                list_l.addWidget(detail_lbl)
            dlg_l.addWidget(list_frame)

            q_lbl = QLabel(
                f"¿Quieres editarlos en el Generator o continuar de todas formas?"
            )
            q_lbl.setWordWrap(True)
            q_lbl.setStyleSheet(
                f"color: {C['text2']}; font-size: 13px; "
                "background: transparent; border: none;"
            )
            dlg_l.addWidget(q_lbl)

            btn_row = QHBoxLayout()
            btn_row.setSpacing(8)
            btn_cancel       = QPushButton("Cancelar")
            btn_edit         = QPushButton("Editar")
            btn_continue_dlg = QPushButton("Continuar")

            for b in (btn_cancel, btn_edit):
                b.setStyleSheet(
                    f"QPushButton {{ background: {C['surf']}; color: {C['text2']}; "
                    f"border: 1px solid {C['border']}; border-radius: 7px; "
                    "padding: 8px 20px; font-weight: 500; }}"
                    f"QPushButton:hover {{ border-color: {C['acc']}; "
                    f"color: {C['acc']}; background: {C['acc_l']}; }}"
                )
            btn_continue_dlg.setStyleSheet(
                f"QPushButton {{ background: {C['acc']}; color: #fff; "
                "border: none; border-radius: 7px; padding: 8px 20px; "
                "font-weight: 700; }}"
                f"QPushButton:hover {{ background: {C['acc_d']}; }}"
            )
            btn_cancel.clicked.connect(dlg.reject)
            btn_edit.clicked.connect(lambda: dlg.done(2))
            btn_continue_dlg.clicked.connect(dlg.accept)

            btn_row.addWidget(btn_cancel)
            btn_row.addStretch()
            btn_row.addWidget(btn_edit)
            btn_row.addWidget(btn_continue_dlg)
            dlg_l.addLayout(btn_row)

            result = dlg.exec()
            if result == 2:
                # Diferir con 150ms para que el QDialog se destruya completamente
                # antes de lanzar el generator y cerrar el simulador
                # Pasar el primer archivo incompatible para importarlo automáticamente
                first_bad = next(
                    (p for p in paths
                     if Path(p).stem in [f for f, _, _ in bad_files]),
                    paths[0]
                )
                QTimer.singleShot(150, lambda: self.bank_s._open_generator(Path(first_bad)))
                return
            elif result != 1:
                return

        self._questions = questions
        self.setup_s.load_questions(questions, warnings or None)
        self.stack.setCurrentIndex(1)

    def _on_exam_ready(self, engine: ExamEngine):
        self.exam_s.start_exam(engine)
        self.stack.setCurrentIndex(2)

    def _on_exam_finished(self, engine: ExamEngine):
        self.results_s.load_results(engine)
        self.stack.setCurrentIndex(3)

    def _on_action(self, action: str):
        if action == "repeat":
            self.setup_s.load_questions(self._questions)
            self.stack.setCurrentIndex(1)
        elif action == "new":
            self.bank_s._refresh()
            self.stack.setCurrentIndex(0)
        elif action == "exit":
            self.close()

    def closeEvent(self, event):
        # Si está en medio de un examen (pantalla 2), pedir confirmación
        if self.stack.currentIndex() == 2 and self.exam_s._engine is not None:
            msg = QMessageBox(self)
            msg.setWindowTitle("Salir del examen")
            msg.setText(
                "Estás en medio de un examen.\n\n¿Seguro que quieres salir? Perderás todo el progreso."
            )
            btn_stay = msg.addButton("Continuar examen", QMessageBox.ButtonRole.RejectRole)
            btn_exit = msg.addButton("Salir",            QMessageBox.ButtonRole.DestructiveRole)
            msg.setDefaultButton(btn_stay)
            msg.exec()
            if msg.clickedButton() == btn_stay:
                event.ignore()
                return
        event.accept()


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    icon_path = _script_dir() / "resources" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    app.setApplicationName("Exam Simulator")
    app.setApplicationVersion(APP_VERSION)
    app.setStyleSheet(QSS)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
