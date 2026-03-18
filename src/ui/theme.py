"""Shared visual theme tokens for the Qt desktop UI."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QApplication


@dataclass(frozen=True)
class ThemeTokens:
    bg_canvas: str = "#e8e2d7"
    bg_surface: str = "#f1ece3"
    bg_panel: str = "#fffcf7"
    bg_panel_alt: str = "#f6efe5"
    bg_panel_strong: str = "#fffdf9"
    bg_highlight: str = "#d6e1e4"
    line_soft: str = "#d8d0c3"
    line_strong: str = "#b8aea1"
    text_main: str = "#22313a"
    text_soft: str = "#5f6d74"
    text_muted: str = "#78858b"
    accent: str = "#2f6477"
    accent_strong: str = "#214857"
    accent_soft: str = "#d8e7ec"
    warning: str = "#a56b22"
    warning_soft: str = "#f3e2cd"
    danger: str = "#a1483f"
    danger_soft: str = "#f1ddd9"
    success: str = "#2f6e4d"
    success_soft: str = "#dcece2"
    radius_sm: int = 8
    radius_md: int = 12
    radius_lg: int = 18
    spacing_xs: int = 6
    spacing_sm: int = 10
    spacing_md: int = 14
    spacing_lg: int = 18


TOKENS = ThemeTokens()


def alpha_hex(color: str, alpha: float) -> str:
    """Return a CSS rgba() string from a hex color and alpha ratio."""
    qcolor = QColor(color)
    return f"rgba({qcolor.red()}, {qcolor.green()}, {qcolor.blue()}, {alpha:.3f})"


def app_font(point_size: int = 10) -> QFont:
    font = QFont()
    font.setFamilies(["IBM Plex Sans", "Noto Sans SC", "Segoe UI", "Arial"])
    font.setPointSize(point_size)
    return font


def mono_font(point_size: int = 9) -> QFont:
    font = QFont()
    font.setFamilies(["IBM Plex Mono", "Cascadia Mono", "Consolas", "Courier New"])
    font.setPointSize(point_size)
    return font


def apply_theme(app: QApplication) -> None:
    """Apply the shared application font and stylesheet."""
    from src.ui.theme_qss import build_stylesheet

    app.setFont(app_font())
    app.setStyleSheet(build_stylesheet())
