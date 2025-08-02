"""
Main logic for paste2file: paste clipboard content to a file via CLI or GUI.
"""

import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import Menu, messagebox, simpledialog
import threading
import time
from datetime import datetime
try:
    import pyperclip
except ImportError:
    pyperclip = None
try:
    from PIL import ImageGrab, Image
except ImportError:
    ImageGrab = None
try:
    import keyboard
except ImportError:
    keyboard = None

from loguru import logger

def get_desktop_path() -> Path:
    """Return the user's Desktop path."""
    return Path(os.path.join(os.path.expanduser("~"), "Desktop"))

def get_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")

def get_default_filename(suffix: str = "txt", user_input: str = "") -> str:
    """Generate a default filename based on timestamp and optional user input."""
    base = get_timestamp()
    if user_input:
        # Replace spaces and whitespace with underscores
        clean_input = user_input.replace(' ', '_').replace('\t', '_').replace('\n', '_').replace('\r', '_')
        # Remove any other problematic characters for filenames
        clean_input = ''.join(c for c in clean_input if c.isalnum() or c in '_-.')
        base = f"{base}_{clean_input}"
    return f"{base}.{suffix}"

def clipboard_content_type() -> str:
    """Detect clipboard content type: 'text', 'image', or 'unknown'."""
    # Try image first
    if ImageGrab:
        try:
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                return 'image'
        except Exception:
            pass
    # Fallback to text
    if pyperclip:
        try:
            text = pyperclip.paste()
            if isinstance(text, str) and text.strip():
                return 'text'
        except Exception:
            pass
    return 'unknown'

def save_clipboard_to_file(filepath: Path) -> str:
    """Save clipboard content to file. Returns file type or raises."""
    ctype = clipboard_content_type()
    if ctype == 'text':
        content = pyperclip.paste()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Clipboard text saved to {filepath}")
        return 'text'
    elif ctype == 'image':
        img = ImageGrab.grabclipboard()
        # Save as PNG to preserve transparency and quality
        img.save(filepath, 'PNG')
        logger.info(f"Clipboard image saved to {filepath}")
        return 'image'
    else:
        raise ValueError("Clipboard does not contain text or image data.")



class Paste2FileApp:
    """Tkinter GUI for paste2file."""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("paste2file")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.85)
        self.root.geometry("260x40+100+100")
        self.label = tk.Label(self.root, text="paste2file", font=("Arial", 14), bg="#27ae60", fg="#fff")
        self.label.pack(fill=tk.BOTH, expand=True)
        self.label.bind("<Button-3>", self.show_menu)
        self.menu = Menu(self.root, tearoff=0)
        self.menu.add_command(label="Exit", command=self.exit_app)
        # Start global hotkey listener
        self.setup_global_hotkey()
        # Make window draggable
        self._drag_data = {'x': 0, 'y': 0}
        self.label.bind('<ButtonPress-1>', self.start_move)
        self.label.bind('<B1-Motion>', self.do_move)

    def setup_global_hotkey(self):
        """Setup global hotkey listener for Ctrl+Shift+V"""
        if keyboard is None:
            logger.warning("keyboard library not available, global hotkey disabled")
            return
        
        def on_hotkey():
            # Schedule in main thread
            self.root.after(0, self.on_ctrl_shift_v)
        
        # Register the hotkey combination using keyboard library
        try:
            keyboard.add_hotkey('ctrl+shift+v', on_hotkey)
            logger.info("Global hotkey Ctrl+Shift+V registered")
        except Exception as e:
            logger.error(f"Failed to setup global hotkey: {e}")

    def exit_app(self):
        """Clean exit including stopping hotkey listener"""
        try:
            if keyboard is not None:
                keyboard.unhook_all()
        except Exception:
            pass
        self.root.quit()

    def show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def on_ctrl_shift_v(self):
        """Handle Ctrl+Shift+V hotkey - can be called from any thread"""
        # Create a custom dialog that's properly centered and topmost
        self.root.attributes('-topmost', True)
        self.root.focus_force()
        
        # Custom dialog for filename input
        dialog = tk.Toplevel(self.root)
        dialog.title("Save Clipboard")
        dialog.attributes('-topmost', True)
        dialog.resizable(False, False)
        dialog.grab_set()  # Make it modal
        
        # Center the dialog on screen
        dialog.geometry("400x120")
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (120 // 2)
        dialog.geometry(f"400x120+{x}+{y}")
        
        # Dialog content
        tk.Label(dialog, text="Optional file name (no extension):", font=("Arial", 10)).pack(pady=10)
        
        entry = tk.Entry(dialog, font=("Arial", 10), width=40)
        entry.pack(pady=5)
        
        # Force focus and bring to front
        dialog.focus_force()
        dialog.lift()
        entry.focus_set()
        entry.focus_force()
        
        result = {'value': None}
        
        def on_ok():
            result['value'] = entry.get()
            dialog.destroy()
            
        def on_cancel():
            result['value'] = None
            dialog.destroy()
            
        def on_enter(event):
            on_ok()
            
        entry.bind('<Return>', on_enter)
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        dialog.wait_window()
        
        user_input = result['value']
        if user_input is None:
            return
        user_input = user_input.strip()
        
        ctype = clipboard_content_type()
        if ctype == 'text':
            suffix = 'txt'
        elif ctype == 'image':
            suffix = 'png'
        else:
            messagebox.showerror("Error", "Clipboard does not contain text or image data.")
            return
            
        # For images, ask for memo text
        memo_text = ""
        if ctype == 'image':
            memo_text = self.get_memo_text()
            
        filename = get_default_filename(suffix, user_input)
        dest = get_desktop_path() / filename
        try:
            if ctype == 'image' and memo_text:
                self.save_image_with_memo(dest, memo_text)
            else:
                save_clipboard_to_file(dest)
            messagebox.showinfo("Saved", f"Clipboard {ctype} saved to {dest}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_memo_text(self):
        """Get memo text for image with custom centered dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Memo to Image")
        dialog.attributes('-topmost', True)
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # Center the dialog on screen
        dialog.geometry("500x200")
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"500x200+{x}+{y}")
        
        tk.Label(dialog, text="Enter memo text (optional):", font=("Arial", 10)).pack(pady=10)
        
        text_widget = tk.Text(dialog, font=("Arial", 10), width=60, height=6, wrap=tk.WORD)
        text_widget.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        
        # Force focus and bring to front
        dialog.focus_force()
        dialog.lift()
        text_widget.focus_set()
        text_widget.focus_force()
        
        result = {'value': ''}
        
        def on_ok():
            result['value'] = text_widget.get(1.0, tk.END).strip()
            dialog.destroy()
            
        def on_cancel():
            result['value'] = ''
            dialog.destroy()
            
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Skip", command=on_cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        dialog.wait_window()
        return result['value']

    def save_image_with_memo(self, filepath: Path, memo_text: str):
        """Save image with memo text appended at bottom"""
        from PIL import ImageDraw, ImageFont
        
        img = ImageGrab.grabclipboard()
        if not isinstance(img, Image.Image):
            raise ValueError("No image in clipboard")
            
        # Calculate memo area size
        if memo_text:
            # Try to use fonts that support Unicode/Chinese characters
            font = None
            font_paths = [
                # Windows fonts that support Chinese
                "C:/Windows/Fonts/msyh.ttc",      # Microsoft YaHei
                "C:/Windows/Fonts/simsun.ttc",    # SimSun
                "C:/Windows/Fonts/simhei.ttf",    # SimHei
                "C:/Windows/Fonts/arial.ttf",     # Arial Unicode MS
                "C:/Windows/Fonts/calibri.ttf",   # Calibri
                # Fallback to system default
                None
            ]
            
            for font_path in font_paths:
                try:
                    if font_path is None:
                        font = ImageFont.load_default()
                        break
                    else:
                        font = ImageFont.truetype(font_path, 16)
                        # Test if font can render Chinese characters
                        test_img = Image.new('RGB', (100, 30))
                        test_draw = ImageDraw.Draw(test_img)
                        test_draw.text((0, 0), "测试中文", font=font, fill=(0, 0, 0))
                        break
                except (OSError, IOError):
                    continue
            
            if font is None:
                font = ImageFont.load_default()
            
            # Calculate text dimensions
            temp_img = Image.new('RGB', (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            
            # Word wrap the text
            words = memo_text.split()
            lines = []
            current_line = ""
            max_width = img.width - 20  # 10px margin on each side
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                bbox = temp_draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                        current_line = word
                    else:
                        lines.append(word)
            if current_line:
                lines.append(current_line)
            
            # Calculate total memo area height
            line_height = temp_draw.textbbox((0, 0), "Ay", font=font)[3] + 4
            memo_height = len(lines) * line_height + 20  # 10px margin top/bottom
            
            # Create new image with memo area
            new_img = Image.new('RGB', (img.width, img.height + memo_height), (255, 255, 255))
            new_img.paste(img, (0, 0))
            
            # Draw memo text
            draw = ImageDraw.Draw(new_img)
            y_offset = img.height + 10
            for line in lines:
                # Calculate text width for center alignment
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x_centered = (img.width - text_width) // 2
                draw.text((x_centered, y_offset), line, fill=(255, 0, 0), font=font)  # Red color
                y_offset += line_height
            
            img = new_img
        
        # Save the image
        img.save(filepath, 'PNG')
        logger.info(f"Clipboard image with memo saved to {filepath}")

    def start_move(self, event):
        self._drag_data['x'] = event.x
        self._drag_data['y'] = event.y

    def do_move(self, event):
        x = self.root.winfo_x() + event.x - self._drag_data['x']
        y = self.root.winfo_y() + event.y - self._drag_data['y']
        self.root.geometry(f"+{x}+{y}")

    def run(self):
        self.root.mainloop()

def main():
    """Entry point for python -m paste2file or CLI."""
    app = Paste2FileApp()
    app.run()

# For python -m paste2file
if __name__ == "__main__":
    main()