/* Native disclosures remain usable when this small enhancement is unavailable. */
(() => {
  const header = document.querySelector('.site-header');
  if (!header) return;
  const menu = header.querySelector('.site-menu');
  const trigger = menu.querySelector('.mobile-menu-toggle');
  const ninja = header.querySelector('.ninja-mega');
  const ninjaTrigger = ninja.querySelector('.ninja-mega-toggle');
  const groups = ninja.querySelectorAll('.ninja-mega-category');
  const desktop = window.matchMedia('(min-width: 1024px)');
  const expanded = (details, summary) => summary.setAttribute('aria-expanded', String(details.open));
  const sync = () => { expanded(menu, trigger); expanded(ninja, ninjaTrigger); };
  const layout = () => {
    const restoreFocus = !desktop.matches && menu.contains(document.activeElement);
    menu.open = desktop.matches;
    ninja.open = false;
    groups.forEach(group => { group.open = desktop.matches; });
    sync();
    if (restoreFocus) trigger.focus();
  };
  layout();
  desktop.addEventListener('change', layout);
  menu.addEventListener('toggle', sync);
  ninja.addEventListener('toggle', sync);
  header.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    if (ninja.open) {
      event.preventDefault();
      ninja.open = false;
      ninjaTrigger.focus();
    } else if (!desktop.matches && menu.open) {
      event.preventDefault();
      menu.open = false;
      trigger.focus();
    }
  });
  ninjaTrigger.addEventListener('keydown', event => {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      ninja.open = true;
      ninja.querySelector('a').focus();
    }
  });
  const close = () => { ninja.open = false; if (!desktop.matches) menu.open = false; sync(); };
  document.addEventListener('click', event => { if (!header.contains(event.target)) close(); });
  header.addEventListener('focusout', event => {
    if (event.relatedTarget && !header.contains(event.relatedTarget)) close();
  });
  ninja.addEventListener('focusout', event => {
    if (event.relatedTarget && !ninja.contains(event.relatedTarget)) ninja.open = false;
  });
  header.addEventListener('click', event => {
    const link = event.target.closest('a[href]');
    if (!link) return;
    close();
    const url = new URL(link.href);
    if (url.pathname === location.pathname && url.hash) {
      const target = document.getElementById(decodeURIComponent(url.hash.slice(1)));
      if (target) { target.setAttribute('tabindex', '-1'); target.focus({preventScroll:true}); }
    }
  });
})();
