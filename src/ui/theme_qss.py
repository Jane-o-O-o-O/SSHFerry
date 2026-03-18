"""Global Qt stylesheet for the desktop UI."""

from __future__ import annotations

from src.ui.theme import TOKENS, alpha_hex


def build_stylesheet() -> str:
    return f"""
QWidget {{
    color: {TOKENS.text_main};
    background: transparent;
    selection-background-color: {TOKENS.accent};
    selection-color: #f8fbfc;
}}

QMainWindow, QWidget#appRoot {{
    background-color: {TOKENS.bg_canvas};
}}

QMenuBar, QMenu, QStatusBar {{
    background-color: {TOKENS.bg_panel_alt};
    color: {TOKENS.text_main};
}}

QMenuBar {{
    border-bottom: 1px solid {TOKENS.line_soft};
}}

QMenu {{
    border: 1px solid {TOKENS.line_soft};
}}

QWidget#topBar {{
    background-color: {TOKENS.bg_panel_alt};
    border: 1px solid {TOKENS.line_soft};
    border-radius: {TOKENS.radius_lg}px;
}}

QFrame#panelCard, QFrame#sessionCard {{
    background-color: {TOKENS.bg_panel};
    border: 1px solid {TOKENS.line_soft};
    border-radius: {TOKENS.radius_lg}px;
}}

QFrame#sessionCard[active="true"] {{
    border: 2px solid {TOKENS.accent};
    background-color: {TOKENS.bg_panel_strong};
}}

QFrame#toolbarCard, QWidget#toolbarCard {{
    background-color: {TOKENS.bg_panel_alt};
    border: 1px solid {TOKENS.line_soft};
    border-radius: {TOKENS.radius_md}px;
}}

QLabel#titleLabel {{
    font-size: 18px;
    font-weight: 700;
    color: {TOKENS.text_main};
}}

QLabel#subtitleLabel, QLabel#mutedLabel {{
    color: {TOKENS.text_soft};
    font-size: 12px;
}}

QLabel#sectionTitle {{
    font-size: 14px;
    font-weight: 700;
    color: {TOKENS.text_main};
}}

QLabel#summaryLabel {{
    color: {TOKENS.text_soft};
}}

QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox {{
    background-color: {alpha_hex(TOKENS.bg_panel_strong, 0.96)};
    border: 1px solid {TOKENS.line_soft};
    border-radius: {TOKENS.radius_sm}px;
    padding: 8px 12px;
    min-height: 18px;
    color: {TOKENS.text_main};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
    border: 1px solid {TOKENS.accent};
}}

QPushButton {{
    background-color: {alpha_hex(TOKENS.bg_panel_strong, 0.9)};
    border: 1px solid {TOKENS.line_soft};
    border-radius: {TOKENS.radius_sm}px;
    padding: 8px 14px;
    min-height: 18px;
    color: {TOKENS.text_main};
}}

QPushButton:hover {{
    background-color: {TOKENS.bg_panel_alt};
    border-color: {TOKENS.line_strong};
}}

QPushButton:pressed {{
    background-color: {TOKENS.accent_soft};
}}

QPushButton[variant="primary"] {{
    background-color: {TOKENS.accent};
    border-color: {TOKENS.accent_strong};
    color: #f8fbfc;
}}

QPushButton[variant="danger"] {{
    background-color: {TOKENS.danger_soft};
    border-color: {alpha_hex(TOKENS.danger, 0.35)};
    color: {TOKENS.danger};
}}

QPushButton[variant="ghost"] {{
    background-color: {alpha_hex(TOKENS.bg_panel_strong, 0.55)};
}}

QPushButton[chrome="icon"] {{
    padding: 0;
    min-width: 34px;
    max-width: 34px;
    min-height: 34px;
    max-height: 34px;
    border-radius: {TOKENS.radius_sm}px;
    border: none;
    background-color: transparent;
}}

QPushButton[chrome="icon"]:hover {{
    background-color: {TOKENS.bg_panel_alt};
    border: 1px solid {TOKENS.line_soft};
}}

QPushButton[chrome="icon"]:pressed {{
    background-color: {TOKENS.accent_soft};
}}

QListWidget, QTreeView, QTreeWidget, QTableWidget, QTextEdit#logOutput {{
    background-color: {alpha_hex(TOKENS.bg_panel_strong, 0.96)};
    alternate-background-color: {TOKENS.bg_panel_alt};
    border: 1px solid {TOKENS.line_soft};
    border-radius: {TOKENS.radius_md}px;
    gridline-color: {TOKENS.line_soft};
}}

QListWidget::item, QTreeView::item, QTreeWidget::item, QTableWidget::item {{
    padding: 6px;
}}

QListWidget::item:selected, QTreeView::item:selected, QTreeWidget::item:selected, QTableWidget::item:selected {{
    background-color: {TOKENS.accent};
    color: #f8fbfc;
}}

QListWidget::item:hover, QTreeView::item:hover, QTreeWidget::item:hover, QTableWidget::item:hover {{
    background-color: {TOKENS.accent_soft};
}}

QHeaderView::section {{
    background-color: {TOKENS.bg_panel_alt};
    border: none;
    border-right: 1px solid {TOKENS.line_soft};
    border-bottom: 1px solid {TOKENS.line_soft};
    padding: 6px 8px;
    font-weight: 700;
    color: {TOKENS.text_soft};
}}

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 4px;
}}

QScrollBar::handle:vertical {{
    background: {alpha_hex(TOKENS.text_muted, 0.45)};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: transparent;
    border: none;
}}

QSplitter::handle {{
    background-color: {alpha_hex(TOKENS.text_muted, 0.18)};
    border-radius: 4px;
}}

QCheckBox {{
    spacing: 8px;
    color: {TOKENS.text_soft};
}}

QDialog {{
    background-color: {TOKENS.bg_surface};
}}

QGroupBox {{
    border: 1px solid {TOKENS.line_soft};
    border-radius: {TOKENS.radius_md}px;
    margin-top: 12px;
    padding: 16px 12px 12px 12px;
    font-weight: 700;
    background-color: {TOKENS.bg_panel};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
    color: {TOKENS.text_soft};
}}
"""
