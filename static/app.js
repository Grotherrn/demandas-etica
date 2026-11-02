'use strict';
// Progressive enhancement: forms still work when JavaScript is disabled.
const filter = window.location.search ? null : document.querySelector('.filters');
if (filter) {
  const search = filter.querySelector('[name=q]');
  const stage = filter.querySelector('[name=stage]');
  const rows = [...document.querySelectorAll('tbody tr[data-search]')];
  const status = document.querySelector('#filter-status');
  const empty = document.querySelector('#live-empty');
  const apply = () => {
    const term = search.value.trim().toLocaleLowerCase('pt-BR');
    let count = 0;
    for (const row of rows) {
      const show = row.dataset.search.toLocaleLowerCase('pt-BR').includes(term) && (!stage.value || row.dataset.stage === stage.value);
      row.hidden = !show;
      if (show) count++;
    }
    empty.hidden = count > 0;
    status.textContent = `${count} demanda(s) exibida(s). Filtro aplicado nesta página.`;
  };
  search.addEventListener('input', apply);
  stage.addEventListener('change', apply);
  filter.addEventListener('submit', event => { event.preventDefault(); apply(); });
  filter.querySelector('a').addEventListener('click', event => {
    event.preventDefault(); search.value = ''; stage.value = ''; apply();
  });
  apply();
}
const incidentStatus = document.querySelector('[name=status]');
if (incidentStatus) {
  const update = () => {
    for (const key of ['action', 'lesson']) {
      const field = document.querySelector(`[name=${key}]`);
      field.required = incidentStatus.value === 'Encerrado';
      field.setAttribute('aria-required', String(field.required));
    }
  };
  incidentStatus.addEventListener('change', update); update();
}
