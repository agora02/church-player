with open('ChurchPlayer.py', 'w', encoding='utf-8') as f:
    f.write('''# -*- coding: utf-8 -*-
"""
Church Media Master - Native Windows Desktop Application
교회 스마트 비디오 & 음악 방송 플레이어 (Windows 네이티브 앱)
"""

import sys
import os
import math
from PyQt6.QtCore import Qt, QUrl, QTimer, QPoint, QRect
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QLinearGradient, QRadialGradient,
    QBrush, QPen, QKeySequence, QShortcut, QCursor, QGuiApplication
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QSlider, QComboBox, QCheckBox,
    QFileDialog, QListWidget, QListWidgetItem, QStackedWidget,
    QGroupBox, QLineEdit, QSpinBox, QRadioButton, QTabWidget
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget


class MusicVisualizerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = 'bars'
        self.track_title = '배경 찬양 / 음악'
        self.is_playing = False
        self.time_offset = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)

        self.particles = []
        for i in range(50):
            self.particles.append({
                'x': (i * 17) % 100 / 100.0,
                'y': (i * 23) % 100 / 100.0,
                'radius': (i % 4) + 2,
                'vx': ((i % 5) - 2) * 0.001,
                'vy': ((i % 7) - 3) * 0.001,
                'color_idx': i % 3
            })

    def set_track_info(self, title):
        self.track_title = title
        self.update()

    def set_playing(self, playing):
        self.is_playing = playing

    def set_theme(self, theme):
        self.theme = theme
        self.update()

    def update_animation(self):
        self.time_offset += 0.03 if self.is_playing else 0.008
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        bg_grad = QLinearGradient(0, 0, w, h)
        bg_grad.setColorAt(0.0, QColor(10, 14, 26))
        bg_grad.setColorAt(0.5, QColor(16, 24, 40))
        bg_grad.setColorAt(1.0, QColor(8, 12, 22))
        painter.fillRect(0, 0, w, h, bg_grad)

        if self.theme == 'bars':
            self.draw_bars(painter, w, h)
        elif self.theme == 'wave':
            self.draw_wave(painter, w, h)
        elif self.theme == 'particles':
            self.draw_particles(painter, w, h)
        else:
            self.draw_ambient(painter, w, h)

        self.draw_center_card(painter, w, h)

    def draw_bars(self, painter, w, h):
        bar_count = 36
        bar_width = (w / bar_count) * 0.65
        gap = (w / bar_count) * 0.35
        grad = QLinearGradient(0, h, 0, h * 0.4)
        grad.setColorAt(0.0, QColor(6, 182, 212, 200))
        grad.setColorAt(0.6, QColor(59, 130, 246, 220))
        grad.setColorAt(1.0, QColor(139, 92, 246, 240))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)

        for i in range(bar_count):
            val = (math.sin(self.time_offset * 2.0 + i * 0.35) * 0.5 + 0.5) * 0.7 + 0.15 if self.is_playing else (math.sin(self.time_offset + i * 0.2) * 0.5 + 0.5) * 0.15 + 0.05
            bar_h = val * (h * 0.45)
            x = i * (bar_width + gap) + gap / 2
            y = h - bar_h - 40
            painter.drawRoundedRect(int(x), int(y), int(bar_width), int(bar_h), 4, 4)
            painter.setBrush(QBrush(QColor(255, 255, 255, 220)))
            painter.drawRect(int(x), int(y), int(bar_width), 3)
            painter.setBrush(QBrush(grad))

    def draw_wave(self, painter, w, h):
        mid_y = h * 0.65
        painter.setBrush(Qt.BrushStyle.NoBrush)
        colors = [QColor(6, 182, 212, 180), QColor(99, 102, 241, 160), QColor(236, 72, 153, 140)]
        for layer in range(3):
            painter.setPen(QPen(colors[layer], 3 + layer * 2))
            points = 50
            prev_pt = None
            for i in range(points + 1):
                x = (i / points) * w
                amp = (70 if self.is_playing else 25) * (1.0 + layer * 0.4)
                y = mid_y + math.sin(i * 0.2 + self.time_offset * (1.5 + layer * 0.3)) * amp * math.sin((i / points) * math.pi)
                pt = QPoint(int(x), int(y))
                if prev_pt:
                    painter.drawLine(prev_pt, pt)
                prev_pt = pt

    def draw_particles(self, painter, w, h):
        painter.setPen(Qt.PenStyle.NoPen)
        colors = [QColor(6, 182, 212), QColor(168, 85, 247), QColor(244, 63, 94)]
        for p in self.particles:
            p['x'] = (p['x'] + p['vx']) % 1.0
            p['y'] = (p['y'] + p['vy']) % 1.0
            px = int(p['x'] * w)
            py = int(p['y'] * h)
            rad = p['radius'] * (1.4 if self.is_playing else 1.0)
            c = colors[p['color_idx']]
            c.setAlpha(180)
            painter.setBrush(QBrush(c))
            painter.drawEllipse(QPoint(px, py), int(rad), int(rad))

    def draw_ambient(self, painter, w, h):
        cx, cy = w / 2, h / 2
        base_r = min(w, h) * 0.25
        pulse = math.sin(self.time_offset * 1.5) * (30 if self.is_playing else 10)
        rad_grad = QRadialGradient(cx, cy, base_r + pulse + 60)
        rad_grad.setColorAt(0.0, QColor(59, 130, 246, 140))
        rad_grad.setColorAt(0.6, QColor(139, 92, 246, 60))
        rad_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(rad_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPoint(int(cx), int(cy)), int(base_r + pulse + 60), int(base_r + pulse + 60))

    def draw_center_card(self, painter, w, h):
        cx, cy = int(w / 2), int(h * 0.4)
        card_w = min(460, int(w * 0.85))
        card_h = 150
        card_x, card_y = cx - int(card_w / 2), cy - int(card_h / 2)

        card_bg = QColor(15, 23, 42, 220)
        painter.setBrush(QBrush(card_bg))
        painter.setPen(QPen(QColor(59, 130, 246, 80), 1.5))
        painter.drawRoundedRect(card_x, card_y, card_w, card_h, 16, 16)

        painter.setFont(QFont('Malgun Gothic', 10, QFont.Weight.Bold))
        painter.setPen(QColor(6, 182, 212))
        painter.drawText(QRect(card_x, card_y + 18, card_w, 24), Qt.AlignmentFlag.AlignCenter, 'WORSHIP MUSIC & BGM')

        painter.setFont(QFont('Malgun Gothic', 15, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRect(card_x + 10, card_y + 48, card_w - 20, 42), Qt.AlignmentFlag.AlignCenter, self.track_title)

        painter.setFont(QFont('Malgun Gothic', 10))
        painter.setPen(QColor(148, 163, 184))
        painter.drawText(QRect(card_x, card_y + 100, card_w, 24), Qt.AlignmentFlag.AlignCenter, '마음을 정돈하고 예배를 준비합니다')


class LiveDisplayWindow(QMainWindow):
    def __init__(self, player, parent=None):
        super().__init__(parent)
        self.player = player
        self.setWindowTitle('Church Live Screen (프로젝터 송출창)')
        self.setStyleSheet('background-color: #000000; color: #ffffff;')

        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        self.video_widget = QVideoWidget(self)
        self.video_widget.setStyleSheet('background-color: #000000;')
        self.stack.addWidget(self.video_widget)

        self.music_widget = MusicVisualizerWidget(self)
        self.stack.addWidget(self.music_widget)

        self.logo_widget = QWidget(self)
        self.logo_widget.setStyleSheet('background-color: #020617;')
        logo_layout = QVBoxLayout(self.logo_widget)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_title = QLabel('환영합니다\n하나님의 은혜와 평강이 함께하시기를 축복합니다', self.logo_widget)
        logo_title.setFont(QFont('Malgun Gothic', 24, QFont.Weight.Bold))
        logo_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_title.setStyleSheet('color: #f8fafc; line-height: 1.6;')
        logo_layout.addWidget(logo_title)
        self.stack.addWidget(self.logo_widget)

        self.blackout_widget = QWidget(self)
        self.blackout_widget.setStyleSheet('background-color: #000000;')
        self.stack.addWidget(self.blackout_widget)

        self.player.setVideoOutput(self.video_widget)

        self.cursor_timer = QTimer(self)
        self.cursor_timer.setSingleShot(True)
        self.cursor_timer.timeout.connect(self.hide_cursor)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        self.unsetCursor()
        self.cursor_timer.start(2000)
        super().mouseMoveEvent(event)

    def hide_cursor(self):
        self.setCursor(Qt.CursorShape.BlankCursor)

    def mouseDoubleClickEvent(self, event):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.showNormal()
        elif event.key() == Qt.Key.Key_F11 or event.key() == Qt.Key.Key_F:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        super().keyPressEvent(event)


class ChurchPlayerMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('CHURCH MEDIA MASTER - 교회 스마트 방송 플레이어 v1.0')
        self.resize(1180, 800)
        self.setMinimumSize(960, 680)

        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(1.0)

        self.playlist = []
        self.current_index = -1
        self.is_blackout = False
        self.is_logo = False
        self.is_ducked = False
        self.current_media_type = 'video'

        self.live_window = LiveDisplayWindow(self.player)

        self.apply_dark_theme()
        self.init_ui()
        self.init_shortcuts()
        self.init_signals()
        self.refresh_screens()

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #090d16;
                color: #e2e8f0;
                font-family: 'Malgun Gothic', 'Segoe UI', sans-serif;
            }
            QGroupBox {
                border: 1px solid #1e293b;
                border-radius: 10px;
                margin-top: 14px;
                font-size: 12px;
                font-weight: bold;
                color: #94a3b8;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 7px 14px;
                color: #f8fafc;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #334155;
                border-color: #475569;
            }
            QPushButton#btnPlay {
                background-color: #2563eb;
                border: 1px solid #3b82f6;
                font-size: 13px;
                padding: 9px 20px;
            }
            QPushButton#btnPlay:hover {
                background-color: #1d4ed8;
            }
            QPushButton#btnLiveStart {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #6366f1);
                border: 1px solid #4f46e5;
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
                padding: 7px 16px;
                border-radius: 8px;
            }
            QPushButton#btnLiveStart:hover {
                background-color: #3b82f6;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #1e293b;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #3b82f6;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #60a5fa;
                width: 14px;
                margin-top: -4px;
                margin-bottom: -4px;
                border-radius: 7px;
            }
            QListWidget {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 4px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px 10px;
                border-radius: 6px;
                margin-bottom: 2px;
            }
            QListWidget::item:hover {
                background-color: #1e293b;
            }
            QListWidget::item:selected {
                background-color: rgba(37, 99, 235, 0.35);
                border: 1px solid #3b82f6;
                color: #ffffff;
            }
            QComboBox, QLineEdit, QSpinBox {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 5px 10px;
                color: #ffffff;
                font-size: 12px;
            }
            QTabWidget::pane {
                border: 1px solid #1e293b;
                border-radius: 8px;
                background-color: #0f172a;
                padding: 10px;
            }
            QTabBar::tab {
                background: #0b1120;
                color: #94a3b8;
                padding: 8px 16px;
                border: 1px solid #1e293b;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background: #0f172a;
                color: #38bdf8;
                border-color: #38bdf8;
            }
        """)

    def init_ui(self):
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(16, 12, 16, 16)
        main_layout.setSpacing(12)

        # Header
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        lbl_app_name = QLabel('⛪ CHURCH MEDIA MASTER', self)
        lbl_app_name.setFont(QFont('Malgun Gothic', 13, QFont.Weight.Bold))
        lbl_app_name.setStyleSheet('color: #ffffff;')
        lbl_sub_desc = QLabel('교회 스마트 비디오 & 음악 방송 시스템 (Windows 네이티브 앱)', self)
        lbl_sub_desc.setFont(QFont('Malgun Gothic', 9))
        lbl_sub_desc.setStyleSheet('color: #64748b;')
        title_box.addWidget(lbl_app_name)
        title_box.addWidget(lbl_sub_desc)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        lbl_screen = QLabel('송출 대상 모니터:', self)
        lbl_screen.setStyleSheet('color: #94a3b8; font-size: 12px; font-weight: bold;')
        header_layout.addWidget(lbl_screen)

        self.cb_screens = QComboBox(self)
        self.cb_screens.setMinimumWidth(220)
        header_layout.addWidget(self.cb_screens)

        self.btn_live_start = QPushButton('🚀 보조 모니터로 송출 시작', self)
        self.btn_live_start.setObjectName('btnLiveStart')
        self.btn_live_start.clicked.connect(self.toggle_live_window)
        header_layout.addWidget(self.btn_live_start)

        main_layout.addLayout(header_layout)

        # Switcher (PVW & PGM)
        switcher_layout = QHBoxLayout()
        switcher_layout.setSpacing(14)

        pvw_box = QGroupBox('PVW (미리보기 화면)', self)
        pvw_inner = QVBoxLayout(pvw_box)
        pvw_inner.setContentsMargins(10, 10, 10, 10)

        self.pvw_mirror = MusicVisualizerWidget(self)
        self.pvw_mirror.setMinimumHeight(180)
        pvw_inner.addWidget(self.pvw_mirror)

        pvw_ctrl = QHBoxLayout()
        self.lbl_pvw_info = QLabel('대기 중인 미디어 없음', self)
        self.lbl_pvw_info.setStyleSheet('color: #64748b; font-size: 11px;')
        pvw_ctrl.addWidget(self.lbl_pvw_info)
        pvw_ctrl.addStretch()

        self.btn_cut = QPushButton('CUT (즉시 송출)', self)
        self.btn_cut.setStyleSheet('background-color: #2563eb; color: #fff;')
        self.btn_cut.clicked.connect(self.cue_cut)
        pvw_ctrl.addWidget(self.btn_cut)
        pvw_inner.addLayout(pvw_ctrl)
        switcher_layout.addWidget(pvw_box, 1)

        pgm_box = QGroupBox('🔴 PGM (현재 프로젝터 실시간 송출 화면)', self)
        pgm_box.setStyleSheet('QGroupBox { border-color: #dc2626; color: #f87171; }')
        pgm_inner = QVBoxLayout(pgm_box)
        pgm_inner.setContentsMargins(10, 10, 10, 10)

        self.pgm_mirror = MusicVisualizerWidget(self)
        self.pgm_mirror.setMinimumHeight(180)
        pgm_inner.addWidget(self.pgm_mirror)

        pgm_ctrl = QHBoxLayout()
        self.btn_duck = QPushButton('🔉 덕킹 (D)', self)
        self.btn_duck.setToolTip('멘트 시 BGM 볼륨 20%로 낮춤 (단축키: D)')
        self.btn_duck.clicked.connect(self.toggle_ducking)
        pgm_ctrl.addWidget(self.btn_duck)

        self.btn_logo = QPushButton('✝️ 로고/대기 (L)', self)
        self.btn_logo.setToolTip('교회 대기화면/로고 화면으로 전환 (단축키: L)')
        self.btn_logo.clicked.connect(self.toggle_logo)
        pgm_ctrl.addWidget(self.btn_logo)

        self.btn_blackout = QPushButton('⚫ 블랙아웃 (B)', self)
        self.btn_blackout.setToolTip('긴급 암전 (단축키: B)')
        self.btn_blackout.setStyleSheet('background-color: #7f1d1d; color: #fecaca;')
        self.btn_blackout.clicked.connect(self.toggle_blackout)
        pgm_ctrl.addWidget(self.btn_blackout)
        pgm_inner.addLayout(pgm_ctrl)
        switcher_layout.addWidget(pgm_box, 1)

        main_layout.addLayout(switcher_layout)

        # Timeline & Controls
        ctrl_box = QGroupBox('플레이어 제어 (Timeline & Controls)', self)
        ctrl_inner = QVBoxLayout(ctrl_box)
        ctrl_inner.setContentsMargins(14, 10, 14, 12)
        ctrl_inner.setSpacing(8)

        time_layout = QHBoxLayout()
        self.lbl_current_time = QLabel('00:00', self)
        self.lbl_current_time.setStyleSheet('font-family: monospace; font-size: 12px; color: #38bdf8; font-weight: bold;')
        time_layout.addWidget(self.lbl_current_time)

        self.slider_time = QSlider(Qt.Orientation.Horizontal, self)
        self.slider_time.setRange(0, 1000)
        self.slider_time.sliderMoved.connect(self.set_position)
        time_layout.addWidget(self.slider_time)

        self.lbl_total_time = QLabel('00:00', self)
        self.lbl_total_time.setStyleSheet('font-family: monospace; font-size: 12px; color: #94a3b8;')
        time_layout.addWidget(self.lbl_total_time)
        ctrl_inner.addLayout(time_layout)

        btn_bar = QHBoxLayout()
        self.btn_prev = QPushButton('⏮ 이전', self)
        self.btn_prev.clicked.connect(self.prev_cue)
        btn_bar.addWidget(self.btn_prev)

        self.btn_rewind = QPushButton('⏪ -10초', self)
        self.btn_rewind.clicked.connect(lambda: self.seek_relative(-10000))
        btn_bar.addWidget(self.btn_rewind)

        self.btn_play = QPushButton('▶ 재생', self)
        self.btn_play.setObjectName('btnPlay')
        self.btn_play.clicked.connect(self.toggle_play)
        btn_bar.addWidget(self.btn_play)

        self.btn_forward = QPushButton('⏩ +10초', self)
        self.btn_forward.clicked.connect(lambda: self.seek_relative(10000))
        btn_bar.addWidget(self.btn_forward)

        self.btn_next = QPushButton('⏭ 다음', self)
        self.btn_next.clicked.connect(self.next_cue)
        btn_bar.addWidget(self.btn_next)

        btn_bar.addSpacing(20)
        btn_bar.addWidget(QLabel('모드:', self))
        self.rb_video = QRadioButton('🎬 비디오', self)
        self.rb_video.setChecked(True)
        self.rb_video.toggled.connect(self.on_mode_toggled)
        btn_bar.addWidget(self.rb_video)

        self.rb_audio = QRadioButton('🎵 음악 전용', self)
        self.rb_audio.toggled.connect(self.on_mode_toggled)
        btn_bar.addWidget(self.rb_audio)

        btn_bar.addStretch()
        btn_bar.addWidget(QLabel('🔊 볼륨:', self))
        self.slider_volume = QSlider(Qt.Orientation.Horizontal, self)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(100)
        self.slider_volume.setFixedWidth(100)
        self.slider_volume.valueChanged.connect(self.set_volume)
        btn_bar.addWidget(self.slider_volume)

        ctrl_inner.addLayout(btn_bar)
        main_layout.addWidget(ctrl_box)

        # Lower Tabs
        self.tabs = QTabWidget(self)
        tab_cue = QWidget()
        tab_cue_layout = QVBoxLayout(tab_cue)
        tab_cue_layout.setContentsMargins(8, 8, 8, 8)

        cue_top = QHBoxLayout()
        cue_top.addWidget(QLabel('예배 미디어 파일 목록:', self))
        self.cb_auto_next = QCheckBox('미디어 종료 시 다음 순서 자동 재생', self)
        self.cb_auto_next.setChecked(True)
        cue_top.addWidget(self.cb_auto_next)
        cue_top.addStretch()

        btn_add = QPushButton('➕ 파일 추가', self)
        btn_add.clicked.connect(self.add_files)
        cue_top.addWidget(btn_add)

        btn_del = QPushButton('🗑️ 삭제', self)
        btn_del.clicked.connect(self.remove_selected_file)
        cue_top.addWidget(btn_del)
        tab_cue_layout.addLayout(cue_top)

        self.list_playlist = QListWidget(self)
        self.list_playlist.itemDoubleClicked.connect(self.on_playlist_double_clicked)
        tab_cue_layout.addWidget(self.list_playlist)
        self.tabs.addTab(tab_cue, '📋 예배 순서 큐 (Cue List)')

        tab_vis = QWidget()
        tab_vis_layout = QGridLayout(tab_vis)
        tab_vis_layout.addWidget(QLabel('음악 모드 비주얼라이저 테마:'), 0, 0)
        self.cb_vis_theme = QComboBox(self)
        self.cb_vis_theme.addItems(['네온 스펙트럼 바 (bars)', '은혜로운 찬양 파형 (wave)', '은하수 펄스 파티클 (particles)', '앰비언트 글로우 (ambient)'])
        self.cb_vis_theme.currentIndexChanged.connect(self.change_vis_theme)
        tab_vis_layout.addWidget(self.cb_vis_theme, 0, 1)

        tab_vis_layout.addWidget(QLabel('곡명 / 앨범 타이틀 직접 입력:'), 1, 0)
        self.txt_track_title = QLineEdit('배경 찬양 / 기도회 BGM', self)
        tab_vis_layout.addWidget(self.txt_track_title, 1, 1)

        btn_apply_title = QPushButton('타이틀 적용', self)
        btn_apply_title.clicked.connect(lambda: self.live_window.music_widget.set_track_info(self.txt_track_title.text()))
        tab_vis_layout.addWidget(btn_apply_title, 1, 2)
        self.tabs.addTab(tab_vis, '🎨 오디오 비주얼라이저 설정')

        main_layout.addWidget(self.tabs)

    def init_signals(self):
        self.player.positionChanged.connect(self.on_position_changed)
        self.player.durationChanged.connect(self.on_duration_changed)
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)

    def init_shortcuts(self):
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self.toggle_play)
        QShortcut(QKeySequence(Qt.Key.Key_B), self, self.toggle_blackout)
        QShortcut(QKeySequence(Qt.Key.Key_L), self, self.toggle_logo)
        QShortcut(QKeySequence(Qt.Key.Key_D), self, self.toggle_ducking)
        QShortcut(QKeySequence(Qt.Key.Key_N), self, self.next_cue)
        QShortcut(QKeySequence(Qt.Key.Key_P), self, self.prev_cue)
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, lambda: self.seek_relative(5000))
        QShortcut(QKeySequence(Qt.Key.Key_Left), self, lambda: self.seek_relative(-5000))

    def refresh_screens(self):
        self.cb_screens.clear()
        screens = QGuiApplication.screens()
        for idx, screen in enumerate(screens):
            name = f'모니터 #{idx + 1}: {screen.name()} ({screen.geometry().width()}x{screen.geometry().height()})'
            if idx == 1:
                name += ' [추천: 보조 모니터/프로젝터]'
            self.cb_screens.addItem(name, screen)
        if len(screens) > 1:
            self.cb_screens.setCurrentIndex(1)

    def toggle_live_window(self):
        if self.live_window.isVisible():
            self.live_window.hide()
            self.btn_live_start.setText('🚀 보조 모니터로 송출 시작')
            self.btn_live_start.setStyleSheet('')
        else:
            selected_screen = self.cb_screens.currentData()
            if selected_screen:
                geo = selected_screen.geometry()
                self.live_window.move(geo.topLeft())
                self.live_window.showFullScreen()
            else:
                self.live_window.show()
            self.btn_live_start.setText('🔴 송출창 켜짐 (클릭 시 닫기)')
            self.btn_live_start.setStyleSheet('background-color: #059669; border-color: #10b981; color: #fff;')

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, '미디어 파일 선택', '',
            'Media Files (*.mp4 *.mkv *.avi *.mov *.mp3 *.wav *.flac *.aac *.m4a);;All Files (*.*)'
        )
        for f in files:
            basename = os.path.basename(f)
            is_audio = f.lower().endswith(('.mp3', '.wav', '.flac', '.aac', '.m4a'))
            media_type = 'audio' if is_audio else 'video'
            icon_str = '🎵 [오디오]' if is_audio else '🎬 [비디오]'
            item = QListWidgetItem(f'{icon_str} {basename}')
            item.setData(Qt.ItemDataRole.UserRole, {'path': f, 'type': media_type, 'title': basename})
            self.list_playlist.addItem(item)
            self.playlist.append({'path': f, 'type': media_type, 'title': basename})

        if self.current_index == -1 and len(self.playlist) > 0:
            self.load_cue(0, auto_play=False)

    def remove_selected_file(self):
        row = self.list_playlist.currentRow()
        if row >= 0:
            self.list_playlist.takeItem(row)
            self.playlist.pop(row)
            if self.current_index == row:
                self.player.stop()
                self.current_index = -1

    def on_playlist_double_clicked(self, item):
        row = self.list_playlist.row(item)
        self.load_cue(row, auto_play=True)

    def load_cue(self, index, auto_play=False):
        if index < 0 or index >= len(self.playlist):
            return

        self.current_index = index
        self.list_playlist.setCurrentRow(index)
        item_data = self.playlist[index]

        media_url = QUrl.fromLocalFile(item_data['path'])
        self.player.setSource(media_url)

        self.current_media_type = item_data['type']
        if self.current_media_type == 'video':
            self.rb_video.setChecked(True)
            self.live_window.stack.setCurrentIndex(0)
        else:
            self.rb_audio.setChecked(True)
            self.live_window.music_widget.set_track_info(item_data['title'])
            self.live_window.stack.setCurrentIndex(1)

        self.pgm_mirror.set_track_info(item_data['title'])
        self.pvw_mirror.set_track_info(item_data['title'])
        self.lbl_pvw_info.setText(f'선택됨: {item_data["title"]}')

        if auto_play:
            self.player.play()
            self.btn_play.setText('⏸ 정지')
            self.live_window.music_widget.set_playing(True)
            self.pgm_mirror.set_playing(True)
        else:
            self.btn_play.setText('▶ 재생')
            self.live_window.music_widget.set_playing(False)
            self.pgm_mirror.set_playing(False)

    def cue_cut(self):
        row = self.list_playlist.currentRow()
        if row >= 0:
            self.load_cue(row, auto_play=True)

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.btn_play.setText('▶ 재생')
            self.live_window.music_widget.set_playing(False)
            self.pgm_mirror.set_playing(False)
        else:
            if self.current_index == -1 and len(self.playlist) > 0:
                self.load_cue(0, auto_play=True)
                return
            self.player.play()
            self.btn_play.setText('⏸ 정지')
            self.live_window.music_widget.set_playing(True)
            self.pgm_mirror.set_playing(True)

    def prev_cue(self):
        if self.current_index > 0:
            self.load_cue(self.current_index - 1, auto_play=True)

    def next_cue(self):
        if self.current_index < len(self.playlist) - 1:
            self.load_cue(self.current_index + 1, auto_play=True)

    def seek_relative(self, offset_ms):
        pos = self.player.position() + offset_ms
        self.player.setPosition(max(0, min(self.player.duration(), pos)))

    def set_position(self, value):
        if self.player.duration() > 0:
            pos = int((value / 1000.0) * self.player.duration())
            self.player.setPosition(pos)

    def set_volume(self, value):
        vol = value / 100.0
        if self.is_ducked:
            vol *= 0.2
        self.audio_output.setVolume(vol)

    def toggle_ducking(self):
        self.is_ducked = not self.is_ducked
        if self.is_ducked:
            self.btn_duck.setStyleSheet('background-color: #d97706; color: #ffffff;')
        else:
            self.btn_duck.setStyleSheet('')
        self.set_volume(self.slider_volume.value())

    def toggle_logo(self):
        self.is_logo = not self.is_logo
        if self.is_logo:
            self.btn_logo.setStyleSheet('background-color: #4f46e5; color: #ffffff;')
            self.live_window.stack.setCurrentIndex(2)
        else:
            self.btn_logo.setStyleSheet('')
            self.live_window.stack.setCurrentIndex(1 if self.current_media_type == 'audio' else 0)

    def toggle_blackout(self):
        self.is_blackout = not self.is_blackout
        if self.is_blackout:
            self.btn_blackout.setStyleSheet('background-color: #dc2626; color: #ffffff; font-weight: bold;')
            self.live_window.stack.setCurrentIndex(3)
        else:
            self.btn_blackout.setStyleSheet('background-color: #7f1d1d; color: #fecaca;')
            self.live_window.stack.setCurrentIndex(1 if self.current_media_type == 'audio' else 0)

    def on_mode_toggled(self):
        if self.rb_video.isChecked():
            self.current_media_type = 'video'
            if not self.is_blackout and not self.is_logo:
                self.live_window.stack.setCurrentIndex(0)
        else:
            self.current_media_type = 'audio'
            if not self.is_blackout and not self.is_logo:
                self.live_window.stack.setCurrentIndex(1)

    def change_vis_theme(self, index):
        themes = ['bars', 'wave', 'particles', 'ambient']
        theme = themes[index]
        self.live_window.music_widget.set_theme(theme)
        self.pgm_mirror.set_theme(theme)
        self.pvw_mirror.set_theme(theme)

    def on_position_changed(self, position):
        dur = self.player.duration()
        if dur > 0:
            val = int((position / dur) * 1000)
            self.slider_time.setValue(val)
        self.lbl_current_time.setText(self.format_time(position))

    def on_duration_changed(self, duration):
        self.lbl_total_time.setText(self.format_time(duration))

    def on_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self.cb_auto_next.isChecked() and self.current_index < len(self.playlist) - 1:
                self.next_cue()
            else:
                self.btn_play.setText('▶ 재생')
                self.live_window.music_widget.set_playing(False)
                self.pgm_mirror.set_playing(False)

    def format_time(self, ms):
        total_sec = int(ms / 1000)
        mins = total_sec // 60
        secs = total_sec % 60
        return f'{mins:02d}:{secs:02d}'


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = ChurchPlayerMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
''')
print("Successfully generated ChurchPlayer.py")
