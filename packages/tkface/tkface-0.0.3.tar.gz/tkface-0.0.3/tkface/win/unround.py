import sys

def unround(root):
    """
    Disable window corner rounding for all windows under the given Tk root (Windows 11 only).
    Does nothing on other OSes.
    """
    if not sys.platform.startswith("win"):
        return
    try:
        import ctypes
        from ctypes import wintypes

        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        DWMWCP_DONOTROUND = 1

        hwnds = set()
        # root window
        hwnds.add(root.winfo_id())
        # all Toplevel windows
        for w in root.winfo_children():
            if hasattr(w, 'winfo_id'):
                hwnds.add(w.winfo_id())

        for hwnd in hwnds:
            corner_pref = ctypes.c_int(DWMWCP_DONOTROUND)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                wintypes.HWND(hwnd),
                ctypes.c_uint(DWMWA_WINDOW_CORNER_PREFERENCE),
                ctypes.byref(corner_pref),
                ctypes.sizeof(corner_pref)
            )
    except Exception:
        pass 