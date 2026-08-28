# -*- coding: utf-8 -*-
"""
Church Media Master - Native Windows Desktop Application
Crafted with Emil Kowalski Design Engineering, Frameless Custom Titlebar & Auto-Updater
"""

import os
import sys
import traceback
import threading
import urllib.request
import tempfile
import webview
import updater

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    base_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    return os.path.join(base_dir, relative_path)

class DesktopAppAPI:
    def __init__(self):
        self.main_window = None
        self.live_window = None

    def minimize_window(self):
        if self.main_window:
            self.main_window.minimize()

    def maximize_window(self):
        if self.main_window:
            # Toggle maximize/restore
            if hasattr(self.main_window, 'is_maximized') and self.main_window.is_maximized:
                self.main_window.restore()
                self.main_window.is_maximized = False
            else:
                self.main_window.maximize()
                self.main_window.is_maximized = True

    def close_window(self):
        if self.live_window:
            try: self.live_window.destroy()
            except Exception: pass
        if self.main_window:
            self.main_window.destroy()

    def get_version(self):
        return updater.get_current_version()

    def check_for_updates(self):
        return updater.check_update_sync()

    def download_and_install_update(self, download_url):
        if not download_url:
            return {'success': False, 'message': '다운로드 URL이 올바르지 않습니다.'}
        
        def run_update():
            try:
                temp_zip = os.path.join(tempfile.gettempdir(), 'ChurchPlayer_Latest.zip')
                urllib.request.urlretrieve(download_url, temp_zip)
                target_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
                updater.apply_update_script(temp_zip, target_dir)
            except Exception as e:
                print('Update error:', e)

        thread = threading.Thread(target=run_update, daemon=True)
        thread.start()
        return {'success': True, 'message': '업데이트 파일을 다운로드하는 중입니다...'}

    def get_screens(self):
        screens = webview.screens
        screen_list = []
        for idx, s in enumerate(screens):
            name = f"모니터 #{idx + 1} ({s.width}x{s.height})"
            if len(screens) > 1 and idx == 1:
                name += " [추천: 보조 모니터/프로젝터]"
            elif idx == 0:
                name += " [주 모니터]"
            
            screen_list.append({
                'index': idx,
                'name': name,
                'width': s.width,
                'height': s.height
            })
        return screen_list

    def open_file_dialog(self):
        if not self.main_window:
            return []
        file_types = ('Media Files (*.mp4;*.mkv;*.avi;*.mov;*.wmv;*.mp3;*.wav;*.flac;*.aac;*.m4a;*.ogg)', 'All files (*.*)')
        result = self.main_window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=True,
            file_types=file_types
        )
        return result or []

    def toggle_live_window(self, screen_index=1):
        if self.live_window:
            try:
                self.live_window.destroy()
            except Exception:
                pass
            self.live_window = None
            return False

        screens = webview.screens
        target_idx = int(screen_index)
        if target_idx < 0 or target_idx >= len(screens):
            target_idx = 1 if len(screens) > 1 else 0
            
        target_screen = screens[target_idx]
        
        live_path = get_resource_path('live.html')
        live_url = f'file:///{live_path.replace(os.sep, "/")}'
        
        self.live_window = webview.create_window(
            title='CHURCH LIVE DISPLAY',
            url=live_url,
            screen=target_screen,
            fullscreen=True,
            frameless=True,
            easy_drag=False,
            background_color='#000000'
        )
        return True

def main():
    index_path = get_resource_path('index.html')
    main_url = f'file:///{index_path.replace(os.sep, "/")}'

    api = DesktopAppAPI()

    main_win = webview.create_window(
        title='CHURCH MEDIA MASTER',
        url=main_url,
        js_api=api,
        width=1320,
        height=840,
        min_size=(1024, 700),
        frameless=True,
        easy_drag=False,
        background_color='#07080c'
    )
    api.main_window = main_win

    webview.start(debug=False)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        with open('crash.log', 'a', encoding='utf-8') as f:
            f.write(f'\n=== CRASH ===\n{traceback.format_exc()}\n')