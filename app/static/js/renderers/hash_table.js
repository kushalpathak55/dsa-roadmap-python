/* Hash-family renderer: one row per bucket, each holding a small horizontal
 * chain of DOM boxes (reuses the same box/arrow visual language as
 * list_boxes.js). The active/just-touched bucket row is highlighted so a
 * collision (a bucket that already has a node when a new one lands) reads
 * clearly. Never re-derives hashing/collision logic - only paints the step. */
function createHashTableRenderer(container) {
  const STATE_COLOR_VAR = {
    new: '--viz-sorted',
    active: '--viz-compare',
    target: '--viz-swap',
    removed: '--viz-swap',
    default: '--viz-default',
  };

  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function render(step) {
    container.classList.add('hash-table');
    container.innerHTML = '';

    step.buckets.forEach((bucket) => {
      const row = document.createElement('div');
      row.className = 'hash-bucket-row';
      if (step.active_bucket === bucket.index) row.classList.add('active');

      const label = document.createElement('div');
      label.className = 'hash-bucket-label';
      label.textContent = `[${bucket.index}]`;
      row.appendChild(label);

      const chain = document.createElement('div');
      chain.className = 'hash-bucket-chain';

      if (bucket.nodes.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'hash-bucket-empty';
        empty.textContent = '—';
        chain.appendChild(empty);
      } else {
        bucket.nodes.forEach((node, i) => {
          const box = document.createElement('div');
          box.className = 'list-node-box list-node-box-small';
          box.style.background = cssVar(STATE_COLOR_VAR[node.state] || STATE_COLOR_VAR.default);
          box.textContent = node.value;
          chain.appendChild(box);

          if (i < bucket.nodes.length - 1) {
            const arrow = document.createElement('div');
            arrow.className = 'list-node-arrow';
            arrow.textContent = '→';
            chain.appendChild(arrow);
          }
        });
      }

      row.appendChild(chain);
      container.appendChild(row);
    });
  }

  return { render, handleResize: () => {} };
}

window.createHashTableRenderer = createHashTableRenderer;
