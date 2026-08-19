/* Generic chrome: play/pause/step/scrub/speed + note/counters. Works for any family
 * because those fields (note, counters) live in every step's common envelope. */
function bindControls(player) {
  const btnPlay = document.getElementById('btn-play');
  const btnBack = document.getElementById('btn-step-back');
  const btnForward = document.getElementById('btn-step-forward');
  const btnReset = document.getElementById('btn-reset');
  const scrub = document.getElementById('scrub');
  const scrubLabel = document.getElementById('scrub-label');
  const speed = document.getElementById('speed');
  const note = document.getElementById('note');
  const counters = document.getElementById('counters');

  scrub.max = Math.max(player.length - 1, 0);

  const originalOnStep = player.onStep;
  player.onStep = (step, index) => {
    originalOnStep(step, index);
    scrub.value = index;
    scrubLabel.textContent = `${index + 1} / ${player.length}`;
    note.textContent = step.note || '';
    counters.textContent = Object.entries(step.counters || {})
      .map(([key, value]) => `${key}: ${value}`)
      .join('   ');
  };

  player.onPlayStateChange = (isPlaying) => {
    btnPlay.textContent = isPlaying ? '⏸' : '▶';
    // Announce step notes to screen readers only while paused/stepping
    // manually (one user action -> one announcement) - autoplay firing
    // every ~400ms would otherwise spam a live region, a known anti-pattern
    // for fast-updating content.
    note.setAttribute('aria-live', isPlaying ? 'off' : 'polite');
  };
  const originalOnEnd = player.onEnd;
  player.onEnd = () => {
    originalOnEnd();
    btnPlay.textContent = '▶';
  };

  btnPlay.addEventListener('click', () => {
    player.isPlaying ? player.pause() : player.play();
  });
  btnBack.addEventListener('click', () => player.stepBack());
  btnForward.addEventListener('click', () => player.stepForward());
  btnReset.addEventListener('click', () => player.reset());
  scrub.addEventListener('input', () => {
    player.pause();
    player.seek(Number(scrub.value));
  });
  speed.addEventListener('input', () => player.setSpeed(Number(speed.value)));

  player.reset();
}

window.bindControls = bindControls;

/* Debugger-style keyboard shortcuts (space/arrows/home) - registered once at
 * script load, not inside bindControls, since a new StepPlayer is built on
 * every Run but the transport buttons are the same DOM nodes throughout, so
 * one listener that clicks whichever button is current works for every run
 * without stacking duplicate listeners. Skipped for genuine text-entry
 * targets (inputs/textareas/selects/contenteditable, including the scrub and
 * speed range sliders, which already use arrow keys natively) and, for
 * Space specifically, for a focused <button> (e.g. a predict-mode answer) so
 * its own native space-activates-click isn't double-fired by this handler. */
document.addEventListener('keydown', (event) => {
  const target = event.target;
  const tag = target && target.tagName;
  const isTextEntry = tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || (target && target.isContentEditable);
  if (isTextEntry) return;

  const btnPlay = document.getElementById('btn-play');
  if (!btnPlay) return;

  if (event.key === ' ' && tag === 'BUTTON') return;

  switch (event.key) {
    case ' ':
      event.preventDefault();
      btnPlay.click();
      break;
    case 'ArrowRight':
      event.preventDefault();
      document.getElementById('btn-step-forward').click();
      break;
    case 'ArrowLeft':
      event.preventDefault();
      document.getElementById('btn-step-back').click();
      break;
    case 'Home':
      event.preventDefault();
      document.getElementById('btn-reset').click();
      break;
  }
});
