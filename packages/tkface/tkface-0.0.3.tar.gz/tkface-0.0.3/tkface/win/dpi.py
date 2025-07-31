import sys
import ctypes

# Global flag to track if DPI awareness is enabled
_dpi_enabled = False

def dpi():
    """
    Enable DPI awareness for Windows applications.
    
    This function should be called before creating any Tkinter windows
    to ensure proper scaling on high-DPI displays.
    """
    if not sys.platform.startswith("win"):
        return False
    
    try:
        # Set DPI awareness to system DPI aware
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        global _dpi_enabled
        _dpi_enabled = True
        return True
    except Exception:
        return False

def get_scaling_factor(root):
    """
    Get DPI scaling factor for a Tkinter root window.
    
    Args:
        root: Tkinter root window
        
    Returns:
        float: Scaling factor (1.0 on non-Windows, actual scaling on Windows if DPI enabled)
    """
    if not sys.platform.startswith("win") or not _dpi_enabled:
        return 1.0
    
    try:
        return root.tk.call('tk', 'scaling')
    except Exception:
        return 1.0

def calculate_dpi_sizes(base_sizes, root, max_scale=1.5):
    """
    Calculate DPI-aware sizes for various UI elements.
    
    Args:
        base_sizes (dict): Dictionary of base sizes (e.g., {'padding': 20, 'width': 10})
        root: Tkinter root window
        max_scale (float): Maximum scaling factor (default: 1.5)
        
    Returns:
        dict: Scaled sizes
    """
    if not sys.platform.startswith("win") or not _dpi_enabled:
        return base_sizes
    
    try:
        scaling = get_scaling_factor(root)
        if scaling > 1.0:
            scale_factor = min(scaling, max_scale)
            return {key: int(value * scale_factor) for key, value in base_sizes.items()}
    except Exception:
        pass
    
    return base_sizes

def scale_icon(icon_name, parent, base_size=24, max_scale=3.0):
    """
    Create a scaled version of a Tkinter icon for DPI-aware sizing.
    
    Args:
        icon_name (str): Icon identifier (e.g., "error", "info")
        parent: Parent widget
        base_size (int): Base icon size
        max_scale (float): Maximum scaling factor
        
    Returns:
        str: Scaled icon name or original icon name if scaling fails
    """
    if not sys.platform.startswith("win") or not _dpi_enabled:
        return icon_name
    
    try:
        scaling = get_scaling_factor(parent)
        if scaling > 1.0:
            # Map icon names to actual Tkinter icon names
            icon_mapping = {
                "error": "::tk::icons::error",
                "info": "::tk::icons::information",
                "warning": "::tk::icons::warning",
                "question": "::tk::icons::question"
            }
            
            # Get the actual Tkinter icon name
            original_icon = icon_mapping.get(icon_name, f"::tk::icons::{icon_name}")
            scaled_icon = f"scaled_{icon_name}_large"
            
            # Get original icon dimensions
            original_width = parent.tk.call('image', 'width', original_icon)
            original_height = parent.tk.call('image', 'height', original_icon)
            
            # Calculate new dimensions
            # Only scale if DPI scaling is significantly higher than 1.0
            if scaling >= 1.25:  # Only scale for 125% DPI or higher
                scale_factor = min(scaling, max_scale)  # Cap at max_scale
            else:
                scale_factor = 1.0  # No scaling for 100% DPI
            
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
            # Create scaled image using Tcl's image scaling
            parent.tk.call('image', 'create', 'photo', scaled_icon)
            parent.tk.call(scaled_icon, 'copy', original_icon, 
                         '-zoom', int(scale_factor), int(scale_factor))
            
            return scaled_icon
    except Exception:
        pass
    
    return icon_name

 