"""
Windows-specific features for tkface.

This module provides Windows-specific enhancements for Tkinter applications.
All functions in this module are designed to work on Windows platforms and
will gracefully degrade or do nothing on other platforms.

Available features:
- DPI awareness and scaling
- Windows-specific button styling (flat buttons)
- Windows system sounds
- Windows 11 corner rounding control
"""

from .dpi import dpi, get_scaling_factor, calculate_dpi_sizes, scale_icon, adjust_window_size, dpi_with_window_size, enable_dpi_geometry
from .button import configure_button_for_windows, get_button_label_with_shortcut, FlatButton, create_flat_button
from .unround import unround
from .bell import bell

__all__ = [
    'dpi', 'get_scaling_factor', 'calculate_dpi_sizes', 'scale_icon', 
    'adjust_window_size', 'dpi_with_window_size', 'enable_dpi_geometry',
    'configure_button_for_windows', 'get_button_label_with_shortcut', 
    'FlatButton', 'create_flat_button',
    'unround', 'bell'
]