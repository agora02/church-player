/**
 * Church Studio Pro - Controller Script with Dynamic Monitor Selection
 * Enhanced with Memory Cleanup, Input Isolation & Hot-Plug Screen Detection
 */
document.addEventListener('DOMContentLoaded', () => {
  const sync = new MediaSync(false);
  const displayManager = new DisplayManager();
  displayManager.init();

  // Elements
  const pgmVideo = document.getElementById('pgmVideo');
  const pgmAudio = document.getElementById('pgmAudio');
  const pgmCanvas = document.getElementById('pgmVisualizerCanvas');
  const pgmStandby = document.getElementById('pgmStandbyPlaceholder');
  const pgmBlackout = document.getElementById('pgmBlackoutOverlay');
  const ambientGlow = document.getElementById('ambientGlow');

  const pvwVideo = document.getElementById('pvwVideo');
  const pvwAudio = document.getElementById('pvwAudio');
  const pvwCanvas = document.getElementById('pvwVisualizerCanvas');
  const pvwStandby = document.getElementById('pvwStandbyPlaceholder');
  const pvwTitle = document.getElementById('pvwTitle');

  const topNowPlayingText = document.getElementById('topNowPlayingText');
  const liveDot = document.getElementById('liveDot');
  const cueCount = document.getElementById('cueCount');

  const btnPlayPause = document.getElementById('btnPlayPause');
  const playIcon = document.getElementById('playIcon');
  const seekSlider = document.getElementById('seekSlider');
  const lblCurrentTime = document.getElementById('lblCurrentTime');
  const lblTotalTime = document.getElementById('lblTotalTime');

  const btnOpenLive = document.getElementById('btnOpenLive');
  const btnLiveText = document.getElementById('btnLiveText');
  const selScreenChoice = document.getElementById('selScreenChoice');

  // Custom Window Controls
  const btnWinMinimize = document.getElementById('btnWinMinimize');
  const btnWinMaximize = document.getElementById('btnWinMaximize');
  const btnWinClose = document.getElementById('btnWinClose');

  if (btnWinMinimize) {
    btnWinMinimize.onclick = () => {
      if (window.pywebview && window.pywebview.api && window.pywebview.api.minimize_window) {
        window.pywebview.api.minimize_window();
      }
    };
  }
  if (btnWinMaximize) {
    btnWinMaximize.onclick = () => {
      if (window.pywebview && window.pywebview.api && window.pywebview.api.maximize_window) {
        window.pywebview.api.maximize_window();
      }
    };
  }
  if (btnWinClose) {
    btnWinClose.onclick = () => {
      if (window.pywebview && window.pywebview.api && window.pywebview.api.close_window) {
        window.pywebview.api.close_window();
      }
    };
  }

  const btnCut = document.getElementById('btnCut');
  const btnDucking = document.getElementById('btnDucking');
  const btnLogoScreen = document.getElementById('btnLogoScreen');
  const btnBlackout = document.getElementById('btnBlackout');

  const btnPrevCue = document.getElementById('btnPrevCue');
  const btnNextCue = document.getElementById('btnNextCue');
  const btnRewind10 = document.getElementById('btnRewind10');
  const btnForward10 = document.getElementById('btnForward10');

  const btnModeVideo = document.getElementById('btnModeVideo');
  const btnModeMusic = document.getElementById('btnModeMusic');
  const volSlider = document.getElementById('volSlider');
  const lblVolPercent = document.getElementById('lblVolPercent');

  const mediaFileInput = document.getElementById('mediaFileInput');
  const btnAddFiles = document.getElementById('btnAddFiles');
  const btnClearCue = document.getElementById('btnClearCue');
  const cueList = document.getElementById('cueList');
  const chkAutoNext = document.getElementById('chkAutoNext');
  const chkLoopCurrent = document.getElementById('chkLoopCurrent');

  const selVisTheme = document.getElementById('selVisTheme');
  const txtTrackTitle = document.getElementById('txtTrackTitle');
  const btnApplyTitle = document.getElementById('btnApplyTitle');

  // Auto-Update Elements
  const btnCheckUpdate = document.getElementById('btnCheckUpdate');
  const updateModal = document.getElementById('updateModal');
  const updateTitle = document.getElementById('updateTitle');
  const updateVersionText = document.getElementById('updateVersionText');
  const updateNotes = document.getElementById('updateNotes');
  const updateProgressArea = document.getElementById('updateProgressArea');
  const updateModalActions = document.getElementById('updateModalActions');
  const btnStartUpdate = document.getElementById('btnStartUpdate');
  const btnCloseUpdateModal = document.getElementById('btnCloseUpdateModal');

  let pendingDownloadUrl = null;

  // Dynamically load version from native API
  async function loadAppVersion() {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.get_version) {
      try {
        const v = await window.pywebview.api.get_version();
        if (v) {
          btnCheckUpdate.textContent = `v${v} ✨`;
        }
      } catch (e) {}
    }
  }
  window.addEventListener('pywebviewready', loadAppVersion);
  setTimeout(loadAppVersion, 300);

  async function checkUpdate(manual = false) {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.check_for_updates) {
      try {
        const info = await window.pywebview.api.check_for_updates();
        if (info && info.has_update) {
          pendingDownloadUrl = info.download_url;
          updateTitle.textContent = '새로운 버전이 출시되었습니다!';
          updateVersionText.textContent = `최신 버전: ${info.latest_version} (현재 v${info.current_version})`;
          updateNotes.textContent = info.release_notes || '신규 기능 및 성능 개선이 포함되어 있습니다.';
          updateModal.classList.remove('hidden');
        } else if (manual) {
          alert(`현재 최신 버전(v${info ? info.current_version : '2.1.0'})을 사용 중입니다.`);
        }
      } catch (e) {
        if (manual) alert('업데이트 서버와 연결할 수 없습니다. 오프라인 상태입니다.');
      }
    }
  }

  btnCheckUpdate.onclick = () => checkUpdate(true);
  btnCloseUpdateModal.onclick = () => updateModal.classList.add('hidden');

  btnStartUpdate.onclick = async () => {
    if (!pendingDownloadUrl) return;
    updateProgressArea.classList.remove('hidden');
    updateModalActions.classList.add('hidden');
    if (window.pywebview && window.pywebview.api && window.pywebview.api.download_and_install_update) {
      await window.pywebview.api.download_and_install_update(pendingDownloadUrl);
    }
  };

  // Visualizers
  const pvwVis = new AudioVisualizer(pvwCanvas, pvwAudio);
  const pgmVis = new AudioVisualizer(pgmCanvas, pgmAudio);

  // State
  let playlist = [];
  let currentPvwIndex = -1;
  let currentPgmIndex = -1;
  let isSeeking = false;
  let isDucked = false;
  let isLogo = false;
  let isBlackout = false;
  let currentMode = 'video';

  function formatTime(sec) {
    if (isNaN(sec) || sec < 0) return '00:00';
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }

  function updateAmbientColor(type) {
    if (!ambientGlow) return;
    if (type === 'video') {
      ambientGlow.style.background = 'radial-gradient(circle, rgba(59, 130, 246, 0.22) 0%, rgba(99, 102, 241, 0.1) 50%, transparent 70%)';
    } else {
      ambientGlow.style.background = 'radial-gradient(circle, rgba(168, 85, 247, 0.25) 0%, rgba(236, 72, 153, 0.12) 50%, transparent 70%)';
    }
  }

  // Load Screens list dynamically (Hot-Plug Support)
  async function loadScreensList() {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.get_screens) {
      try {
        const screens = await window.pywebview.api.get_screens();
        if (screens && screens.length > 0) {
          const currentVal = selScreenChoice.value;
          selScreenChoice.innerHTML = '';
          screens.forEach((s) => {
            const opt = document.createElement('option');
            opt.value = s.index;
            opt.textContent = s.name;
            selScreenChoice.appendChild(opt);
          });
          if (screens.some(s => String(s.index) === currentVal)) {
            selScreenChoice.value = currentVal;
          } else if (screens.length > 1) {
            selScreenChoice.value = '1';
          }
        }
      } catch (err) {
        console.warn('Failed to get screens from native API:', err);
      }
    }
  }
  window.addEventListener('pywebviewready', loadScreensList);
  setTimeout(loadScreensList, 500);
  selScreenChoice.onmousedown = loadScreensList;
  selScreenChoice.onfocus = loadScreensList;

  // Load to PVW
  function loadToPvw(index) {
    if (index < 0 || index >= playlist.length) return;
    currentPvwIndex = index;
    const item = playlist[index];
    pvwTitle.textContent = item.title;

    if (item.type === 'video') {
      pvwVideo.src = item.url;
      pvwVideo.classList.remove('hidden');
      pvwAudio.src = '';
      pvwCanvas.classList.add('hidden');
      pvwStandby.classList.add('hidden');
      pvwVis.stop();
    } else {
      pvwAudio.src = item.url;
      pvwVideo.src = '';
      pvwVideo.classList.add('hidden');
      pvwCanvas.classList.remove('hidden');
      pvwStandby.classList.add('hidden');
      pvwVis.start();
    }

    document.querySelectorAll('.cue-item').forEach((el, idx) => {
      el.classList.toggle('selected', idx === index);
    });
  }

  // CUT to PGM
  function cutToPgm(index = currentPvwIndex, autoPlay = true) {
    if (index < 0 || index >= playlist.length) return;
    currentPgmIndex = index;
    const item = playlist[index];
    currentMode = item.type;
    updateAmbientColor(currentMode);

    if (currentMode === 'video') {
      btnModeVideo.classList.add('active');
      btnModeMusic.classList.remove('active');
      pgmVideo.src = item.url;
      pgmVideo.classList.remove('hidden');
      pgmAudio.src = '';
      pgmCanvas.classList.add('hidden');
      pgmStandby.classList.add('hidden');
      pgmVis.stop();
    } else {
      btnModeMusic.classList.add('active');
      btnModeVideo.classList.remove('active');
      pgmAudio.src = item.url;
      pgmVideo.src = '';
      pgmVideo.classList.add('hidden');
      pgmCanvas.classList.remove('hidden');
      pgmStandby.classList.add('hidden');
      pgmVis.start();
    }

    topNowPlayingText.textContent = `▶ ${item.title}`;
    txtTrackTitle.value = item.title;

    // Reset emergency overlays
    isLogo = false;
    isBlackout = false;
    btnLogoScreen.classList.remove('active');
    btnBlackout.classList.remove('active');
    pgmBlackout.classList.add('hidden');

    const activeEl = currentMode === 'video' ? pgmVideo : pgmAudio;
    activeEl.volume = isDucked ? (volSlider.value / 100) * 0.2 : (volSlider.value / 100);

    if (autoPlay) {
      activeEl.play().then(() => {
        setPlayState(true);
      }).catch(err => console.warn(err));
    }

    // Broadcast to Live Display
    sync.updateState({
      isPlaying: autoPlay,
      mediaSrc: item.url,
      mediaName: item.title,
      mediaType: currentMode,
      currentTime: 0,
      isBlackout: false,
      isLogo: false
    });
  }

  function setPlayState(playing) {
    if (playing) {
      playIcon.innerHTML = '<rect width="4" height="16" x="6" y="4"/><rect width="4" height="16" x="14" y="4"/>';
    } else {
      playIcon.innerHTML = '<polygon points="5 3 19 12 5 21 5 3"/>';
    }
  }

  function togglePlay() {
    const activeEl = currentMode === 'video' ? pgmVideo : pgmAudio;
    if (!activeEl.src) {
      if (playlist.length > 0) cutToPgm(0, true);
      return;
    }

    if (activeEl.paused) {
      activeEl.play();
      setPlayState(true);
      sync.updateState({ isPlaying: true });
    } else {
      activeEl.pause();
      setPlayState(false);
      sync.updateState({ isPlaying: false });
    }
  }

  btnPlayPause.onclick = togglePlay;
  btnCut.onclick = () => cutToPgm(currentPvwIndex, true);

  // Time Updates
  function attachTimeListeners(el) {
    el.ontimeupdate = () => {
      if (isSeeking) return;
      lblCurrentTime.textContent = formatTime(el.currentTime);
      lblTotalTime.textContent = formatTime(el.duration);
      if (el.duration > 0) {
        seekSlider.value = (el.currentTime / el.duration) * 100;
        seekSlider.style.setProperty('--progress', seekSlider.value + '%');
      }
    };

    el.onended = () => {
      if (chkLoopCurrent.checked) {
        el.currentTime = 0;
        el.play();
      } else if (chkAutoNext.checked && currentPgmIndex < playlist.length - 1) {
        cutToPgm(currentPgmIndex + 1, true);
      } else {
        setPlayState(false);
        sync.updateState({ isPlaying: false });
      }
    };
  }
  attachTimeListeners(pgmVideo);
  attachTimeListeners(pgmAudio);

  // Safe Seeking (0ms sync)
  seekSlider.oninput = () => {
    isSeeking = true;
    seekSlider.style.setProperty('--progress', seekSlider.value + '%');
    const activeEl = currentMode === 'video' ? pgmVideo : pgmAudio;
    if (activeEl.duration > 0) {
      const previewTime = (seekSlider.value / 100) * activeEl.duration;
      lblCurrentTime.textContent = formatTime(previewTime);
    }
  };

  seekSlider.onchange = () => {
    const activeEl = currentMode === 'video' ? pgmVideo : pgmAudio;
    if (activeEl.duration > 0) {
      const targetTime = (seekSlider.value / 100) * activeEl.duration;
      activeEl.currentTime = targetTime;
      sync.updateState({ currentTime: targetTime });
    }
    seekSlider.style.setProperty('--progress', seekSlider.value + '%');
    isSeeking = false;
  };

  // Skip & Seek Buttons
  btnRewind10.onclick = () => {
    const el = currentMode === 'video' ? pgmVideo : pgmAudio;
    el.currentTime = Math.max(0, el.currentTime - 10);
    sync.updateState({ currentTime: el.currentTime });
    if (el.duration > 0) {
      seekSlider.value = (el.currentTime / el.duration) * 100;
      seekSlider.style.setProperty('--progress', seekSlider.value + '%');
    }
  };
  btnForward10.onclick = () => {
    const el = currentMode === 'video' ? pgmVideo : pgmAudio;
    el.currentTime = Math.min(el.duration || 0, el.currentTime + 10);
    sync.updateState({ currentTime: el.currentTime });
    if (el.duration > 0) {
      seekSlider.value = (el.currentTime / el.duration) * 100;
      seekSlider.style.setProperty('--progress', seekSlider.value + '%');
    }
  };
  btnPrevCue.onclick = () => {
    if (currentPgmIndex > 0) cutToPgm(currentPgmIndex - 1, true);
  };
  btnNextCue.onclick = () => {
    if (currentPgmIndex < playlist.length - 1) cutToPgm(currentPgmIndex + 1, true);
  };

  // Mode buttons
  btnModeVideo.onclick = () => {
    currentMode = 'video';
    btnModeVideo.classList.add('active');
    btnModeMusic.classList.remove('active');
    updateAmbientColor('video');
  };
  btnModeMusic.onclick = () => {
    currentMode = 'audio';
    btnModeMusic.classList.add('active');
    btnModeVideo.classList.remove('active');
    updateAmbientColor('audio');
  };

  // Volume
  volSlider.oninput = () => {
    const vol = volSlider.value / 100;
    lblVolPercent.textContent = `${volSlider.value}%`;
    volSlider.style.setProperty('--vol-progress', volSlider.value + '%');
    const finalVol = isDucked ? vol * 0.2 : vol;
    pgmVideo.volume = finalVol;
    pgmAudio.volume = finalVol;
    sync.updateState({ volume: finalVol });
  };
  volSlider.oninput();

  // Emergency Switches
  btnDucking.onclick = () => {
    isDucked = !isDucked;
    btnDucking.classList.toggle('active', isDucked);
    volSlider.oninput();
  };

  btnLogoScreen.onclick = () => {
    isLogo = !isLogo;
    btnLogoScreen.classList.toggle('active', isLogo);
    sync.updateState({ isLogo: isLogo });
  };

  btnBlackout.onclick = () => {
    isBlackout = !isBlackout;
    btnBlackout.classList.toggle('active', isBlackout);
    pgmBlackout.classList.toggle('hidden', !isBlackout);
    sync.updateState({ isBlackout: isBlackout });
  };

  // Visualizer Themes
  selVisTheme.onchange = () => {
    pvwVis.setTheme(selVisTheme.value);
    pgmVis.setTheme(selVisTheme.value);
    sync.updateState({ visualizerTheme: selVisTheme.value });
  };

  btnApplyTitle.onclick = () => {
    sync.updateState({ mediaName: txtTrackTitle.value });
  };

  // File Selector
  btnAddFiles.onclick = () => {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.open_file_dialog) {
      window.pywebview.api.open_file_dialog().then(files => {
        if (files) handleSelectedFiles(files);
      });
    } else {
      mediaFileInput.click();
    }
  };

  mediaFileInput.onchange = (e) => {
    handleSelectedFiles(Array.from(e.target.files));
  };

  function handleSelectedFiles(files) {
    if (!files || files.length === 0) return;
    const audioExts = ['.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg', '.wma', '.mid', '.midi'];
    for (const f of files) {
      const rawPath = typeof f === 'string' ? f : (f.path || f.name);
      const name = rawPath.split(/[\\/]/).pop();
      const dotIdx = name.lastIndexOf('.');
      const ext = dotIdx !== -1 ? name.slice(dotIdx).toLowerCase() : '';
      const isAudio = audioExts.includes(ext);
      const title = dotIdx !== -1 ? name.slice(0, dotIdx) : name;
      const url = typeof f === 'string' ? f : URL.createObjectURL(f);
      playlist.push({
        name: name,
        title: title,
        type: isAudio ? 'audio' : 'video',
        url: url
      });
    }
    renderCueList();
    if (currentPvwIndex === -1 && playlist.length > 0) {
      loadToPvw(0);
    }
  }

  function renderCueList() {
    cueCount.textContent = `${playlist.length}개`;
    if (playlist.length === 0) {
      cueList.innerHTML = `
        <li class="empty-state-card">
          <div class="empty-icon-circle">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M12 12v9"/><path d="m16 16-4-4-4 4"/></svg>
          </div>
          <p class="empty-primary">등록된 미디어가 없습니다</p>
          <p class="empty-sub">파일을 이곳으로 드래그 & 드롭하세요</p>
        </li>
      `;
      return;
    }

    cueList.innerHTML = '';
    playlist.forEach((item, idx) => {
      const li = document.createElement('li');
      li.className = `cue-item ${idx === currentPvwIndex ? 'selected' : ''}`;
      li.innerHTML = `
        <div class="cue-item-info">
          <span class="cue-type-badge ${item.type}">${item.type === 'video' ? '🎬 비디오' : '🎵 찬양'}</span>
          <span class="cue-title">${item.title}</span>
        </div>
        <button class="btn-del-item" title="삭제">
          <svg class="icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" x2="6" y1="6" y2="18"/><line x1="6" x2="18" y1="6" y2="18"/></svg>
        </button>
      `;

      li.onclick = (e) => {
        if (e.target.closest('.btn-del-item')) {
          const removed = playlist.splice(idx, 1)[0];
          // Memory Cleanup
          if (removed && removed.url && removed.url.startsWith('blob:')) {
            URL.revokeObjectURL(removed.url);
          }
          renderCueList();
          return;
        }
        loadToPvw(idx);
      };

      li.ondblclick = () => {
        cutToPgm(idx, true);
      };

      cueList.appendChild(li);
    });
  }

  btnClearCue.onclick = () => {
    // Memory Cleanup for all items
    playlist.forEach(item => {
      if (item.url && item.url.startsWith('blob:')) {
        URL.revokeObjectURL(item.url);
      }
    });
    playlist = [];
    currentPvwIndex = -1;
    currentPgmIndex = -1;
    pvwVideo.src = '';
    pvwAudio.src = '';
    pgmVideo.src = '';
    pgmAudio.src = '';
    pvwStandby.classList.remove('hidden');
    pgmStandby.classList.remove('hidden');
    topNowPlayingText.textContent = '송출 대기 중';
    renderCueList();
  };

  // Drag & Drop with Visual Feedback
  const studioSidebar = document.querySelector('.studio-sidebar');
  window.addEventListener('dragover', (e) => {
    e.preventDefault();
    if (studioSidebar) studioSidebar.classList.add('drag-over');
  });
  window.addEventListener('dragleave', (e) => {
    if (e.clientX <= 0 || e.clientY <= 0) {
      if (studioSidebar) studioSidebar.classList.remove('drag-over');
    }
  });
  window.addEventListener('drop', (e) => {
    e.preventDefault();
    if (studioSidebar) studioSidebar.classList.remove('drag-over');
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleSelectedFiles(Array.from(e.dataTransfer.files));
    }
  });

  // Open Live Window with Selected Screen
  btnOpenLive.onclick = async () => {
    const selectedScreenIndex = parseInt(selScreenChoice.value, 10) || 0;
    if (window.pywebview && window.pywebview.api && window.pywebview.api.toggle_live_window) {
      window.pywebview.api.toggle_live_window(selectedScreenIndex);
    } else {
      await displayManager.openLiveWindow();
    }
  };

  // Sync listener
  sync.subscribe((type, data) => {
    if (type === 'LIVE_STATUS_CHANGE') {
      if (data.connected) {
        liveDot.classList.add('live');
        btnOpenLive.classList.add('active');
        btnLiveText.textContent = '🔴 송출창 켜짐';
      } else {
        liveDot.classList.remove('live');
        btnOpenLive.classList.remove('active');
        btnLiveText.textContent = '🚀 송출 시작';
      }
    }
  });

  // Keyboard Shortcuts (Input Isolation)
  window.addEventListener('keydown', (e) => {
    // Isolate when typing in inputs, select boxes or contenteditable
    const tag = e.target.tagName;
    if (['INPUT', 'SELECT', 'TEXTAREA'].includes(tag) || e.target.isContentEditable) {
      return;
    }

    if (e.code === 'Space') {
      e.preventDefault();
      togglePlay();
    } else if (e.code === 'KeyB') {
      btnBlackout.click();
    } else if (e.code === 'KeyL') {
      btnLogoScreen.click();
    } else if (e.code === 'KeyD') {
      btnDucking.click();
    } else if (e.code === 'KeyN') {
      btnNextCue.click();
    } else if (e.code === 'KeyP') {
      btnPrevCue.click();
    } else if (e.code === 'ArrowLeft') {
      btnRewind10.click();
    } else if (e.code === 'ArrowRight') {
      btnForward10.click();
    }
  });
});