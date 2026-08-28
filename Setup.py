# -*- coding: utf-8 -*-
"""
Church Media Master - Standalone Windows GUI Installer
Installs to %LocalAppData%\Programs\ChurchPlayer & Creates Desktop/StartMenu Shortcuts.
"""

import os
import sys
import zipfile
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import threading

APP_NAME = "Church Media Master"
APP_EXE = "ChurchPlayer.exe"
DEFAULT_INSTALL_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Programs", "ChurchPlayer")

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)

def create_shortcut(target_path, shortcut_path, icon_path, working_dir):
    vbs_script = f"""
    Set oWS = WScript.CreateObject("WScript.Shell")
    sLinkFile = "{shortcut_path}"
    Set oLink = oWS.CreateShortcut(sLinkFile)
    oLink.TargetPath = "{target_path}"
    oLink.WorkingDirectory = "{working_dir}"
    oLink.IconLocation = "{icon_path},0"
    oLink.Save
    """
    vbs_file = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "create_shortcut.vbs")
    with open(vbs_file, "w", encoding="cp949") as f:
        f.write(vbs_script)
    subprocess.run(["cscript", "//nologo", vbs_file], check=False)
    if os.path.exists(vbs_file):
        try: os.remove(vbs_file)
        except Exception: pass

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} 설치 마법사")
        self.root.geometry("520x360")
        self.root.resizable(False, False)
        self.root.configure(bg="#0d111a")

        # Center window
        self.root.eval('tk::PlaceWindow . center')

        self.install_dir_var = tk.StringVar(value=DEFAULT_INSTALL_DIR)
        self.create_desktop_var = tk.BooleanVar(value=True)
        self.create_startmenu_var = tk.BooleanVar(value=True)
        self.run_after_var = tk.BooleanVar(value=True)

        self.setup_ui()

    def setup_ui(self):
        # Header banner
        header = tk.Frame(self.root, bg="#161f30", height=70)
        header.pack(fill="x", side="top")
        
        lbl_title = tk.Label(header, text="✝️  Church Media Master Pro v2.0.0", font=("Segoe UI", 13, "bold"), fg="#ffffff", bg="#161f30")
        lbl_title.pack(anchor="w", padx=20, pady=(12, 2))
        
        lbl_sub = tk.Label(header, text="교회 스마트 예배 & 미디어 방송 통합 플레이어 설치", font=("Segoe UI", 9), fg="#94a3b8", bg="#161f30")
        lbl_sub.pack(anchor="w", padx=20)

        # Body frame
        body = tk.Frame(self.root, bg="#0d111a")
        body.pack(fill="both", expand=True, padx=24, pady=16)

        # Directory label & entry
        lbl_dir = tk.Label(body, text="설치 경로:", font=("Segoe UI", 9, "bold"), fg="#cbd5e1", bg="#0d111a")
        lbl_dir.pack(anchor="w", pady=(0, 4))

        ent_dir = tk.Entry(body, textvariable=self.install_dir_var, font=("Segoe UI", 9), bg="#1e293b", fg="#ffffff", insertbackground="white", relief="flat")
        ent_dir.pack(fill="x", ipady=4, pady=(0, 12))

        # Checkboxes
        chk_desktop = tk.Checkbutton(body, text="바탕화면에 바로가기 아이콘 생성", variable=self.create_desktop_var, font=("Segoe UI", 9), fg="#e2e8f0", bg="#0d111a", selectcolor="#1e293b", activebackground="#0d111a", activeforeground="#ffffff")
        chk_desktop.pack(anchor="w", pady=2)

        chk_start = tk.Checkbutton(body, text="시작 메뉴에 프로그램 등록", variable=self.create_startmenu_var, font=("Segoe UI", 9), fg="#e2e8f0", bg="#0d111a", selectcolor="#1e293b", activebackground="#0d111a", activeforeground="#ffffff")
        chk_start.pack(anchor="w", pady=2)

        chk_run = tk.Checkbutton(body, text="설치 완료 후 프로그램 바로 실행", variable=self.run_after_var, font=("Segoe UI", 9), fg="#e2e8f0", bg="#0d111a", selectcolor="#1e293b", activebackground="#0d111a", activeforeground="#ffffff")
        chk_run.pack(anchor="w", pady=2)

        # Progress bar
        self.progress = ttk.Progressbar(body, mode="determinate")
        self.progress.pack(fill="x", pady=(14, 4))

        self.lbl_status = tk.Label(body, text="설치 준비 완료. [설치 시작] 버튼을 눌러주세요.", font=("Segoe UI", 9), fg="#64748b", bg="#0d111a")
        self.lbl_status.pack(anchor="w")

        # Bottom buttons
        footer = tk.Frame(self.root, bg="#0d111a")
        footer.pack(fill="x", side="bottom", padx=24, pady=(0, 16))

        self.btn_install = tk.Button(footer, text="🚀 설치 시작", command=self.start_installation, font=("Segoe UI", 10, "bold"), bg="#2563eb", fg="#ffffff", activebackground="#1d4ed8", activeforeground="#ffffff", relief="flat", padx=16, pady=6, cursor="hand2")
        self.btn_install.pack(side="right")

        btn_cancel = tk.Button(footer, text="취소", command=self.root.destroy, font=("Segoe UI", 9), bg="#334155", fg="#cbd5e1", relief="flat", padx=12, pady=6, cursor="hand2")
        btn_cancel.pack(side="right", padx=8)

    def start_installation(self):
        self.btn_install.config(state="disabled", text="설치 중...")
        threading.Thread(target=self.run_install_thread, daemon=True).start()

    def run_install_thread(self):
        try:
            target_dir = self.install_dir_var.get()
            os.makedirs(target_dir, exist_ok=True)

            zip_src = get_resource_path("bundle.zip")
            if not os.path.exists(zip_src):
                zip_src = get_resource_path("ChurchPlayer_v2.0.0.zip")

            self.lbl_status.config(text="프로그램 파일 복사 중...")
            with zipfile.ZipFile(zip_src, "r") as z:
                total_files = len(z.infolist())
                for i, file_info in enumerate(z.infolist()):
                    z.extract(file_info, target_dir)
                    prog = int(((i + 1) / total_files) * 80)
                    self.progress["value"] = prog
                    self.root.update_idletasks()

            self.lbl_status.config(text="바로가기 아이콘 생성 중...")
            exe_path = os.path.join(target_dir, APP_EXE)
            icon_path = os.path.join(target_dir, "app_icon.ico")
            if not os.path.exists(icon_path):
                icon_path = exe_path

            # Desktop Shortcut
            if self.create_desktop_var.get():
                desktop = os.path.join(os.environ.get("USERPROFILE", "C:\\"), "Desktop")
                sc_path = os.path.join(desktop, f"{APP_NAME}.lnk")
                create_shortcut(exe_path, sc_path, icon_path, target_dir)

            # Start Menu Shortcut
            if self.create_startmenu_var.get():
                start_menu = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs")
                sc_path = os.path.join(start_menu, f"{APP_NAME}.lnk")
                create_shortcut(exe_path, sc_path, icon_path, target_dir)

            self.progress["value"] = 100
            self.lbl_status.config(text="🎉 설치가 성공적으로 완료되었습니다!", fg="#38bdf8")

            # Launch app if checked
            if self.run_after_var.get():
                subprocess.Popen([exe_path], cwd=target_dir)

            messagebox.showinfo("설치 완료", f"{APP_NAME} 설치가 완료되었습니다!\n바탕화면에서 바로 실행하실 수 있습니다.")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("설치 오류", f"설치 중 오류가 발생했습니다:\n{str(e)}")
            self.btn_install.config(state="normal", text="설치 재시도")

if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()
