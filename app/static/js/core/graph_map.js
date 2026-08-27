/* Homepage graph map - pans/zooms, draws prerequisite edges, and locks
 * topics until their requirements are done. Reads every topic from the
 * hidden #topic-data block in base.html (single source of truth, same
 * technique command_palette.js already used) rather than a duplicated JS
 * array - layout (x/y) is computed here from that same data, not hardcoded,
 * so it can never drift from topics.yaml.
 */
(function () {
  const dataRoot = document.getElementById('topic-data');
  const svg = document.getElementById('graphSvg');
  if (!dataRoot || !svg) return;

  const COMPLEXITY_LABEL = {
    root: 'Core Concept', '1': 'O(1)', logn: 'O(log n)', n: 'O(n)',
    nlogn: 'O(n log n)', n2: 'O(n²)', exp: 'Exponential',
  };

  /* ---------------- parse + layout ---------------- */

  // The sr-only " - completed" span inside each entry is hidden via the
  // `hidden` attribute (toggled by progress.js), which does NOT remove it
  // from .textContent - read it raw and every title picks up that suffix
  // regardless of actual status. Clone and strip it first.
  function titleOf(el) {
    const clone = el.cloneNode(true);
    clone.querySelectorAll('.sr-only').forEach((n) => n.remove());
    return clone.textContent.trim().replace(/\s+/g, ' ');
  }

  function parseNodes() {
    return [...dataRoot.querySelectorAll('.nav-topic[data-progress-slug]')].map((el) => ({
      slug: el.dataset.progressSlug,
      title: titleOf(el),
      category: el.dataset.category || '',
      complexity: el.dataset.complexity || 'root',
      requires: el.dataset.requires ? el.dataset.requires.split(',').filter(Boolean) : [],
      blurb: el.dataset.blurb || '',
      href: el.getAttribute('href'),
      isCurrent: el.hasAttribute('aria-current'),
    }));
  }

  function computeLayout(nodes) {
    const bySlug = new Map(nodes.map((n) => [n.slug, n]));

    // Depth = longest path from a root (empty requires) - memoized DFS.
    const depthCache = new Map();
    function depthOf(slug, seen) {
      if (depthCache.has(slug)) return depthCache.get(slug);
      if (seen.has(slug)) return 0; // malformed cycle guard, shouldn't happen
      seen.add(slug);
      const node = bySlug.get(slug);
      const reqs = node ? node.requires : [];
      const d = reqs.length ? 1 + Math.max(...reqs.map((r) => depthOf(r, seen))) : 0;
      depthCache.set(slug, d);
      return d;
    }
    nodes.forEach((n) => { n.depth = depthOf(n.slug, new Set()); });

    // Lane = first-seen order of each category in the DOM (already matches
    // topics.yaml's category order, since that's how #topic-data was built).
    const laneOf = new Map();
    nodes.forEach((n) => {
      if (!laneOf.has(n.category)) laneOf.set(n.category, laneOf.size);
    });
    const laneCount = Math.max(laneOf.size, 1);

    const X_SPACING = 210;
    const X_OFFSET = 110;
    const Y_SPACING = 1240 / (laneCount + 1);

    // Nodes sharing the same (depth, category) would land on the exact same
    // point - spread them with a vertical jitter around their lane, wide
    // enough to actually clear the largest node's diameter (a root node's
    // r=34, so two full circles need >=68px center-to-center or their hit
    // areas overlap and steal clicks from each other).
    const groups = new Map();
    nodes.forEach((n) => {
      const key = `${n.depth}|${n.category}`;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(n);
    });
    groups.forEach((group) => {
      const spread = 84;
      group.forEach((n, i) => {
        const offset = (i - (group.length - 1) / 2) * spread;
        n.x = X_OFFSET + n.depth * X_SPACING;
        n.y = 60 + (laneOf.get(n.category) + 1) * Y_SPACING + offset;
      });
    });

    return nodes;
  }

  function computeStatus(nodes) {
    const progress = window.dsaProgress;
    const isComplete = progress ? progress.isComplete : () => false;
    nodes.forEach((n) => {
      if (isComplete(n.slug)) {
        n.status = 'done';
      } else if (n.requires.every((r) => isComplete(r))) {
        n.status = 'current';
      } else {
        n.status = 'locked';
      }
    });
    return nodes;
  }

  const nodes = computeStatus(computeLayout(parseNodes()));
  const bySlug = new Map(nodes.map((n) => [n.slug, n]));

  function edgeList() {
    const list = [];
    nodes.forEach((n) => n.requires.forEach((r) => { if (bySlug.has(r)) list.push([r, n.slug]); }));
    return list;
  }
  const edges = edgeList();

  /* ---------------- render ---------------- */

  const edgesLayer = document.getElementById('edgesLayer');
  const nodesLayer = document.getElementById('nodesLayer');

  function bezierPath(a, b) {
    const midX = (a.x + b.x) / 2;
    return `M ${a.x} ${a.y} C ${midX} ${a.y}, ${midX} ${b.y}, ${b.x} ${b.y}`;
  }

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const sortedEdges = [...edges].sort((e1, e2) => bySlug.get(e1[0]).x - bySlug.get(e2[0]).x);
  sortedEdges.forEach(([fromSlug, toSlug], i) => {
    const a = bySlug.get(fromSlug);
    const b = bySlug.get(toSlug);
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', bezierPath(a, b));
    path.setAttribute('class', 'edge' + (b.status === 'locked' ? ' locked' : ''));
    path.dataset.from = fromSlug;
    path.dataset.to = toSlug;
    edgesLayer.appendChild(path);

    if (reduceMotion) return;
    const len = path.getTotalLength();
    path.style.strokeDasharray = String(len);
    path.style.strokeDashoffset = String(len);
    path.style.transition = `stroke-dashoffset .9s cubic-bezier(.3,.7,.2,1) ${i * 18}ms, stroke .25s ease, opacity .25s ease, stroke-width .25s ease`;
    requestAnimationFrame(() => { path.style.strokeDashoffset = '0'; });
  });

  const sortedNodes = [...nodes].sort((a, b) => a.x - b.x);
  sortedNodes.forEach((n, i) => {
    const r = n.depth === 0 ? 34 : 26;
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.setAttribute('class', `node-group ${n.status}`);
    g.dataset.slug = n.slug;
    g.setAttribute('tabindex', '0');
    g.setAttribute('role', 'button');
    g.setAttribute('aria-label', `${n.title}, ${n.status}, ${COMPLEXITY_LABEL[n.complexity] || ''}`);
    if (!reduceMotion) {
      g.style.animation = `pop-in .5s cubic-bezier(.34,1.4,.4,1) both`;
      g.style.animationDelay = `${i * 28}ms`;
    }
    g.style.transformOrigin = `${n.x}px ${n.y}px`;

    const colorVar = `var(--c-${n.complexity})`;

    const halo = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    halo.setAttribute('class', 'halo');
    halo.setAttribute('cx', n.x); halo.setAttribute('cy', n.y); halo.setAttribute('r', r + 6);
    halo.setAttribute('fill', colorVar);
    halo.setAttribute('opacity', n.status === 'locked' ? 0.05 : n.status === 'done' ? 0.22 : 0.15);

    const core = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    core.setAttribute('class', 'core');
    core.setAttribute('cx', n.x); core.setAttribute('cy', n.y); core.setAttribute('r', r);
    core.setAttribute('fill', n.status === 'done' ? colorVar : n.status === 'current' ? 'rgba(16,25,42,0.9)' : '#0d1420');

    const ring = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    ring.setAttribute('class', 'ring');
    ring.setAttribute('cx', n.x); ring.setAttribute('cy', n.y); ring.setAttribute('r', r);
    ring.setAttribute('stroke', n.status === 'locked' ? 'rgba(255,255,255,0.12)' : colorVar);
    ring.setAttribute('stroke-width', n.status === 'current' ? 2.5 : 2);

    g.appendChild(halo); g.appendChild(core); g.appendChild(ring);

    if (n.status === 'done') {
      const check = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      check.setAttribute('x', n.x); check.setAttribute('y', n.y + 5);
      check.setAttribute('text-anchor', 'middle');
      check.setAttribute('font-size', '15');
      check.setAttribute('fill', '#0a1420');
      check.textContent = '✓';
      g.appendChild(check);
    } else if (n.status === 'locked') {
      const lock = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      lock.setAttribute('x', n.x); lock.setAttribute('y', n.y + 4);
      lock.setAttribute('text-anchor', 'middle');
      lock.setAttribute('font-size', '11');
      lock.setAttribute('fill', 'var(--ink-dim)');
      lock.textContent = '\u{1F512}';
      g.appendChild(lock);
    } else {
      const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      dot.setAttribute('cx', n.x); dot.setAttribute('cy', n.y); dot.setAttribute('r', 4);
      dot.setAttribute('fill', colorVar);
      g.appendChild(dot);
    }

    const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    label.setAttribute('class', 'node-label');
    label.setAttribute('x', n.x); label.setAttribute('y', n.y + r + 18);
    label.setAttribute('font-size', '12.5');
    label.textContent = n.title;
    g.appendChild(label);

    const sub = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    sub.setAttribute('class', 'node-sub');
    sub.setAttribute('x', n.x); sub.setAttribute('y', n.y + r + 32);
    sub.setAttribute('fill', n.status === 'locked' ? 'var(--ink-dim)' : colorVar);
    sub.textContent = COMPLEXITY_LABEL[n.complexity] || '';
    g.appendChild(sub);

    g.addEventListener('click', () => openPanel(n.slug));
    g.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); openPanel(n.slug); }
    });
    g.addEventListener('mouseenter', () => highlightNeighbors(n.slug, true));
    g.addEventListener('mouseleave', () => highlightNeighbors(n.slug, false));

    nodesLayer.appendChild(g);
  });

  function highlightNeighbors(slug, on) {
    document.querySelectorAll('.edge').forEach((e) => {
      const connected = e.dataset.from === slug || e.dataset.to === slug;
      e.classList.toggle('lit', on && connected);
    });
  }

  /* ---------------- detail panel ---------------- */

  const panel = document.getElementById('detailPanel');
  const panelClose = document.getElementById('panelClose');
  let panelLastFocused = null;

  function getPanelFocusable() {
    return [...panel.querySelectorAll('button, a[href]')].filter((el) => !el.disabled);
  }

  function openPanel(slug) {
    const n = bySlug.get(slug);
    if (!n) return;
    panelLastFocused = document.activeElement;

    document.getElementById('panelCrumb').textContent = `dsa / ${n.category.toLowerCase().replace(/[^a-z0-9]+/g, '_')} / ${n.slug}`;
    document.getElementById('panelTag').textContent = n.category;
    document.getElementById('panelTitle').textContent = n.title;

    const compEl = document.getElementById('panelComplexity');
    compEl.style.borderColor = `color-mix(in srgb, var(--c-${n.complexity}) 45%, transparent)`;
    compEl.style.color = `var(--c-${n.complexity})`;
    compEl.querySelector('.dot').style.background = `var(--c-${n.complexity})`;
    document.getElementById('panelComplexityText').textContent = COMPLEXITY_LABEL[n.complexity] || '';

    document.getElementById('panelBlurb').textContent = n.blurb;

    const prereqBox = document.getElementById('prereqBox');
    const prereqList = document.getElementById('prereqList');
    const cta = document.getElementById('panelCta');

    if (n.status === 'locked') {
      prereqBox.hidden = false;
      prereqList.innerHTML = '';
      n.requires.forEach((r) => {
        const reqNode = bySlug.get(r);
        const item = document.createElement('div');
        item.className = 'prereq-item';
        const pip = document.createElement('span');
        pip.className = 'pip';
        if (reqNode) pip.style.background = window.dsaProgress && window.dsaProgress.isComplete(r) ? `var(--c-${reqNode.complexity})` : '';
        const text = document.createElement('span');
        text.textContent = reqNode ? reqNode.title : r;
        item.appendChild(pip);
        item.appendChild(text);
        prereqList.appendChild(item);
      });
      cta.textContent = '\u{1F512} Locked — complete prerequisites first';
      cta.className = 'panel-cta locked-cta';
      cta.removeAttribute('href');
      cta.setAttribute('aria-disabled', 'true');
    } else {
      prereqBox.hidden = true;
      if (n.status === 'done') {
        cta.textContent = '✓ Completed — review again →';
        cta.className = 'panel-cta done-cta';
      } else {
        cta.textContent = 'Start topic →';
        cta.className = 'panel-cta ready';
      }
      cta.setAttribute('href', n.href);
      cta.removeAttribute('aria-disabled');
    }

    panel.classList.add('open');
    requestAnimationFrame(() => panelClose.focus());
  }

  function closePanel() {
    panel.classList.remove('open');
    if (panelLastFocused && document.contains(panelLastFocused)) panelLastFocused.focus();
    panelLastFocused = null;
  }
  panelClose.addEventListener('click', closePanel);
  panel.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') { event.preventDefault(); closePanel(); return; }
    if (event.key !== 'Tab') return;
    const focusable = getPanelFocusable();
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });

  /* ---------------- search + legend filter ---------------- */

  const searchInput = document.getElementById('graph-search');
  let activeComplexity = null;

  function applyFilter() {
    const q = searchInput.value.trim().toLowerCase();
    document.querySelectorAll('.node-group').forEach((g) => {
      const n = bySlug.get(g.dataset.slug);
      const matchesComplexity = !activeComplexity || n.complexity === activeComplexity;
      const matchesSearch = !q || n.title.toLowerCase().includes(q) || n.category.toLowerCase().includes(q);
      g.classList.toggle('dimmed', !(matchesComplexity && matchesSearch));
    });
    document.querySelectorAll('.edge').forEach((e) => {
      const a = bySlug.get(e.dataset.from);
      const b = bySlug.get(e.dataset.to);
      const matchesComplexity = !activeComplexity || a.complexity === activeComplexity || b.complexity === activeComplexity;
      const matchesSearch = !q || a.title.toLowerCase().includes(q) || b.title.toLowerCase().includes(q);
      e.classList.toggle('dimmed', !(matchesComplexity && matchesSearch));
    });
  }
  searchInput.addEventListener('input', applyFilter);

  document.querySelectorAll('#legend button').forEach((btn) => {
    btn.addEventListener('click', () => {
      const key = btn.dataset.complexity;
      activeComplexity = activeComplexity === key ? null : key;
      document.querySelectorAll('#legend button').forEach((b) => b.classList.toggle('active', b === btn && activeComplexity));
      applyFilter();
    });
  });

  /* ---------------- pan + zoom ---------------- */

  const graphWrap = document.getElementById('graphWrap');
  const viewport = document.getElementById('viewport');
  let scale = 0.82, tx = 40, ty = 20, isDragging = false, lastX, lastY, dragMoved = false;

  function applyTransform() {
    viewport.setAttribute('transform', `translate(${tx},${ty}) scale(${scale})`);
  }
  applyTransform();

  graphWrap.addEventListener('pointerdown', (e) => {
    isDragging = true; dragMoved = false; lastX = e.clientX; lastY = e.clientY;
    graphWrap.classList.add('dragging');
  });
  window.addEventListener('pointermove', (e) => {
    if (!isDragging) return;
    tx += e.clientX - lastX; ty += e.clientY - lastY;
    if (Math.abs(e.clientX - lastX) > 2 || Math.abs(e.clientY - lastY) > 2) dragMoved = true;
    lastX = e.clientX; lastY = e.clientY;
    applyTransform();
  });
  window.addEventListener('pointerup', () => { isDragging = false; graphWrap.classList.remove('dragging'); });

  graphWrap.addEventListener('wheel', (e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.08 : 0.08;
    scale = Math.min(2, Math.max(0.35, scale + delta));
    applyTransform();
  }, { passive: false });

  document.getElementById('zoomIn').addEventListener('click', () => { scale = Math.min(2, scale + 0.15); applyTransform(); });
  document.getElementById('zoomOut').addEventListener('click', () => { scale = Math.max(0.35, scale - 0.15); applyTransform(); });
  document.getElementById('zoomReset').addEventListener('click', () => { scale = 0.82; tx = 40; ty = 20; applyTransform(); });

  /* ---------------- Map / List toggle ---------------- */

  const tabMap = document.getElementById('tab-map');
  const tabList = document.getElementById('tab-list');
  const listView = document.getElementById('listView');

  function buildListView() {
    const cats = new Map();
    nodes.forEach((n) => {
      if (!cats.has(n.category)) cats.set(n.category, []);
      cats.get(n.category).push(n);
    });
    const listInner = document.getElementById('listInner');
    listInner.innerHTML = '';
    cats.forEach((items, cat) => {
      const section = document.createElement('div');
      section.className = 'list-cat';
      const h3 = document.createElement('h3');
      h3.textContent = cat;
      section.appendChild(h3);
      items.forEach((n) => {
        const row = document.createElement('div');
        row.className = `list-item ${n.status}`;
        row.dataset.slug = n.slug;
        const pip = document.createElement('span');
        pip.className = 'pip';
        pip.style.background = n.status === 'locked' ? 'var(--ink-dim)' : `var(--c-${n.complexity})`;
        const name = document.createElement('span');
        name.className = 'name';
        name.textContent = n.title;
        row.appendChild(pip);
        row.appendChild(name);
        if (n.status === 'locked') {
          const lockMini = document.createElement('span');
          lockMini.className = 'lock-mini';
          lockMini.textContent = '\u{1F512}';
          row.appendChild(lockMini);
        } else {
          const statusTxt = document.createElement('span');
          statusTxt.className = 'status-txt';
          statusTxt.textContent = n.status === 'done' ? 'done' : 'available';
          row.appendChild(statusTxt);
        }
        row.addEventListener('click', () => openPanel(n.slug));
        section.appendChild(row);
      });
      listInner.appendChild(section);
    });
  }
  buildListView();

  tabMap.addEventListener('click', () => {
    tabMap.classList.add('active'); tabMap.setAttribute('aria-pressed', 'true');
    tabList.classList.remove('active'); tabList.setAttribute('aria-pressed', 'false');
    listView.classList.remove('active'); graphWrap.classList.remove('hidden-view');
  });
  tabList.addEventListener('click', () => {
    tabList.classList.add('active'); tabList.setAttribute('aria-pressed', 'true');
    tabMap.classList.remove('active'); tabMap.setAttribute('aria-pressed', 'false');
    listView.classList.add('active'); graphWrap.classList.add('hidden-view');
  });
})();
