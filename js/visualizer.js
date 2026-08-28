/**
 * Audio Visualizer Engine using Web Audio API & HTML5 Canvas
 */
class AudioVisualizer {
  constructor(canvasElement, audioElement) {
    this.canvas = canvasElement;
    this.ctx = canvasElement.getContext('2d');
    this.audio = audioElement;
    this.audioCtx = null;
    this.analyser = null;
    this.source = null;
    this.dataArray = null;
    this.animationId = null;
    this.theme = 'bars'; // 'bars' | 'wave' | 'particles' | 'ambient'
    this.colorTheme = 'cyan'; // 'cyan' | 'purple' | 'emerald' | 'sunset'
    this.particles = [];
    this.initParticles();
    this.isInitialized = false;

    // Handle canvas resizing
    this.resize();
    window.addEventListener('resize', () => this.resize());
  }

  resize() {
    if (!this.canvas) return;
    this.canvas.width = this.canvas.parentElement ? this.canvas.parentElement.clientWidth : window.innerWidth;
    this.canvas.height = this.canvas.parentElement ? this.canvas.parentElement.clientHeight : window.innerHeight;
  }

  initAudioContext() {
    if (this.isInitialized) return;
    try {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      this.audioCtx = new AudioContextClass();
      this.analyser = this.audioCtx.createAnalyser();
      this.analyser.fftSize = 256; // 128 data bins
      this.analyser.smoothingTimeConstant = 0.8;

      if (this.audio) {
        this.source = this.audioCtx.createMediaElementSource(this.audio);
        this.source.connect(this.analyser);
        this.analyser.connect(this.audioCtx.destination);
      }

      this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
      this.isInitialized = true;
    } catch (err) {
      console.warn('[Visualizer] Web Audio API init warning (user gesture may be needed):', err);
    }
  }

  initParticles() {
    this.particles = [];
    const count = 70;
    for (let i = 0; i < count; i++) {
      this.particles.push({
        x: Math.random(),
        y: Math.random(),
        radius: Math.random() * 3 + 1,
        vx: (Math.random() - 0.5) * 0.001,
        vy: (Math.random() - 0.5) * 0.001,
        alpha: Math.random() * 0.7 + 0.3,
        colorIndex: Math.random()
      });
    }
  }

  setTheme(theme) {
    this.theme = theme;
  }

  setColorTheme(color) {
    this.colorTheme = color;
  }

  start() {
    if (this.audioCtx && this.audioCtx.state === 'suspended') {
      this.audioCtx.resume();
    }
    if (!this.animationId) {
      this.render();
    }
  }

  stop() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
  }

  getColorStops() {
    switch (this.colorTheme) {
      case 'purple':
        return ['#a855f7', '#ec4899', '#6366f1'];
      case 'emerald':
        return ['#10b981', '#06b6d4', '#3b82f6'];
      case 'sunset':
        return ['#f59e0b', '#ef4444', '#ec4899'];
      case 'cyan':
      default:
        return ['#06b6d4', '#3b82f6', '#8b5cf6'];
    }
  }

  render() {
    this.animationId = requestAnimationFrame(() => this.render());
    if (!this.canvas || !this.ctx) return;

    const w = this.canvas.width;
    const h = this.canvas.height;

    // Clear canvas
    this.ctx.clearRect(0, 0, w, h);

    let hasAudioData = false;
    let avgFreq = 0;
    if (this.analyser && this.dataArray && (!this.audio || !this.audio.paused)) {
      this.analyser.getByteFrequencyData(this.dataArray);
      let sum = 0;
      for (let i = 0; i < this.dataArray.length; i++) {
        sum += this.dataArray[i];
      }
      avgFreq = sum / this.dataArray.length;
      hasAudioData = avgFreq > 0;
    }

    // Mock ambient animation if no audio playing
    const time = Date.now() * 0.002;

    switch (this.theme) {
      case 'bars':
        this.renderBars(w, h, hasAudioData, avgFreq, time);
        break;
      case 'wave':
        this.renderWave(w, h, hasAudioData, avgFreq, time);
        break;
      case 'particles':
        this.renderParticles(w, h, hasAudioData, avgFreq, time);
        break;
      case 'ambient':
      default:
        this.renderAmbient(w, h, hasAudioData, avgFreq, time);
        break;
    }
  }

  renderBars(w, h, hasAudio, avgFreq, time) {
    const ctx = this.ctx;
    const barCount = 48;
    const barWidth = (w / barCount) * 0.65;
    const gap = (w / barCount) * 0.35;
    const colors = this.getColorStops();

    const gradient = ctx.createLinearGradient(0, h, 0, h * 0.3);
    gradient.addColorStop(0, colors[0]);
    gradient.addColorStop(0.5, colors[1]);
    gradient.addColorStop(1, colors[2]);

    for (let i = 0; i < barCount; i++) {
      let val = 0;
      if (hasAudio) {
        const binIndex = Math.floor((i / barCount) * (this.dataArray.length * 0.75));
        val = this.dataArray[binIndex] / 255;
      } else {
        // Idle animation
        val = (Math.sin(time + i * 0.2) * 0.5 + 0.5) * 0.2 + 0.05;
      }

      const barHeight = Math.max(8, val * h * 0.55);
      const x = i * (barWidth + gap) + gap;
      const y = h - barHeight - 20;

      ctx.fillStyle = gradient;
      ctx.shadowColor = colors[1];
      ctx.shadowBlur = val > 0.4 ? 15 : 5;
      
      // Rounded bar top
      ctx.beginPath();
      ctx.roundRect(x, y, barWidth, barHeight, [4, 4, 0, 0]);
      ctx.fill();

      // Top highlight cap
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(x, y, barWidth, 3);
    }
    ctx.shadowBlur = 0;
  }

  renderWave(w, h, hasAudio, avgFreq, time) {
    const ctx = this.ctx;
    const colors = this.getColorStops();
    const midY = h * 0.6;

    ctx.save();
    for (let layer = 0; layer < 3; layer++) {
      ctx.beginPath();
      const points = 60;
      const alpha = 0.4 + layer * 0.25;

      for (let i = 0; i <= points; i++) {
        const x = (i / points) * w;
        let amp = (hasAudio ? (avgFreq / 255) * 120 : 30) * (1 + layer * 0.3);
        let freq = 0.02 + layer * 0.01;
        let y = midY + Math.sin(i * 0.15 + time * (1 + layer * 0.5)) * amp * Math.sin((i / points) * Math.PI);

        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }

      ctx.strokeStyle = colors[layer % colors.length];
      ctx.lineWidth = 3 + layer * 2;
      ctx.shadowColor = colors[layer % colors.length];
      ctx.shadowBlur = 20;
      ctx.globalAlpha = alpha;
      ctx.stroke();
    }
    ctx.restore();
  }

  renderParticles(w, h, hasAudio, avgFreq, time) {
    const ctx = this.ctx;
    const colors = this.getColorStops();
    const boost = hasAudio ? (avgFreq / 255) * 2.5 : 0.5;

    ctx.save();
    this.particles.forEach((p, idx) => {
      p.x += p.vx * (1 + boost);
      p.y += p.vy * (1 + boost);

      if (p.x < 0) p.x = 1;
      if (p.x > 1) p.x = 0;
      if (p.y < 0) p.y = 1;
      if (p.y > 1) p.y = 0;

      const px = p.x * w;
      const py = p.y * h;
      const radius = p.radius * (1 + (hasAudio ? (this.dataArray[idx % this.dataArray.length] / 255) * 1.5 : 0));

      ctx.beginPath();
      ctx.arc(px, py, radius, 0, Math.PI * 2);
      ctx.fillStyle = colors[Math.floor(p.colorIndex * colors.length)];
      ctx.shadowColor = colors[0];
      ctx.shadowBlur = 10 * boost;
      ctx.globalAlpha = p.alpha;
      ctx.fill();
    });
    ctx.restore();
  }

  renderAmbient(w, h, hasAudio, avgFreq, time) {
    const ctx = this.ctx;
    const colors = this.getColorStops();
    const centerX = w / 2;
    const centerY = h / 2;
    const baseRadius = Math.min(w, h) * 0.22;
    const pulse = hasAudio ? (avgFreq / 255) * 50 : Math.sin(time) * 15;

    const radGrad = ctx.createRadialGradient(
      centerX, centerY, baseRadius * 0.2,
      centerX, centerY, baseRadius + pulse + 80
    );
    radGrad.addColorStop(0, colors[0]);
    radGrad.addColorStop(0.5, colors[1]);
    radGrad.addColorStop(1, 'transparent');

    ctx.save();
    ctx.fillStyle = radGrad;
    ctx.beginPath();
    ctx.arc(centerX, centerY, baseRadius + pulse + 80, 0, Math.PI * 2);
    ctx.fill();

    // Inner glowing ring
    ctx.beginPath();
    ctx.arc(centerX, centerY, baseRadius + pulse * 0.5, 0, Math.PI * 2);
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 2;
    ctx.shadowColor = '#ffffff';
    ctx.shadowBlur = 20;
    ctx.globalAlpha = 0.8;
    ctx.stroke();
    ctx.restore();
  }
}

window.AudioVisualizer = AudioVisualizer;
