import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pyautogui
import requests
import threading
import io


SERVER_URL = "http://120.27.15.234:8000"


class ScreenTranslatorClient:
    def __init__(self, root):
        self.root = root
        self.root.title("屏幕翻译工具 - 客户端")
        self.root.geometry("800x750")

        self.server_url = SERVER_URL

        self.selection_window = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.rect_id = None

        self.setup_ui()
        self.check_server()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.capture_btn = ttk.Button(top_frame, text="截取屏幕", command=self.start_selection)
        self.capture_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(top_frame, text="服务器:").pack(side=tk.LEFT, padx=(10, 0))
        self.server_entry = ttk.Entry(top_frame, width=30)
        self.server_entry.insert(0, self.server_url)
        self.server_entry.pack(side=tk.LEFT, padx=(5, 10))

        ttk.Button(top_frame, text="测试连接", command=self.check_server).pack(side=tk.LEFT)

        ttk.Label(main_frame, text="状态: ").grid(row=1, column=0, sticky=tk.W, pady=(5, 5))
        self.status_label = ttk.Label(main_frame, text="就绪")
        self.status_label.grid(row=1, column=0, sticky=tk.W, padx=(50, 0), pady=(5, 5))

        ttk.Label(main_frame, text="截图预览:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.screenshot_label = ttk.Label(main_frame)
        self.screenshot_label.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(main_frame, text="原文 (OCR识别):").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.source_text = tk.Text(main_frame, height=8, wrap=tk.WORD)
        self.source_text.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        ttk.Label(main_frame, text="译文 (翻译结果):").grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        self.target_text = tk.Text(main_frame, height=8, wrap=tk.WORD)
        self.target_text.grid(row=7, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        main_frame.rowconfigure(5, weight=1)
        main_frame.rowconfigure(7, weight=1)

    def check_server(self):
        url = self.server_entry.get().strip().rstrip("/")
        if not url:
            return
        try:
            resp = requests.get(f"{url}/health", timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                status = []
                if data.get("tesseract"):
                    status.append("OCR✅")
                else:
                    status.append("OCR❌")
                status.append(f"模型:{data.get('model', '?')}")
                self.status_label.config(text="服务器连接正常 - " + " ".join(status))
            else:
                self.status_label.config(text=f"服务器异常 (状态码:{resp.status_code})")
        except Exception as e:
            self.status_label.config(text=f"无法连接服务器: {e}")

    def start_selection(self):
        self.server_url = self.server_entry.get().strip().rstrip("/")
        if not self.server_url:
            messagebox.showerror("错误", "请先填写服务器地址")
            return

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
                screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))

                img = ImageTk.PhotoImage(screenshot.resize((400, 300)))
                self.screenshot_label.config(image=img)
                self.screenshot_label.image = img

                self.status("正在上传到服务器识别+翻译...")

                img_bytes = io.BytesIO()
                screenshot.save(img_bytes, format="PNG")
                img_bytes.seek(0)

                resp = requests.post(
                    f"{self.server_url}/translate",
                    files={"file": ("screenshot.png", img_bytes, "image/png")},
                    timeout=180,
                )
                resp.raise_for_status()
                result = resp.json()

                self.source_text.delete(1.0, tk.END)
                self.source_text.insert(tk.END, result.get("source_text", ""))

                self.target_text.delete(1.0, tk.END)
                self.target_text.insert(tk.END, result.get("translation", ""))

                self.status("完成")

            except requests.exceptions.ConnectionError:
                messagebox.showerror("错误", f"无法连接到服务器 {self.server_url}\n请确保后端服务已启动。")
                self.status("连接失败")
            except requests.exceptions.Timeout:
                messagebox.showerror("错误", "请求超时，服务器处理时间过长")
                self.status("超时")
            except Exception as e:
                messagebox.showerror("错误", str(e))
                self.status("出错了")

        threading.Thread(target=task, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenTranslatorClient(root)
    root.mainloop()
