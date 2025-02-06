import os
import sys
import psutil
import win32gui
from PIL import Image
import win32con
import win32api
import win32ui

def resource_path(relative_path):
    """
    Returns an absolute path to a resource.
    If the application is compiled (frozen), the base path is the directory of the executable.
    Otherwise, it uses the current working directory.
    """
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    resolved = os.path.join(base_path, relative_path)
    print(f"[resource_path] Resolved '{relative_path}' to '{resolved}'")
    return resolved

def download_process_icon(process_name):
    """
    Downloads the icon of the given process (e.g. 'chrome.exe') and saves it into the bundled icons folder.
    If no icon is found in the process executable, a fallback default icon is used (if available).
    All resource paths (both input and output) are wrapped via resource_path.
    Returns:
        The absolute path to the saved icon.
    Raises:
        Exception: If neither an icon from the executable nor a default icon is available.
    """
    print(f"[download_process_icon] Starting icon download for process: {process_name}")
    
    hdc = None
    mem_dc = None
    save_dc = None
    bitmap = None

    try:
        # Determine the icons directory via resource_path.
        icons_dir = resource_path("icons")
        print(f"[download_process_icon] Icons directory resolved to: {icons_dir}")
        if not os.path.exists(icons_dir):
            print(f"[download_process_icon] Icons directory does not exist. Creating it.")
            os.makedirs(icons_dir)
        else:
            print(f"[download_process_icon] Icons directory exists.")

        # Find the process and get its executable path.
        exe_path = None
        print("[download_process_icon] Searching for process...")
        for proc in psutil.process_iter(['name', 'exe']):
            proc_name = proc.info['name']
            if proc_name and proc_name.lower() == process_name.lower():
                exe_path = proc.info['exe']
                print(f"[download_process_icon] Found process '{proc_name}' with exe path: {exe_path}")
                break
        if not exe_path:
            raise Exception(f"Process {process_name} not found")

        # Get standard icon dimensions.
        ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
        ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
        print(f"[download_process_icon] Icon dimensions: {ico_x}x{ico_y}")

        # Extract icons from the executable.
        print(f"[download_process_icon] Attempting to extract icons from: {exe_path}")
        icons = win32gui.ExtractIconEx(exe_path, 0)
        large_icons = icons[0]
        small_icons = icons[1]
        print(f"[download_process_icon] Number of large icons: {len(large_icons)}")
        print(f"[download_process_icon] Number of small icons: {len(small_icons)}")

        if large_icons and len(large_icons) > 0:
            large_icon = large_icons[0]
            print("[download_process_icon] Using large icon.")
        elif small_icons and len(small_icons) > 0:
            large_icon = small_icons[0]
            print("[download_process_icon] Large icon not available; using small icon.")
        else:
            # Fallback: load the default icon via resource_path.
            default_icon_path = resource_path(os.path.join("icons", "default_icon.png"))
            print(f"[download_process_icon] No icons found in executable. Attempting to use default icon at: {default_icon_path}")
            if os.path.exists(default_icon_path):
                print("[download_process_icon] Default icon found.")
                return default_icon_path
            else:
                raise Exception("No icons found in the executable and no default icon available.")

        # Create device contexts and a bitmap.
        print("[download_process_icon] Creating device contexts and bitmap.")
        hdc = win32gui.GetDC(0)
        mem_dc = win32ui.CreateDCFromHandle(hdc)
        save_dc = mem_dc.CreateCompatibleDC()
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mem_dc, ico_x, ico_y)

        # Select the bitmap into the device context.
        save_dc.SelectObject(bitmap)

        # Draw the icon onto the bitmap.
        print("[download_process_icon] Drawing icon onto bitmap.")
        save_dc.DrawIcon((0, 0), large_icon)

        # Convert the bitmap to a PIL Image.
        print("[download_process_icon] Converting bitmap to PIL image.")
        bmpstr = bitmap.GetBitmapBits(True)
        img = Image.frombuffer('RGBA', (ico_x, ico_y), bmpstr, 'raw', 'BGRA', 0, 1)

        # Save the icon using resource_path for the output file.
        output_filename = f"{process_name}_icon.png"
        output_path = resource_path(os.path.join("icons", output_filename))
        print(f"[download_process_icon] Saving icon to: {output_path}")
        img.save(output_path, 'PNG')

        # Clean up the extracted icon handle.
        win32gui.DestroyIcon(large_icon)
        print("[download_process_icon] Icon download successful.")

        return os.path.abspath(output_path)

    except Exception as e:
        print(f"[download_process_icon] Exception occurred: {e}")
        raise Exception(f"Error downloading icon: {str(e)}")
    finally:
        # Clean up all GDI resources.
        if save_dc is not None:
            save_dc.DeleteDC()
        if mem_dc is not None:
            mem_dc.DeleteDC()
        if bitmap is not None:
            win32gui.DeleteObject(bitmap.GetHandle())
        if hdc is not None:
            win32gui.ReleaseDC(0, hdc)
        print("[download_process_icon] Cleaned up GDI resources.")
