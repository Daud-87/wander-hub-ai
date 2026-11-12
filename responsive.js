/* Wander Hub AI - mobile menu. Adds a hamburger to any page header that has a nav. */
(function () {
  function init() {
    var headers = document.querySelectorAll('header');
    headers.forEach(function (h, idx) {
      var nav = h.querySelector('nav');
      if (!nav || h.querySelector('.wh-burger')) return;
      var links = nav.querySelectorAll('a');
      if (!links.length) return;

      nav.classList.add('wh-nav');
      if (getComputedStyle(h).position === 'static') h.style.position = 'relative';

      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'wh-burger';
      btn.setAttribute('aria-label', 'Open menu');
      btn.setAttribute('aria-expanded', 'false');
      btn.setAttribute('aria-controls', 'wh-menu-' + idx);
      btn.innerHTML = '&#9776;';

      var panel = document.createElement('div');
      panel.className = 'wh-menu';
      panel.id = 'wh-menu-' + idx;
      var here = location.pathname.split('/').pop() || 'landing.html';
      links.forEach(function (a) {
        var c = document.createElement('a');
        c.href = a.getAttribute('href');
        c.textContent = a.textContent.trim();
        if (c.getAttribute('href') === here) c.className = 'wh-current';
        panel.appendChild(c);
      });

      function setOpen(open) {
        panel.classList.toggle('open', open);
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        btn.innerHTML = open ? '&#10005;' : '&#9776;';
      }
      btn.addEventListener('click', function (e) { e.stopPropagation(); setOpen(!panel.classList.contains('open')); });
      document.addEventListener('click', function (e) { if (!h.contains(e.target)) setOpen(false); });
      document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setOpen(false); });
      window.addEventListener('resize', function () { if (window.innerWidth >= 1024) setOpen(false); });

      nav.parentNode.insertBefore(btn, nav);
      h.appendChild(panel);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
