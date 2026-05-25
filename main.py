import tkinter as tk
from tkinter import ttk
from gui_artifact import ArtifactCalculatorTab
from gui_stone import StoneCalculatorTab

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("종합 스펙업 계산기 (유물 / 스톤)")
        self.root.geometry("880x850")
        self.root.resizable(True, True)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # ⭐ [신설] 탭 변경 이벤트 바인딩
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.frame_artifact = tk.Frame(self.notebook, bg="#F8F9FA")
        self.notebook.add(self.frame_artifact, text=" 💎 고급 유물 계산기 ")
        self.app_artifact = ArtifactCalculatorTab(self.frame_artifact, self.root)

        self.frame_stone = tk.Frame(self.notebook, bg="#E9ECEF")
        self.notebook.add(self.frame_stone, text=" 🪨 스톤 계산기 ")
        self.app_stone = StoneCalculatorTab(self.frame_stone, self.root)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ⭐ [핵심] 탭이 바뀔 때 포커스를 root(윈도우 전체)로 강제 이동
    def on_tab_changed(self, event):
        self.root.focus_set()

    def on_closing(self):
        try:
            self.root.focus_set()
            self.app_artifact.save_current_data()
            self.app_stone.save_current_data()
        except Exception as e:
            print(f"자동 저장 중 오류 발생: {e}")
        finally:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()