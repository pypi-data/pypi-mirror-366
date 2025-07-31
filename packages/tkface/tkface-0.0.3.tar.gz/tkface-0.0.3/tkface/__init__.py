from . import messagebox
from . import simpledialog
from . import lang
from . import win

# Export Windows-specific flat button as Button
from .win.button import FlatButton as Button

__version__ = "0.0.3"
__all__ = ["messagebox", "simpledialog", "lang", "win", "Button"] 