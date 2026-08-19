/* Owns only the step timeline. Renderers/chrome plug in via callbacks and never
 * duplicate algorithm logic - they only render whatever step the player hands them. */
class StepPlayer {
  constructor({ steps, onStep, onEnd, onPlayStateChange, speedMs = 400 }) {
    this.steps = steps;
    this.onStep = onStep || (() => {});
    this.onEnd = onEnd || (() => {});
    this.onPlayStateChange = onPlayStateChange || (() => {});
    this.speedMs = speedMs;
    this.currentIndex = -1;
    this.timer = null;
    this.isPlaying = false;
  }

  get length() {
    return this.steps.length;
  }

  _emit(index) {
    this.currentIndex = index;
    const step = this.steps[index];
    if (step) this.onStep(step, index);
  }

  reset() {
    this.pause();
    this._emit(0);
  }

  seek(index) {
    const clamped = Math.max(0, Math.min(index, this.steps.length - 1));
    this._emit(clamped);
    if (clamped === this.steps.length - 1) {
      this.pause();
      this.onEnd();
    }
  }

  stepForward() {
    this.seek(this.currentIndex + 1);
  }

  stepBack() {
    this.pause();
    this.seek(this.currentIndex - 1);
  }

  play() {
    if (this.isPlaying) return;
    if (this.currentIndex >= this.steps.length - 1) this.currentIndex = -1;
    this.isPlaying = true;
    this.onPlayStateChange(true);
    this._tick();
  }

  _tick() {
    this.timer = setTimeout(() => {
      if (!this.isPlaying) return;
      const next = this.currentIndex + 1;
      this._emit(next);
      if (next >= this.steps.length - 1) {
        this.pause();
        this.onEnd();
        return;
      }
      this._tick();
    }, this.speedMs);
  }

  pause() {
    this.isPlaying = false;
    if (this.timer) clearTimeout(this.timer);
    this.timer = null;
    this.onPlayStateChange(false);
  }

  setSpeed(ms) {
    this.speedMs = ms;
  }
}

window.StepPlayer = StepPlayer;
