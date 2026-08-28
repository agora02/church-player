# -*- coding: utf-8 -*-
"""
Church Media Master - Ultra Modern Glassmorphic Installer & Uninstaller
Powered by Edge WebView2 & Emil Kowalski Design Engineering
"""

import os
import sys
import zipfile
import subprocess
import threading
import time
import shutil
import webview

APP_NAME = "Church Media Master"
APP_EXE = "ChurchPlayer.exe"
DEFAULT_INSTALL_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Programs", "ChurchPlayer")

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    base_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    return os.path.join(base_dir, relative_path)

def get_real_desktop_path():
    try:
        res = subprocess.run(['powershell', '-NoProfile', '-Command', '[Environment]::GetFolderPath("Desktop")'], capture_output=True, text=True, encoding='utf-8', errors='replace')
        p = res.stdout.strip()
        if p and os.path.exists(p):
            return p
    except Exception:
        pass
    user = os.environ.get('USERPROFILE', '')
    for candidate in [os.path.join(user, '바탕 화면'), os.path.join(user, 'OneDrive', '바탕 화면'), os.path.join(user, 'OneDrive', 'Desktop'), os.path.join(user, 'Desktop')]:
        if os.path.exists(candidate):
            return candidate
    return os.path.join(user, 'Desktop')

def get_real_startmenu_path():
    try:
        res = subprocess.run(['powershell', '-NoProfile', '-Command', '[Environment]::GetFolderPath("Programs")'], capture_output=True, text=True, encoding='utf-8', errors='replace')
        p = res.stdout.strip()
        if p and os.path.exists(p):
            return p
    except Exception:
        pass
    return os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs')

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
    try:
        with open(vbs_file, "w", encoding="cp949", errors="replace") as f:
            f.write(vbs_script)
        subprocess.run(["cscript", "//nologo", vbs_file], check=False)
        if os.path.exists(vbs_file):
            os.remove(vbs_file)
    except Exception as e:
        print("Shortcut creation error:", e)

class InstallerAPI:
    def __init__(self):
        self.window = None

    def get_default_dir(self):
        return DEFAULT_INSTALL_DIR

    def check_installed(self, target_dir):
        check_dir = target_dir or DEFAULT_INSTALL_DIR
        exe = os.path.join(check_dir, APP_EXE)
        return os.path.exists(exe)

    def choose_folder(self):
        if not self.window:
            return ""
        result = self.window.create_file_dialog(webview.FOLDER_DIALOG)
        if result and len(result) > 0:
            folder = result[0]
            if not folder.endswith("ChurchPlayer"):
                folder = os.path.join(folder, "ChurchPlayer")
            return folder
        return ""

    def close(self):
        if self.window:
            self.window.destroy()

    def start_install(self, options):
        def worker():
            try:
                target_dir = options.get('install_dir') or DEFAULT_INSTALL_DIR
                create_desktop = options.get('create_desktop', True)
                create_startmenu = options.get('create_startmenu', True)
                run_after = options.get('run_after', True)

                # Terminate running app before overwrite/install
                subprocess.run(["taskkill", "/F", "/IM", APP_EXE], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(0.3)

                os.makedirs(target_dir, exist_ok=True)
                zip_src = get_resource_path("ChurchPlayer_v2.1.0.zip")
                if not os.path.exists(zip_src):
                    zip_src = get_resource_path("ChurchPlayer_v2.0.0.zip")

                self.window.evaluate_js("updateProgress(10, '프로그램 파일 압축 해제 중...')")
                time.sleep(0.3)

                with zipfile.ZipFile(zip_src, "r") as z:
                    file_list = z.infolist()
                    total = len(file_list)
                    for idx, finfo in enumerate(file_list):
                        z.extract(finfo, target_dir)
                        if idx % 10 == 0 or idx == total - 1:
                            pct = 10 + int((idx / total) * 70)
                            self.window.evaluate_js(f"updateProgress({pct}, '파일 복사 중 ({idx + 1}/{total})...')")

                self.window.evaluate_js("updateProgress(85, '바탕화면 및 시작 메뉴 바로가기 생성 중...')")
                exe_path = os.path.join(target_dir, APP_EXE)
                icon_path = os.path.join(target_dir, "app_icon.ico")
                if not os.path.exists(icon_path):
                    icon_path = exe_path

                # Real Desktop Shortcut
                if create_desktop:
                    desktop = get_real_desktop_path()
                    sc_path = os.path.join(desktop, f"{APP_NAME}.lnk")
                    create_shortcut(exe_path, sc_path, icon_path, target_dir)

                # Real Start Menu Shortcut
                if create_startmenu:
                    start_menu = get_real_startmenu_path()
                    os.makedirs(start_menu, exist_ok=True)
                    sc_path = os.path.join(start_menu, f"{APP_NAME}.lnk")
                    create_shortcut(exe_path, sc_path, icon_path, target_dir)

                self.window.evaluate_js("updateProgress(100, '🎉 설치 및 업데이트가 완료되었습니다!')")
                time.sleep(1.2)

                if run_after:
                    subprocess.Popen([exe_path], cwd=target_dir)

                self.window.destroy()
            except Exception as e:
                self.window.evaluate_js(f"updateProgress(0, '오류 발생: {str(e)}')")

        threading.Thread(target=worker, daemon=True).start()

    def start_uninstall(self, target_dir):
        def worker():
            try:
                dest_dir = target_dir or DEFAULT_INSTALL_DIR
                self.window.evaluate_js("updateProgress(20, '실행 중인 프로세스 종료 중...')")
                subprocess.run(["taskkill", "/F", "/IM", APP_EXE], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(0.5)

                self.window.evaluate_js("updateProgress(50, '바로가기 아이콘 제거 중...')")
                desktop = get_real_desktop_path()
                sc_desktop = os.path.join(desktop, f"{APP_NAME}.lnk")
                if os.path.exists(sc_desktop):
                    try: os.remove(sc_desktop)
                    except Exception: pass

                start_menu = get_real_startmenu_path()
                sc_start = os.path.join(start_menu, f"{APP_NAME}.lnk")
                if os.path.exists(sc_start):
                    try: os.remove(sc_start)
                    except Exception: pass

                self.window.evaluate_js("updateProgress(75, '프로그램 파일 삭제 중...')")
                if os.path.exists(dest_dir):
                    shutil.rmtree(dest_dir, ignore_errors=True)

                self.window.evaluate_js("updateProgress(100, '🗑️ 프로그램이 완전히 삭제되었습니다.')")
                time.sleep(1.5)
                self.window.destroy()
            except Exception as e:
                self.window.evaluate_js(f"updateProgress(0, '삭제 중 오류 발생: {str(e)}')")

        threading.Thread(target=worker, daemon=True).start()

def main():
    html_path = get_resource_path("installer.html")
    html_url = f"file:///{html_path.replace(os.sep, '/')}"

    api = InstallerAPI()
    win = webview.create_window(
        title="Church Media Master 설치 및 관리 마법사",
        url=html_url,
        js_api=api,
        width=550,
        height=470,
        resizable=False,
        background_color="#0b0d14"
    )
    api.window = win
    webview.start(debug=False)

if __name__ == '__main__':
    main()
