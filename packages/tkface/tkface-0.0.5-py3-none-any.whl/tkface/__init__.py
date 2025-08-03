from . import messagebox
from . import simpledialog
from . import lang
from . import win
from . import calendar

# Export Windows-specific flat button as Button
from .win.button import FlatButton as Button

# Export DPI functions for easy access
from .win.dpi import enable_dpi_geometry as dpi

__version__ = "0.0.5"
__all__ = ["messagebox", "simpledialog", "lang", "win", "calendar", "Button", "dpi"] 