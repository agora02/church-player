/**
 * Live Display Screen Sync Receiver
 * High Precision 0-delay Synchronization with Dissolve Transitions
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
      // 1. Blackout Transition (Dissolve)
      if (state.isBlackout) {
        liveBlackout.classList.remove('hidden');
      } else {
        liveBlackout.classList.add('hidden');
      }

      // 2. Standby / Logo (Dissolve)
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

      // 5. Volume & Unmute for Primary Output
      const targetEl = currentType === 'video' ? liveVideo : liveAudio;
      targetEl.muted = false;
      if (state.volume !== undefined) {
        targetEl.volume = state.volume;
      }

      // 6. High-Precision Play / Pause & Time Sync (Threshold: 0.15s)
      if (state.currentTime !== undefined && Math.abs(targetEl.currentTime - state.currentTime) > 0.15) {
        targetEl.currentTime = state.currentTime;
      }

      if (state.isPlaying) {
        if (targetEl.paused) {
          targetEl.play().catch(err => console.warn('[Live] Autoplay sync notice:', err));
        }
      } else {
        if (!targetEl.paused) {
          targetEl.pause();
        }
      }
    }
  });
});
