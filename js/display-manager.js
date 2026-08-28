/**
 * Smart Multi-Display / Screen Manager
 * Detects secondary monitors/projectors and launches clean Live Display automatically
 */
class DisplayManager {
  constructor() {
    this.liveWindowRef = null;
    this.screens = [];
    this.selectedScreen = null;
    this.hasScreenDetailsAPI = 'getScreenDetails' in window;
  }

  async init() {
    if (this.hasScreenDetailsAPI) {
      try {
        const screenDetails = await window.getScreenDetails();
        this.screens = screenDetails.screens;
        this.screens.forEach((s, idx) => {
          if (!s.isPrimary && !this.selectedScreen) {
            this.selectedScreen = s; // Default to first secondary screen (projector)
          }
        });
        if (!this.selectedScreen && this.screens.length > 0) {
          this.selectedScreen = this.screens[0];
        }

        screenDetails.addEventListener('screenschange', () => {
          this.screens = screenDetails.screens;
          console.log('[DisplayManager] Screens updated:', this.screens);
        });
      } catch (err) {
        console.warn('[DisplayManager] Screen details permission or API issue:', err);
      }
    }
  }

  async openLiveWindow(options = {}) {
    // If window is already open and not closed, bring to front
    if (this.liveWindowRef && !this.liveWindowRef.closed) {
      this.liveWindowRef.focus();
      return this.liveWindowRef;
    }

    const liveUrl = window.location.origin + window.location.pathname.replace(/index\.html$/, '') + 'live.html';
    
    let windowFeatures = 'menubar=no,toolbar=no,location=no,status=no,resizable=yes,scrollbars=no';

    // Attempt multi-screen positioning
    if (this.hasScreenDetailsAPI) {
      try {
        const screenDetails = await window.getScreenDetails();
        const secondary = screenDetails.screens.find(s => !s.isPrimary) || screenDetails.screens[0];
        
        if (secondary) {
          windowFeatures += `,left=${secondary.availLeft},top=${secondary.availTop},width=${secondary.availWidth},height=${secondary.availHeight}`;
        }
      } catch (e) {
        console.log('[DisplayManager] Falling back to standard dual screen coords', e);
        const left = window.screen.width; // Offset to next monitor
        windowFeatures += `,left=${left},top=0,width=1920,height=1080`;
      }
    } else {
      // Fallback: estimate secondary monitor position (typically to the right or left of primary)
      const left = window.screen.availWidth;
      windowFeatures += `,left=${left},top=0,width=1280,height=720`;
    }

    this.liveWindowRef = window.open(liveUrl, 'ChurchLiveDisplayWindow', windowFeatures);

    if (this.liveWindowRef) {
      this.liveWindowRef.focus();
    } else {
      alert('팝업 차단이 감지되었습니다. 브라우저 주소창 우측에서 팝업을 허용해주세요!');
    }

    return this.liveWindowRef;
  }

  closeLiveWindow() {
    if (this.liveWindowRef && !this.liveWindowRef.closed) {
      this.liveWindowRef.close();
      this.liveWindowRef = null;
    }
  }

  isLiveWindowOpen() {
    return this.liveWindowRef && !this.liveWindowRef.closed;
  }
}

window.DisplayManager = DisplayManager;
