# -*- coding: utf-8 -*-
"""
Auto-Update Engine for Church Media Master
Fetches latest release info from GitHub and performs seamless background update.
"""

import os
import sys
import json
import urllib.request
import tempfile
import subprocess
import zipfile
import shutil

CURRENT_VERSION = "2.0.0"
# GitHub repo endpoint for church media player releases
GITHUB_REPO_API = "https://api.github.com/repos/agora02/church-player/releases/latest"

def get_current_version():
    return CURRENT_VERSION

def check_update_sync(api_url=GITHUB_REPO_API):
    """Checks GitHub releases API for newer version."""
    try:
        req = urllib.request.Request(
            api_url,
            headers={'User-Agent': 'ChurchMediaMaster-Updater'}
        )
        with urllib.request.urlopen(req, timeout=4) as response:
            if response.status != 200:
                return {'has_update': False, 'current_version': CURRENT_VERSION}
            
            data = json.loads(response.read().decode('utf-8'))
            latest_tag = data.get('tag_name', '').lstrip('v')
            release_notes = data.get('body', '신규 기능 및 성능 개선이 포함되어 있습니다.')
            
            # Find zip asset
            download_url = None
            for asset in data.get('assets', []):
                if asset.get('name', '').endswith('.zip') or asset.get('name', '').endswith('.exe'):
                    download_url = asset.get('browser_download_url')
                    break

            if not download_url and data.get('zipball_url'):
                download_url = data.get('zipball_url')

            # Version compare
            if latest_tag and latest_tag > CURRENT_VERSION:
                return {
                    'has_update': True,
                    'current_version': CURRENT_VERSION,
                    'latest_version': f"v{latest_tag}",
                    'release_notes': release_notes,
                    'download_url': download_url or data.get('html_url')
                }
    except Exception as e:
        # Offline or repo not yet published
        pass

    return {
        'has_update': False,
        'current_version': CURRENT_VERSION,
        'latest_version': f"v{CURRENT_VERSION}",
        'message': '최신 버전을 사용하고 있습니다.'
    }

def apply_update_script(zip_path, target_dir):
    """Creates a temporary batch file to extract and replace the application."""
    bat_content = f"""@echo off
timeout /t 2 /nobreak > nul
echo Updating Church Media Master...
powershell -Command "Expand-Archive -Path '{zip_path}' -DestinationPath '{target_dir}' -Force"
del /f /q "{zip_path}"
start "" "{os.path.join(target_dir, 'ChurchPlayer.exe')}"
del "%~f0"
exit
"""
    temp_bat = os.path.join(tempfile.gettempdir(), 'church_player_updater.bat')
    with open(temp_bat, 'w', encoding='cp949') as f:
        f.write(bat_content)
    
    subprocess.Popen(['cmd.exe', '/c', temp_bat], shell=False)
    sys.exit(0)
