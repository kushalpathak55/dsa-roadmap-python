/* Array-family renderer: draws a bar per array element on a Canvas, colored by
 * the state Python already computed (indices.compare/swap/pivot/sorted/found).
 * This renderer never re-derives algorithm state - it only paints what a step says. */
function createBarsRenderer(canvas) {
  const ctx = canvas.getContext('2d');
  let lastStep = null;

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function colorFor(i, indices) {
    if (indices.found === i) return cssVar('--viz-sorted');
    if (indices.sorted && indices.sorted.includes(i)) return cssVar('--viz-sorted');
    if (indices.swap && indices.swap.includes(i)) return cssVar('--viz-swap');
    if (indices.compare && indices.compare.includes(i)) return cssVar('--viz-compare');
    if (indices.pivot && indices.pivot.includes(i)) return cssVar('--viz-pivot');
    return cssVar('--viz-default');
  }

  // Backs the canvas with devicePixelRatio-many pixels (crisp on retina iOS
  // screens) while every drawing call below stays in CSS-pixel units - the
  // transform below does the scaling, so geometry math never needs a dpr term.
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

  function render(step) {
    lastStep = step;
    const { width, height } = syncBackingStore();
    const array = step.array;
    const indices = step.indices || {};
    const labelSpace = 18;
    const plotHeight = height - labelSpace;

    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = cssVar('--baseline');
    ctx.fillRect(0, plotHeight, width, 1);

    const n = array.length;
    if (n === 0) return;
    const maxVal = Math.max(...array, 1);
    const slotWidth = width / n;
    const gap = 2;

    array.forEach((value, i) => {
      const barHeight = Math.max((value / maxVal) * (plotHeight - 20), 2);
      const x = i * slotWidth + gap / 2;
      const barWidth = Math.max(slotWidth - gap, 1);
      const y = plotHeight - barHeight;
      const radius = Math.min(4, barWidth / 2);

      ctx.fillStyle = colorFor(i, indices);
      ctx.beginPath();
      ctx.moveTo(x, y + radius);
      ctx.arcTo(x, y, x + radius, y, radius);
      ctx.arcTo(x + barWidth, y, x + barWidth, y + radius, radius);
      ctx.lineTo(x + barWidth, plotHeight);
      ctx.lineTo(x, plotHeight);
      ctx.closePath();
      ctx.fill();

      if (slotWidth > 14) {
        ctx.fillStyle = cssVar('--text-secondary');
        ctx.font = '11px system-ui, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(String(value), x + barWidth / 2, height - 4);
      }
    });
  }

  function handleResize() {
    if (lastStep) render(lastStep);
  }

  return { render, handleResize };
}

window.createBarsRenderer = createBarsRenderer;
