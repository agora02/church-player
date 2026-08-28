/**
 * Live Display Screen Sync Receiver
 */
document.addEventListener('DOMContentLoaded', () => {
  const sync = new MediaSync(true);

  const liveVideo = document.getElementById('liveVideo');
  const liveAudio = document.getElementById('liveAudio');
  const liveCanvas = document.getElementById('liveVisualizerCanvas');
  const liveStandby = document.getElementById('liveStandbyScreen');
  const liveBlackout = document.getElementById('liveBlackoutOverlay');

  const visualizer = new AudioVisualizer(liveCanvas, liveAudio);

  let currentSrc = '';
  let currentType = 'video';

  sync.subscribe((type, state) => {
    if (type === 'STATE_UPDATE') {
      // 1. Blackout
      if (state.isBlackout) {
        liveBlackout.classList.remove('hidden');
      } else {
        liveBlackout.classList.add('hidden');
      }

      // 2. Standby / Logo
      if (state.isLogo || !state.mediaSrc) {
        liveStandby.classList.remove('hidden');
        liveVideo.classList.add('hidden');
        liveCanvas.classList.add('hidden');
        liveVideo.pause();
        liveAudio.pause();
        visualizer.stop();
        return;
      } else {
        liveStandby.classList.add('hidden');
      }

      // 3. Media Switch
      if (currentSrc !== state.mediaSrc || currentType !== state.mediaType) {
        currentSrc = state.mediaSrc;
        currentType = state.mediaType;

        if (currentType === 'video') {
          liveVideo.src = currentSrc;
          liveVideo.classList.remove('hidden');
          liveCanvas.classList.add('hidden');
          liveAudio.src = '';
          visualizer.stop();
        } else {
          liveAudio.src = currentSrc;
          liveAudio.classList.remove('hidden');
          liveVideo.src = '';
          liveVideo.classList.add('hidden');
          liveCanvas.classList.remove('hidden');
          visualizer.start();
        }
      }

      // 4. Visualizer Theme
      if (state.visualizerTheme) {
        visualizer.setTheme(state.visualizerTheme);
      }

      // 5. Volume
      const targetEl = currentType === 'video' ? liveVideo : liveAudio;
      if (state.volume !== undefined) {
        targetEl.volume = state.volume;
      }

      // 6. Play / Pause & Time Sync
      if (state.currentTime !== undefined && Math.abs(targetEl.currentTime - state.currentTime) > 0.5) {
        targetEl.currentTime = state.currentTime;
      }

      if (state.isPlaying) {
        if (targetEl.paused) {
          targetEl.play().catch(err => console.warn('[Live] Play error:', err));
        }
      } else {
        if (!targetEl.paused) {
          targetEl.pause();
        }
      }
    }
  });
});
