/* Predict-mode gate: turns passive watching into active guessing. Wraps a
 * StepPlayer's onStep so that when predict mode is on and playback is about
 * to reveal a NEW step (never one already seen) that carries a `predict`
 * prompt, the player pauses and the DOM asks the question first - the real
 * render only happens once the user answers, then playback resumes if it
 * was running. Scrubbing/stepping back through already-revealed steps is
 * never gated, so replaying the timeline stays instant.
 *
 * The gate is created once per page load and `.attach(player)` is called
 * again every time app.js builds a new StepPlayer (each "Run"), so the
 * enabled/score state persists across runs while the gating logic re-wraps
 * whatever the current player's onStep chain is (bindControls et al). */
function createPredictGate({ panelEl, questionEl, optionsEl, feedbackEl, scoreEl, toggleEl }) {
  const state = { enabled: false, correct: 0, total: 0 };

  function updateScoreDisplay() {
    scoreEl.textContent = state.total ? `Predictions: ${state.correct}/${state.total}` : '';
  }

  function setEnabled(enabled) {
    state.enabled = enabled;
    toggleEl.classList.toggle('active', enabled);
    toggleEl.textContent = enabled ? '🎮 Predict Mode: On' : '🎮 Predict Mode: Off';
    panelEl.hidden = true;
  }

  toggleEl.addEventListener('click', () => setEnabled(!state.enabled));
  setEnabled(false);

  function renderPrompt(predict, onResolve) {
    panelEl.hidden = false;
    questionEl.textContent = predict.question;
    feedbackEl.textContent = '';
    optionsEl.innerHTML = '';

    predict.options.forEach((option) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'predict-option';
      btn.textContent = option;
      btn.addEventListener('click', () => {
        const correct = option === predict.answer;
        state.total += 1;
        if (correct) state.correct += 1;
        updateScoreDisplay();

        [...optionsEl.children].forEach((b) => {
          b.disabled = true;
          if (b.textContent === predict.answer) b.classList.add('predict-correct');
        });
        if (!correct) btn.classList.add('predict-wrong');
        feedbackEl.textContent = correct ? '✅ Correct!' : `❌ Not quite — it was "${predict.answer}".`;

        setTimeout(() => {
          panelEl.hidden = true;
          onResolve();
        }, 1100);
      });
      optionsEl.appendChild(btn);
    });
  }

  function attach(player) {
    let maxRevealed = -1;
    const nextOnStep = player.onStep;

    player.onStep = (step, index) => {
      if (state.enabled && step.predict && index > maxRevealed) {
        const wasPlaying = player.isPlaying;
        player.pause();
        renderPrompt(step.predict, () => {
          maxRevealed = index;
          nextOnStep(step, index);
          if (wasPlaying) player.play();
        });
      } else {
        maxRevealed = Math.max(maxRevealed, index);
        nextOnStep(step, index);
      }
    };
  }

  return { attach };
}

window.createPredictGate = createPredictGate;
