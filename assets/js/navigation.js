/* Native disclosure navigation; ordinary links retain their browser behaviour. */
(() => {
  const menu = document.querySelector('.ninja-mega');
  if (!menu) return;
  const trigger = menu.querySelector('.ninja-mega-toggle');
  const groups = menu.querySelectorAll('.ninja-mega-category');
  const desktop = window.matchMedia('(min-width: 1024px)');
  const layout = () => groups.forEach(group => { group.open = desktop.matches; });
  layout();
  desktop.addEventListener('change', layout);
  menu.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu.open) {
      event.preventDefault();
      menu.open = false;
      trigger.focus();
    }
  });
  document.addEventListener('click', event => {
    if (menu.open && !menu.contains(event.target)) menu.open = false;
  });
  menu.addEventListener('focusout', event => {
    if (!menu.contains(event.relatedTarget)) menu.open = false;
  });
  menu.addEventListener('click', event => {
    if (event.target.closest('a[href]')) menu.open = false;
  });
})();
