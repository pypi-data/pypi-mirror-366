import sys
import ctypes

# Global flag to track if DPI awareness is enabled
_dpi_enabled = False

def dpi(root=None):
    """
    Enable DPI awareness for Windows applications.
    
    If root is provided, also enables DPI-aware geometry for the window.
    This function should be called before creating any Tkinter windows
    to ensure proper scaling on high-DPI displays.
    
    Args:
        root: Optional Tkinter root window for DPI-aware geometry
    """
    if not sys.platform.startswith("win"):
        return False
    
    try:
        # Set DPI awareness to system DPI aware
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        global _dpi_enabled
        _dpi_enabled = True
        
        # If root is provided, enable DPI-aware geometry
        if root is not None:
            enable_dpi_geometry(root)
        
        return True
    except Exception:
        return False

def adjust_window_size(root, base_width, base_height, scale_factor=1.5, max_scale=2.0):
    """
    Adjust window size based on DPI scaling factor.
    
    Args:
        root: Tkinter root window
        base_width (int): Base window width
        base_height (int): Base window height
        scale_factor (float): Additional scaling factor (default: 0.75)
        max_scale (float): Maximum scaling factor (default: 1.5)
        
    Returns:
        tuple: (adjusted_width, adjusted_height)
    """
    if not sys.platform.startswith("win") or not _dpi_enabled:
        return base_width, base_height
    
    try:
        scaling = get_scaling_factor(root)
        if scaling > 1.0:
            # Apply DPI scaling with additional scale factor and max limit
            adjusted_scale = min(scaling * scale_factor, max_scale)
            adjusted_width = int(base_width * adjusted_scale)
            adjusted_height = int(base_height * adjusted_scale)
            return adjusted_width, adjusted_height
    except Exception:
        pass
    
    return base_width, base_height

def dpi_with_window_size(root, base_width, base_height, scale_factor=1.5, max_scale=2.0):
    """
    Enable DPI awareness and adjust window size in one call.
    
    Args:
        root: Tkinter root window
        base_width (int): Base window width
        base_height (int): Base window height
        scale_factor (float): Additional scaling factor (default: 0.75)
        max_scale (float): Maximum scaling factor (default: 1.5)
        
    Returns:
        tuple: (adjusted_width, adjusted_height)
    """
    # Enable DPI awareness
    dpi_enabled = dpi()
    
    # Adjust window size
    adjusted_width, adjusted_height = adjust_window_size(root, base_width, base_height, scale_factor, max_scale)
    
    # Set window geometry
    root.geometry(f"{adjusted_width}x{adjusted_height}")
    
    return adjusted_width, adjusted_height

def enable_dpi_geometry(root):
    """
    Enable DPI-aware geometry for a Tkinter root window.
    This patches the geometry method to automatically apply DPI scaling.
    
    Args:
        root: Tkinter root window
    """
    if not sys.platform.startswith("win"):
        return
    
    # Enable DPI awareness
    dpi()
    
    # Adjust Tkinter scaling for UI elements
    try:
        scaling = get_scaling_factor(root)
        if scaling > 1.0:
            # Apply higher scaling for UI elements
            ui_scale = min(scaling * 2.0, 2.5)  # Scale UI elements more aggressively
            root.tk.call('tk', 'scaling', ui_scale)
    except Exception:
        pass
    
    # Store original geometry method
    original_geometry = root.geometry
    
    def dpi_geometry(geometry_string=None):
        if geometry_string is None:
            return original_geometry()
        
        # Parse geometry string (e.g., "600x600" or "600x600+100+100")
        if 'x' in geometry_string:
            # Extract size part
            size_part = geometry_string.split('+')[0]
            if 'x' in size_part:
                width_str, height_str = size_part.split('x')
                try:
                    base_width = int(width_str)
                    base_height = int(height_str)
                    
                    # Apply DPI scaling
                    adjusted_width, adjusted_height = adjust_window_size(
                        root, base_width, base_height
                    )
                    
                    # Reconstruct geometry string with adjusted size
                    if '+' in geometry_string:
                        position_part = geometry_string.split('+', 1)[1]
                        adjusted_geometry = f"{adjusted_width}x{adjusted_height}+{position_part}"
                    else:
                        adjusted_geometry = f"{adjusted_width}x{adjusted_height}"
                    
                    return original_geometry(adjusted_geometry)
                except ValueError:
                    # If parsing fails, use original geometry
                    return original_geometry(geometry_string)
        
        # For non-size geometry strings, use original method
        return original_geometry(geometry_string)
    
    # Replace the geometry method
    root.geometry = dpi_geometry

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

def calculate_dpi_sizes(base_sizes, root, max_scale=2.5):
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

 