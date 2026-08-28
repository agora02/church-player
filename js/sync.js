/**
 * Church Media Sync Protocol
 * Manages real-time 0-delay synchronization between Controller and Live Projector screens
 */
class MediaSync {
  constructor(isLiveWindow = false) {
    this.isLiveWindow = isLiveWindow;
    this.channelName = 'church_media_live_sync_channel';
    this.channel = new BroadcastChannel(this.channelName);
    this.listeners = new Set();
    this.lastState = this.getDefaultState();
    this.isLiveConnected = false;
    this.lastLivePing = 0;

    // Listen for messages
    this.channel.onmessage = (event) => {
      const { type, data, timestamp } = event.data;
      this.handleMessage(type, data, timestamp);
    };

    // Heartbeat mechanism
    if (this.isLiveWindow) {
      // Live window sends heartbeat every 1 second
      setInterval(() => {
        this.send('LIVE_HEARTBEAT', {
          windowLocation: window.location.href,
          screenInfo: {
            width: window.innerWidth,
            height: window.innerHeight,
            screenX: window.screenX,
            screenY: window.screenY
          }
        });
      }, 1000);

      // Report initial state request
      this.send('REQUEST_STATE', {});
    } else {
      // Controller checks live heartbeat
      setInterval(() => {
        const now = Date.now();
        const connected = now - this.lastLivePing < 2500;
        if (connected !== this.isLiveConnected) {
          this.isLiveConnected = connected;
          this.notify('LIVE_STATUS_CHANGE', { connected: this.isLiveConnected });
        }
      }, 1000);
    }
  }

  getDefaultState() {
    return {
      isPlaying: false,
      currentTime: 0,
      duration: 0,
      volume: 1.0,
      muted: false,
      playbackRate: 1.0,
      mediaType: 'video', // 'video' | 'audio'
      mediaSrc: '',
      mediaName: '',
      mediaThumbnail: '',
      
      // Live broadcast controls
      isBlackout: false,
      isLogo: false,
      customLogoUrl: '',
      fadeTransition: false,
      
      // Visualizer settings (for audio mode)
      visualizerTheme: 'bars', // 'bars' | 'wave' | 'particles' | 'ambient'
      visualizerColor: 'emerald', // 'cyan' | 'purple' | 'emerald' | 'sunset'
      backgroundTheme: 'gradient_holy', // 'dark' | 'gradient_holy' | 'stars' | 'motion_clouds'
      
      // Live Overlays
      countdownActive: false,
      countdownEndTime: 0,
      countdownTitle: '예배 시작까지',
      subtitleActive: false,
      subtitleText: '',
      subtitlePosition: 'bottom', // 'bottom' | 'center' | 'top'
      
      // Audio Ducking
      isDucked: false,
      duckFactor: 0.25 // 25% volume during speech
    };
  }

  send(type, data = {}) {
    this.channel.postMessage({
      type,
      data,
      timestamp: Date.now(),
      sender: this.isLiveWindow ? 'live' : 'controller'
    });
  }

  updateState(partialState) {
    this.lastState = { ...this.lastState, ...partialState };
    this.send('STATE_UPDATE', this.lastState);
  }

  handleMessage(type, data, timestamp) {
    if (type === 'STATE_UPDATE') {
      this.lastState = { ...this.lastState, ...data };
      this.notify('STATE_UPDATE', this.lastState);
    } else if (type === 'LIVE_HEARTBEAT') {
      this.lastLivePing = Date.now();
      if (!this.isLiveConnected) {
        this.isLiveConnected = true;
        this.notify('LIVE_STATUS_CHANGE', { connected: true, liveInfo: data });
      }
    } else if (type === 'REQUEST_STATE' && !this.isLiveWindow) {
      // Controller responds with full state
      this.send('STATE_UPDATE', this.lastState);
    } else {
      // Specific commands (PLAY, PAUSE, SEEK, DUCK, etc.)
      this.notify(type, data);
    }
  }

  subscribe(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  notify(type, data) {
    for (const listener of this.listeners) {
      try {
        listener(type, data);
      } catch (err) {
        console.error('Error in sync listener:', err);
      }
    }
  }
}

window.MediaSync = MediaSync;
