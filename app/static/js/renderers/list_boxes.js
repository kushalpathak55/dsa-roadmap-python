/* List-family renderer: draws linked list / stack / queue nodes as DOM boxes,
 * colored by the state Python already computed. `step.layout` picks the
 * arrangement - "chain" (arrows, head/tail/current), "stack" (grows upward,
 * top), or "queue" (front/rear, no arrows). Never re-derives structure - only
 * paints what a step says. */
function createListRenderer(container) {
  const POINTER_LABELS = {
    head: 'head',
    tail: 'tail',
    top: 'top',
    front: 'front',
    rear: 'rear',
    current: 'current',
  };

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
    container.classList.remove('list-stage-chain', 'list-stage-stack', 'list-stage-queue');
    container.classList.add(`list-stage-${step.layout}`);
    container.innerHTML = '';

    if (!step.nodes.length) {
      const empty = document.createElement('div');
      empty.className = 'list-empty';
      empty.textContent = 'Empty';
      container.appendChild(empty);
      return;
    }

    const pointerMap = {};
    Object.entries(step.pointers || {}).forEach(([key, id]) => {
      if (!id) return;
      (pointerMap[id] = pointerMap[id] || []).push(POINTER_LABELS[key] || key);
    });

    step.nodes.forEach((node, i) => {
      const wrapper = document.createElement('div');
      wrapper.className = 'list-node-wrapper';

      const label = document.createElement('div');
      label.className = 'list-node-label';
      label.textContent = pointerMap[node.id] ? pointerMap[node.id].join(', ') : ' ';
      wrapper.appendChild(label);

      const box = document.createElement('div');
      box.className = 'list-node-box';
      box.style.background = cssVar(STATE_COLOR_VAR[node.state] || STATE_COLOR_VAR.default);
      box.textContent = node.value;
      wrapper.appendChild(box);

      container.appendChild(wrapper);

      if (step.layout === 'chain' && i < step.nodes.length - 1) {
        const arrow = document.createElement('div');
        arrow.className = 'list-node-arrow';
        arrow.textContent = '→';
        container.appendChild(arrow);
      }
    });
  }

  return { render, handleResize: () => {} };
}

window.createListRenderer = createListRenderer;
