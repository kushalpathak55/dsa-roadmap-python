/* Array-family renderer: draws a bar per array element on a Canvas, colored by
 * the state Python already computed (indices.compare/swap/pivot/sorted/found).
 * This renderer never re-derives algorithm state - it only paints what a step
 * says. Unlike a plain snapshot draw, bars animate BETWEEN steps (height
 * eases, an active state gets a brief spring "pop" + glow) via a persistent
 * requestAnimationFrame loop that starts on the first change and stops once
 * everything has settled - not a fixed idle loop burning battery forever. */
function createBarsRenderer(canvas) {
  const ctx = canvas.getContext('2d');
  let lastStep = null;
  let bars = []; // per-index animation state, positional (matches the old renderer's indexing)
  let rafId = null;

  const HEIGHT_MS = 260;
  const PULSE_MS = 420;
  const FOUND_PULSE_MS = 700;
  const ACTIVE_STATES = new Set(['compare', 'swap', 'pivot', 'found']);

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function stateFor(i, indices) {
    if (indices.found === i) return 'found';
    if (indices.sorted && indices.sorted.includes(i)) return 'sorted';
    if (indices.swap && indices.swap.includes(i)) return 'swap';
    if (indices.compare && indices.compare.includes(i)) return 'compare';
    if (indices.pivot && indices.pivot.includes(i)) return 'pivot';
    return 'default';
  }

  function baseColorFor(state) {
    if (state === 'found' || state === 'sorted') return cssVar('--viz-sorted');
    if (state === 'swap') return cssVar('--viz-swap');
    if (state === 'compare') return cssVar('--viz-compare');
    if (state === 'pivot') return cssVar('--viz-pivot');
    return cssVar('--viz-default');
  }

  function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  // A single smooth bump (0 at start/end, peak at the midpoint) - the "pop"
  // an active bar gets, layered on top of its normal height.
  function pulseAmount(t) {
    if (t >= 1) return 0;
    return Math.sin(t * Math.PI);
  }

  function lerp(a, b, t) {
    return a + (b - a) * t;
  }

  function syncBackingStore() {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    const cssWidth = Math.max(rect.width, 1);
    const cssHeight = Math.max(rect.height, 1);
    const targetWidth = Math.round(cssWidth * dpr);
    const targetHeight = Math.round(cssHeight * dpr);
    if (canvas.width !== targetWidth || canvas.height !== targetHeight) {
      canvas.width = targetWidth;
      canvas.height = targetHeight;
    }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { width: cssWidth, height: cssHeight };
  }

  function reconcile(array, indices, now) {
    array.forEach((value, i) => {
      const state = stateFor(i, indices);
      let bar = bars[i];
      if (!bar) {
        bar = bars[i] = {
          currentValue: value,
          fromValue: value,
          toValue: value,
          heightStart: now,
          state,
          pulseStart: ACTIVE_STATES.has(state) ? now : null,
          pulseMs: state === 'found' ? FOUND_PULSE_MS : PULSE_MS,
        };
        return;
      }
      if (bar.toValue !== value) {
        bar.fromValue = bar.currentValue;
        bar.toValue = value;
        bar.heightStart = now;
      }
      if (bar.state !== state) {
        bar.state = state;
        if (ACTIVE_STATES.has(state)) {
          bar.pulseStart = now;
          bar.pulseMs = state === 'found' ? FOUND_PULSE_MS : PULSE_MS;
        }
      }
    });
    bars.length = array.length;
  }

  function draw(now) {
    const { width, height } = syncBackingStore();
    const labelSpace = 18;
    const plotHeight = height - labelSpace;

    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = cssVar('--baseline');
    ctx.fillRect(0, plotHeight, width, 1);

    const n = bars.length;
    if (n === 0) return false;
    const maxVal = Math.max(...bars.map((b) => Math.max(b.currentValue, b.toValue)), 1);
    const slotWidth = width / n;
    const gap = 2;

    let stillAnimating = false;

    bars.forEach((bar, i) => {
      const heightT = Math.min(1, (now - bar.heightStart) / HEIGHT_MS);
      bar.currentValue = lerp(bar.fromValue, bar.toValue, easeOutCubic(heightT));
      if (heightT < 1) stillAnimating = true;

      let pulse = 0;
      if (bar.pulseStart !== null) {
        const pulseT = (now - bar.pulseStart) / bar.pulseMs;
        pulse = pulseAmount(pulseT);
        if (pulseT < 1) stillAnimating = true;
        else bar.pulseStart = null;
      }

      const baseHeight = Math.max((bar.currentValue / maxVal) * (plotHeight - 20), 2);
      const barHeight = baseHeight + pulse * (bar.state === 'found' ? 18 : 12);
      const scaleX = 1 + pulse * (bar.state === 'found' ? 0.16 : 0.1);

      const x = i * slotWidth + gap / 2;
      const barWidth = Math.max(slotWidth - gap, 1);
      const centerX = x + barWidth / 2;
      const y = plotHeight - barHeight;
      const radius = Math.min(4, (barWidth * scaleX) / 2);
      const color = baseColorFor(bar.state);
      const active = ACTIVE_STATES.has(bar.state) && pulse > 0.02;

      ctx.save();
      ctx.translate(centerX, plotHeight);
      ctx.scale(scaleX, 1);
      ctx.translate(-centerX, -plotHeight);

      const grad = ctx.createLinearGradient(0, y, 0, plotHeight);
      grad.addColorStop(0, `color-mix(in srgb, ${color} 65%, white)`);
      grad.addColorStop(1, color);
      ctx.fillStyle = grad;

      if (active) {
        ctx.shadowColor = `color-mix(in srgb, ${color} 55%, transparent)`;
        ctx.shadowBlur = 16 * pulse;
      } else {
        ctx.shadowBlur = 0;
      }

      ctx.beginPath();
      ctx.moveTo(x, y + radius);
      ctx.arcTo(x, y, x + barWidth, y, radius);
      ctx.arcTo(x + barWidth, y, x + barWidth, y + radius, radius);
      ctx.lineTo(x + barWidth, plotHeight);
      ctx.lineTo(x, plotHeight);
      ctx.closePath();
      ctx.fill();
      ctx.shadowBlur = 0;
      ctx.restore();

      if (slotWidth > 14) {
        ctx.fillStyle = active ? color : cssVar('--text-secondary');
        ctx.font = active ? `${11 + pulse * 2}px system-ui, sans-serif` : '11px system-ui, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(String(Math.round(bar.currentValue)), centerX, height - 4);
      }
    });

    return stillAnimating;
  }

  function loop() {
    const stillAnimating = draw(performance.now());
    if (stillAnimating) {
      rafId = requestAnimationFrame(loop);
    } else {
      rafId = null;
    }
  }

  function requestFrame() {
    if (rafId === null) rafId = requestAnimationFrame(loop);
  }

  function render(step) {
    lastStep = step;
    reconcile(step.array, step.indices || {}, performance.now());
    requestFrame();
  }

  function handleResize() {
    if (lastStep) draw(performance.now());
  }

  return { render, handleResize };
}

window.createBarsRenderer = createBarsRenderer;
