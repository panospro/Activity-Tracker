import psutil
import win32gui
from PIL import Image
import win32con
import win32api
import win32ui
import os 

def download_process_icon(process_name):
    """
    Downloads the icon of a process given its name (e.g., 'chrome.exe')
    Saves it in the 'icons' folder and returns the full path to the saved icon
    """
    hdc = None
    mem_dc = None
    save_dc = None
    bitmap = None
    
    try:
        # Create icons directory if it doesn't exist
        icons_dir = "icons"
        if not os.path.exists(icons_dir):
            os.makedirs(icons_dir)
            
        # Find the process
        for proc in psutil.process_iter(['name', 'exe']):
            if proc.info['name'].lower() == process_name.lower():
                exe_path = proc.info['exe']
                break
        else:
            raise Exception(f"Process {process_name} not found")

        # Extract large icon
        ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
        ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
        
        large_icon = win32gui.ExtractIconEx(exe_path, 0)[0][0]
        
        # Create device contexts and bitmap
        hdc = win32gui.GetDC(0)
        mem_dc = win32ui.CreateDCFromHandle(hdc)
        save_dc = mem_dc.CreateCompatibleDC()
        
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mem_dc, ico_x, ico_y)
        
        # Select bitmap into device context
        save_dc.SelectObject(bitmap)
        
        # Draw icon onto bitmap
        save_dc.DrawIcon((0, 0), large_icon)
        
        # Convert bitmap to PIL Image
        bmpstr = bitmap.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGBA',
            (ico_x, ico_y),
            bmpstr, 'raw', 'BGRA', 0, 1
        )
        
        # Save the icon in the icons directory
        output_filename = f"{process_name}_icon.png"
        output_path = os.path.join(icons_dir, output_filename)
        img.save(output_path, 'PNG')
        
        # Get the absolute path
        abs_path = os.path.abspath(output_path)
        
        # Cleanup icon
        win32gui.DestroyIcon(large_icon)
        
        return abs_path
        
    except Exception as e:
        raise Exception(f"Error downloading icon: {str(e)}")
        
    finally:
        # Proper cleanup of GDI resources
        if save_dc is not None:
            save_dc.DeleteDC()
        if mem_dc is not None:
            mem_dc.DeleteDC()
        if bitmap is not None:
            win32gui.DeleteObject(bitmap.GetHandle())
        if hdc is not None:
            win32gui.ReleaseDC(0, hdc)
