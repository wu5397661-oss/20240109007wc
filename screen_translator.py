import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pyautogui
import requests
import threading
import os
import subprocess
import sys

def get_subprocess_startupinfo():
    """获取 subprocess 启动信息，用于隐藏子进程的窗口"""
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        return startupinfo
    return None

class ScreenTranslator:
    def __init__(self, root):
        self.root = root
        self.root.title("屏幕翻译工具")
        self.root.geometry("800x700")
        
        self.tesseract_exe = r"D:\CM\Tess\tesseract.exe"
        self.tessdata_dir = r"D:\CM\Tess\tessdata"
        
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "qwen2.5:7b-instruct-q4_K_M"
        
        self.selection_window = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.rect_id = None
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.capture_btn = ttk.Button(btn_frame, text="截取屏幕", command=self.start_selection)
        self.capture_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(btn_frame, text="状态: ").pack(side=tk.LEFT)
        self.status_label = ttk.Label(btn_frame, text="就绪")
        self.status_label.pack(side=tk.LEFT)
        
        ttk.Label(main_frame, text="截图预览:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.screenshot_label = ttk.Label(main_frame)
        self.screenshot_label.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(main_frame, text="原文:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        self.source_text = tk.Text(main_frame, height=8, wrap=tk.WORD)
        self.source_text.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        ttk.Label(main_frame, text="译文:").grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        self.target_text = tk.Text(main_frame, height=8, wrap=tk.WORD)
        self.target_text.grid(row=6, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        main_frame.rowconfigure(4, weight=1)
        main_frame.rowconfigure(6, weight=1)
    
    def start_selection(self):
        self.root.withdraw()
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.attributes("-fullscreen", True)
        self.selection_window.attributes("-alpha", 0.3)
        self.selection_window.configure(bg="black")
        self.selection_window.attributes("-topmost", True)
        
        self.canvas = tk.Canvas(self.selection_window, cursor="cross", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Escape>", self.cancel_selection)
    
    def on_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y
    
    def on_mouse_drag(self, event):
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline="red", width=2
        )
    
    def on_mouse_up(self, event):
        self.end_x = event.x
        self.end_y = event.y
        
        if self.selection_window:
            self.selection_window.destroy()
            self.selection_window = None
        
        self.root.deiconify()
        
        if self.start_x and self.start_y and self.end_x and self.end_y:
            x1 = min(self.start_x, self.end_x)
            y1 = min(self.start_y, self.end_y)
            x2 = max(self.start_x, self.end_x)
            y2 = max(self.start_y, self.end_y)
            
            if x2 > x1 and y2 > y1:
                self.capture_and_translate(x1, y1, x2, y2)
    
    def cancel_selection(self, event):
        if self.selection_window:
            self.selection_window.destroy()
            self.selection_window = None
        self.root.deiconify()
    
    def status(self, text):
        self.status_label.config(text=text)
        self.root.update()
    
    def capture_and_translate(self, x1, y1, x2, y2):
        def task():
            try:
                self.status("正在截图...")
                screenshot = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))
                
                img = ImageTk.PhotoImage(screenshot.resize((400, 300)))
                self.screenshot_label.config(image=img)
                self.screenshot_label.image = img
                
                self.status("正在识别文字...")
                temp_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_screenshot.png")
                screenshot.save(temp_image_path)
                
                cmd = [
                    self.tesseract_exe,
                    temp_image_path,
                    "stdout",
                    "-l", "eng",
                    "--tessdata-dir", self.tessdata_dir
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', startupinfo=get_subprocess_startupinfo())
                text = result.stdout
                
                os.remove(temp_image_path)
                
                self.source_text.delete(1.0, tk.END)
                self.source_text.insert(tk.END, text)
                
                if not text.strip():
                    self.status("未识别到文字")
                    return
                
                self.status("正在翻译...")
                translation = self.translate_with_ollama(text)
                
                self.target_text.delete(1.0, tk.END)
                self.target_text.insert(tk.END, translation)
                
                self.status("完成")
                
            except Exception as e:
                messagebox.showerror("错误", str(e))
                self.status("出错了")
        
        threading.Thread(target=task, daemon=True).start()
    
    def translate_with_ollama(self, text):
        prompt = f"请将以下英文翻译成中文：\n\n{text}"
        
        try:
            self.status("正在连接 Ollama...")
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )
            self.status("正在翻译...")
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.Timeout:
            return "翻译超时：模型推理时间过长，请尝试缩短识别的文字长度或更换更快的模型。"
        except requests.exceptions.ConnectionError:
            return "连接失败：无法连接到 Ollama，请确保 Ollama 服务正在运行！"
        except Exception as e:
            return f"翻译失败: {str(e)}\n请确保 Ollama 正在运行并且 qwen-translator 已安装"

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenTranslator(root)
    root.mainloop()
