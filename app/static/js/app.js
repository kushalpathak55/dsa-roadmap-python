(function () {
  const section = document.querySelector('.visualizer');
  if (!section) return;

  const algoKey = section.dataset.algoKey;
  const family = section.dataset.family;
  const topicSlug = section.dataset.topicSlug;
  const needsTarget = section.dataset.needsTarget === 'true';
  const needsK = section.dataset.needsK === 'true';

  const btnRun = document.getElementById('btn-run');
  const note = document.getElementById('note');
  const stage = document.getElementById('stage');

  const RENDERER_FACTORIES = {
    array: () => createBarsRenderer(stage),
    list: () => createListRenderer(stage),
    hash: () => createHashTableRenderer(stage),
    tree: () => createTreeRenderer(stage),
    graph: () => createGraphRenderer(stage),
    dp: () => createDPGridRenderer(stage),
  };

  let buildPayload;

  if (family === 'graph') {
    const edgesInput = document.getElementById('edges-input');
    const startInput = document.getElementById('start-input');
    buildPayload = () => {
      const edges = edgesInput.value.trim();
      if (!edges) throw new Error('Enter at least one edge.');
      const payload = { edges };
      if (startInput) {
        const start = startInput.value.trim();
        if (!start) throw new Error('Enter a start node.');
        payload.start = start;
      }
      return payload;
    };
  } else if (family === 'dp') {
    function parseIntList(text, fieldName) {
      const values = text
        .split(',')
        .map((piece) => piece.trim())
        .filter((piece) => piece.length > 0)
        .map((piece) => {
          const n = Number(piece);
          if (!Number.isInteger(n)) throw new Error(`${fieldName}: "${piece}" is not an integer`);
          return n;
        });
      if (values.length === 0) throw new Error(`Enter at least one value for ${fieldName}.`);
      return values;
    }

    if (algoKey === 'fibonacci_memo' || algoKey === 'n_queens') {
      const nInput = document.getElementById('n-input');
      buildPayload = () => ({ n: Number(nInput.value) });
    } else if (algoKey === 'knapsack') {
      const capacityInput = document.getElementById('capacity-input');
      const weightsInput = document.getElementById('weights-input');
      const valuesInput = document.getElementById('values-input');
      buildPayload = () => ({
        capacity: Number(capacityInput.value),
        weights: parseIntList(weightsInput.value, 'weights'),
        values: parseIntList(valuesInput.value, 'values'),
      });
    } else if (algoKey === 'lcs') {
      const aInput = document.getElementById('a-input');
      const bInput = document.getElementById('b-input');
      buildPayload = () => {
        const a = aInput.value.trim();
        const b = bInput.value.trim();
        if (!a || !b) throw new Error('Enter both strings.');
        return { a, b };
      };
    }
  } else if (algoKey === 'trie_demo') {
    const wordsInput = document.getElementById('words-input');
    buildPayload = () => {
      const words = wordsInput.value
        .split(',')
        .map((piece) => piece.trim())
        .filter((piece) => piece.length > 0);
      if (words.length === 0) throw new Error('Enter at least one word.');
      return { words };
    };
  } else if (algoKey === 'union_find_demo') {
    const edgesInput = document.getElementById('edges-input');
    buildPayload = () => {
      const edges = edgesInput.value.trim();
      if (!edges) throw new Error('Enter at least one union operation.');
      return { edges };
    };
  } else {
    const arrayInput = document.getElementById('array-input');
    const targetInput = document.getElementById('target-input');
    const targetField = section.querySelector('.target-field');
    const kInput = document.getElementById('k-input');
    const kField = section.querySelector('.k-field');
    const btnRandomize = document.getElementById('btn-randomize');

    if (needsTarget) targetField.style.display = '';
    if (needsK) kField.style.display = '';

    function parseArray(text) {
      return text
        .split(',')
        .map((piece) => piece.trim())
        .filter((piece) => piece.length > 0)
        .map((piece) => {
          const n = Number(piece);
          if (!Number.isFinite(n)) throw new Error(`"${piece}" is not a number`);
          return Math.trunc(n);
        });
    }

    function randomArray(size = 10, max = 99) {
      return Array.from({ length: size }, () => Math.floor(Math.random() * max) + 1);
    }

    btnRandomize.addEventListener('click', () => {
      const arr = randomArray();
      arrayInput.value = arr.join(', ');
      if (needsTarget) targetInput.value = String(arr[Math.floor(Math.random() * arr.length)]);
      if (needsK) kInput.value = String(Math.min(Number(kInput.value) || 1, arr.length));
    });

    buildPayload = () => {
      const array = parseArray(arrayInput.value);
      if (array.length === 0) throw new Error('Enter at least one number.');
      const payload = { array };
      if (needsTarget) payload.target = Number(targetInput.value);
      if (needsK) payload.k = Number(kInput.value);
      return payload;
    };
  }

  const predictToggle = document.getElementById('predict-toggle');
  const predictGate = predictToggle
    ? createPredictGate({
        panelEl: document.getElementById('predict-panel'),
        questionEl: document.getElementById('predict-question'),
        optionsEl: document.getElementById('predict-options'),
        feedbackEl: document.getElementById('predict-feedback'),
        scoreEl: document.getElementById('predict-score'),
        toggleEl: predictToggle,
      })
    : null;

  let currentPlayer = null;
  let currentRenderer = null;

  // The canvas backing store is sized from its rendered CSS box (see bars.js),
  // so an orientation change or the sidebar reflowing at a breakpoint needs a
  // repaint - otherwise the bitmap stays stretched to the old box size.
  let resizeQueued = false;
  window.addEventListener('resize', () => {
    if (resizeQueued) return;
    resizeQueued = true;
    requestAnimationFrame(() => {
      resizeQueued = false;
      if (currentRenderer) currentRenderer.handleResize();
    });
  });
  window.addEventListener('orientationchange', () => {
    if (currentRenderer) currentRenderer.handleResize();
  });

  async function runAlgorithm() {
    let payload;
    try {
      payload = buildPayload();
    } catch (err) {
      note.textContent = `Invalid input: ${err.message}`;
      return;
    }

    btnRun.disabled = true;
    note.textContent = 'Running...';

    try {
      const response = await fetch(`/api/run/${algoKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.detail ? JSON.stringify(body.detail) : `HTTP ${response.status}`);
      }
      const data = await response.json();

      if (currentPlayer) currentPlayer.pause();
      currentRenderer = (RENDERER_FACTORIES[family] || RENDERER_FACTORIES.array)();
      currentPlayer = new StepPlayer({
        steps: data.steps,
        onStep: (step, index) => currentRenderer.render(step, index),
        onEnd: () => { if (window.dsaProgress) window.dsaProgress.markComplete(topicSlug); },
      });
      bindControls(currentPlayer);
      if (predictGate) predictGate.attach(currentPlayer);
      // Motion is the point of this page - start playing immediately rather
      // than waiting on an extra tap, whether this run came from the page
      // just loading (see the auto-run below) or the user pressing Run.
      currentPlayer.play();
    } catch (err) {
      note.textContent = `Error: ${err.message}`;
    } finally {
      btnRun.disabled = false;
    }
  }

  btnRun.addEventListener('click', runAlgorithm);

  // Auto-run once on load with whatever example values are pre-filled, so a
  // visitor sees the animation playing immediately instead of a blank stage.
  runAlgorithm();
})();
