/* DP-family renderer: an HTML table, one cell per grid entry. Always 2D (even
 * fibonacci's single row), so this one renderer covers every DP topic - no
 * per-algorithm special casing. Cell color: green = the final answer (kind
 * "done" cursor), yellow = the cell currently being computed, violet = a
 * cell the current computation depends on, plain = everything else. */
function createDPGridRenderer(container) {
  function cssVar(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  }

  function render(step) {
    container.innerHTML = '';

    const table = document.createElement('table');
    table.className = 'dp-table';

    const highlightSet = new Set((step.highlight.cells || []).map(([r, c]) => `${r},${c}`));
    const cursor = step.cursor;

    if (step.col_labels.length) {
      const thead = document.createElement('thead');
      const headRow = document.createElement('tr');
      headRow.appendChild(document.createElement('th'));
      step.col_labels.forEach((label) => {
        const th = document.createElement('th');
        th.textContent = label;
        headRow.appendChild(th);
      });
      thead.appendChild(headRow);
      table.appendChild(thead);
    }

    const tbody = document.createElement('tbody');
    step.grid.forEach((row, r) => {
      const tr = document.createElement('tr');
      const rowHeader = document.createElement('th');
      rowHeader.textContent = step.row_labels[r] || '';
      tr.appendChild(rowHeader);

      row.forEach((value, c) => {
        const td = document.createElement('td');
        td.textContent = value === null || value === undefined ? '' : String(value);

        const isCursor = cursor && cursor.row === r && cursor.col === c;
        const isDependency = highlightSet.has(`${r},${c}`);
        if (isCursor && step.kind === 'done') {
          td.style.background = cssVar('--viz-sorted');
          td.style.color = cssVar('--fill-ink');
        } else if (isCursor) {
          td.style.background = cssVar('--viz-compare');
          td.style.color = cssVar('--fill-ink');
        } else if (isDependency) {
          td.style.background = cssVar('--viz-pivot');
          td.style.color = cssVar('--fill-ink');
        }
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);

    container.appendChild(table);
  }

  return { render, handleResize: () => {} };
}

window.createDPGridRenderer = createDPGridRenderer;
