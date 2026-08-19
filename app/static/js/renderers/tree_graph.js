/* D3-based renderers for the two node-link families: trees (createTreeRenderer)
 * and graphs (createGraphRenderer). Both are "dumb" renderers - all state
 * (including, for graphs, node position) is computed in Python and painted
 * as-is; see common.py's tree_step/graph_step docstrings for why. */

const NODE_STATE_COLOR_VAR = {
  new: '--viz-sorted',
  sorted: '--viz-sorted',
  frontier: '--viz-pivot',
  active: '--viz-compare',
  target: '--viz-swap',
  removed: '--viz-swap',
  default: '--viz-default',
};

const EDGE_STATE_COLOR_VAR = {
  tree: '--viz-sorted',
  default: '--baseline',
};

function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function nodeColor(state) {
  return cssVar(NODE_STATE_COLOR_VAR[state] || NODE_STATE_COLOR_VAR.default);
}

/* Tree-family renderer: builds a hierarchy straight from each node's `parent`
 * id (d3.stratify) and lays it out with d3.tree() every render - unlike a
 * graph, a tree's shape legitimately changes step to step, so recomputing
 * layout each time is correct (no jitter risk the way a force-directed graph
 * would have). The SVG uses a viewBox fit to the tree's bounding box, so it
 * scales crisply at any size without devicePixelRatio math.
 *
 * Nodes can form a FOREST (multiple `parent: null` roots at once, e.g.
 * Union-Find before everything merges into one set) - d3.stratify only
 * accepts a single root, so nodes are first grouped by which root they trace
 * back to, each group gets its own stratify+tree layout, and the resulting
 * subtrees are placed side by side. A single-root tree is just a forest of
 * size one, so this is also what BST/heap/trie use - no separate code path. */
function createTreeRenderer(container) {
  let svg = null;

  function ensureSvg() {
    if (!svg) {
      container.innerHTML = '';
      svg = d3.select(container).append('svg').attr('class', 'tree-svg');
    }
    return svg;
  }

  function groupByRoot(nodes) {
    const byId = new Map(nodes.map((n) => [n.id, n]));
    const rootIdCache = new Map();
    function rootIdOf(id) {
      if (rootIdCache.has(id)) return rootIdCache.get(id);
      const node = byId.get(id);
      const rootId = node.parent == null ? id : rootIdOf(node.parent);
      rootIdCache.set(id, rootId);
      return rootId;
    }
    const groups = new Map();
    nodes.forEach((n) => {
      const rootId = rootIdOf(n.id);
      if (!groups.has(rootId)) groups.set(rootId, []);
      groups.get(rootId).push(n);
    });
    return [...groups.values()];
  }

  function render(step) {
    const svgSel = ensureSvg();
    svgSel.selectAll('*').remove();

    if (!step.nodes.length) {
      svgSel.style('display', 'none');
      let empty = container.querySelector('.tree-empty');
      if (!empty) {
        empty = document.createElement('div');
        empty.className = 'tree-empty';
        empty.textContent = 'Empty';
        container.appendChild(empty);
      }
      return;
    }
    svgSel.style('display', 'block');
    const empty = container.querySelector('.tree-empty');
    if (empty) empty.remove();

    const dx = 56;
    const dy = 72;
    const gapX = 40;
    const roots = [];
    let offsetX = 0;
    groupByRoot(step.nodes).forEach((groupNodes) => {
      const root = d3.stratify().id((d) => d.id).parentId((d) => d.parent)(groupNodes);
      d3.tree().nodeSize([dx, dy])(root);

      let gx0 = Infinity;
      let gx1 = -Infinity;
      root.each((d) => {
        if (d.x < gx0) gx0 = d.x;
        if (d.x > gx1) gx1 = d.x;
      });
      const shift = offsetX - gx0;
      root.each((d) => {
        d.x += shift;
      });
      offsetX += gx1 - gx0 + gapX;
      roots.push(root);
    });

    let x0 = Infinity;
    let x1 = -Infinity;
    let y0 = Infinity;
    let y1 = -Infinity;
    roots.forEach((root) => {
      root.each((d) => {
        if (d.x < x0) x0 = d.x;
        if (d.x > x1) x1 = d.x;
        if (d.y < y0) y0 = d.y;
        if (d.y > y1) y1 = d.y;
      });
    });
    const padX = 36;
    const padY = 36;
    svgSel.attr('viewBox', `${x0 - padX} ${y0 - padY} ${x1 - x0 + padX * 2} ${y1 - y0 + padY * 2}`);

    const allLinks = roots.flatMap((root) => root.links());
    const allDescendants = roots.flatMap((root) => root.descendants());

    svgSel
      .append('g')
      .attr('fill', 'none')
      .attr('stroke', cssVar('--baseline'))
      .attr('stroke-width', 2)
      .selectAll('path')
      .data(allLinks)
      .join('path')
      .attr('d', d3.linkVertical().x((d) => d.x).y((d) => d.y));

    const nodeGroup = svgSel
      .append('g')
      .selectAll('g')
      .data(allDescendants)
      .join('g')
      .attr('transform', (d) => `translate(${d.x},${d.y})`);

    nodeGroup
      .append('circle')
      .attr('r', 18)
      .attr('fill', (d) => nodeColor(d.data.state));

    nodeGroup
      .append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.32em')
      .attr('fill', cssVar('--fill-ink'))
      .attr('font-size', '13px')
      .attr('font-weight', '600')
      .text((d) => d.data.value);
  }

  return { render, handleResize: () => {} };
}

/* Graph-family renderer: node x/y arrive frozen from Python (circular_layout)
 * and are never recomputed here - only `state` changes step to step, so
 * nothing jitters. Directed edges get an arrowhead via an SVG marker. */
function createGraphRenderer(container) {
  let svg = null;
  let defsAdded = false;

  function ensureSvg() {
    if (!svg) {
      container.innerHTML = '';
      svg = d3.select(container).append('svg').attr('class', 'tree-svg');
    }
    return svg;
  }

  function ensureArrowMarker(svgSel) {
    if (defsAdded) return;
    svgSel
      .append('defs')
      .append('marker')
      .attr('id', 'graph-arrow')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 10)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', cssVar('--baseline'));
    defsAdded = true;
  }

  // Directed edges get their line pulled back from the target's center to its
  // circle edge (+ a little extra) so the arrowhead marker lands beside the
  // node instead of being drawn underneath it.
  function pulledBackEndpoint(source, target, pullback) {
    const dx = target.x - source.x;
    const dy = target.y - source.y;
    const dist = Math.sqrt(dx * dx + dy * dy) || 1;
    return { x: target.x - (dx / dist) * pullback, y: target.y - (dy / dist) * pullback };
  }

  function render(step) {
    const svgSel = ensureSvg();
    svgSel.selectAll('*').remove();
    defsAdded = false;

    if (!step.nodes.length) {
      svgSel.style('display', 'none');
      return;
    }
    svgSel.style('display', 'block');
    ensureArrowMarker(svgSel);

    const byId = Object.fromEntries(step.nodes.map((n) => [n.id, n]));
    const padX = 36;
    const padY = 36;
    const xs = step.nodes.map((n) => n.x);
    const ys = step.nodes.map((n) => n.y);
    const x0 = Math.min(...xs) - padX;
    const x1 = Math.max(...xs) + padX;
    const y0 = Math.min(...ys) - padY;
    const y1 = Math.max(...ys) + padY;
    svgSel.attr('viewBox', `${x0} ${y0} ${x1 - x0} ${y1 - y0}`);

    svgSel
      .append('g')
      .selectAll('line')
      .data(step.edges)
      .join('line')
      .attr('x1', (d) => byId[d.source].x)
      .attr('y1', (d) => byId[d.source].y)
      .attr('x2', (d) => (d.directed ? pulledBackEndpoint(byId[d.source], byId[d.target], 24).x : byId[d.target].x))
      .attr('y2', (d) => (d.directed ? pulledBackEndpoint(byId[d.source], byId[d.target], 24).y : byId[d.target].y))
      .attr('stroke', (d) => cssVar(EDGE_STATE_COLOR_VAR[d.state] || EDGE_STATE_COLOR_VAR.default))
      .attr('stroke-width', (d) => (d.state === 'tree' ? 3 : 2))
      .attr('marker-end', (d) => (d.directed ? 'url(#graph-arrow)' : null));

    const nodeGroup = svgSel
      .append('g')
      .selectAll('g')
      .data(step.nodes)
      .join('g')
      .attr('transform', (d) => `translate(${d.x},${d.y})`);

    nodeGroup
      .append('circle')
      .attr('r', 18)
      .attr('fill', (d) => nodeColor(d.state));

    nodeGroup
      .append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.32em')
      .attr('fill', cssVar('--fill-ink'))
      .attr('font-size', '13px')
      .attr('font-weight', '600')
      .text((d) => d.value);
  }

  return { render, handleResize: () => {} };
}

window.createTreeRenderer = createTreeRenderer;
window.createGraphRenderer = createGraphRenderer;
