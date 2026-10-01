(function () {
  'use strict';
  var root = document.documentElement;

  // Sticky header shadow + back-to-top button
  var header = document.querySelector('.site-header');
  var toTop = document.querySelector('.to-top');
  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    if (header) header.classList.toggle('scrolled', y > 8);
    if (toTop) toTop.classList.toggle('show', y > 700);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Mobile menu
  var btn = document.querySelector('.menu-btn');
  var nav = document.getElementById('nav');
  function setMenu(open) {
    root.classList.toggle('nav-open', open);
    if (btn) btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  if (btn && nav) {
    btn.addEventListener('click', function () { setMenu(!root.classList.contains('nav-open')); });
    nav.addEventListener('click', function (e) { if (e.target.tagName === 'A') setMenu(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); });
  }

  // Reveal on scroll
  var items = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add('in'); });
  }

  // Contact form
  var form = document.getElementById('contact-form');
  if (!form) return;
  var status = form.querySelector('.form-status');
  var submit = form.querySelector('button[type="submit"]');
  var d = form.dataset;

  function say(msg, cls) {
    status.textContent = msg;
    status.className = 'form-status ' + (cls || '');
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var f = form.elements;
    if (f._gotcha && f._gotcha.value) return; // bot

    var missing = false;
    ['name', 'email', 'message'].forEach(function (n) {
      var ok = f[n].value.trim() !== '' && (n !== 'email' || /^\S+@\S+\.\S+$/.test(f[n].value.trim()));
      f[n].classList.toggle('invalid', !ok);
      if (!ok) missing = true;
    });
    if (missing) { say(d.msgRequired, 'error'); return; }

    var data = {
      name: f.name.value.trim(), company: f.company.value.trim(), email: f.email.value.trim(),
      phone: f.phone.value.trim(), topic: f.topic.value, message: f.message.value.trim()
    };

    if (d.ejsService && d.ejsTemplate && d.ejsKey) {
      // EmailJS REST API: delivers the enquiry straight to the company inbox
      submit.disabled = true; say(d.msgSending, 'info');
      fetch('https://api.emailjs.com/api/v1.0/email/send', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          service_id: d.ejsService, template_id: d.ejsTemplate, user_id: d.ejsKey,
          template_params: {
            from_name: data.name, company: data.company || '-', reply_to: data.email,
            phone: data.phone || '-', topic: data.topic, message: data.message,
            site_language: d.lang === 'ar' ? 'Arabic' : 'English'
          }
        })
      }).then(function (r) {
        if (!r.ok) throw new Error('bad status');
        form.reset(); say(d.msgOk, 'ok');
      }).catch(function () { say(d.msgErr, 'error'); })
        .then(function () { submit.disabled = false; });
    } else if (d.endpoint) {
      submit.disabled = true; say(d.msgSending, 'info');
      fetch(d.endpoint, {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(data)
      }).then(function (r) {
        if (!r.ok) throw new Error('bad status');
        form.reset(); say(d.msgOk, 'ok');
      }).catch(function () { say(d.msgErr, 'error'); })
        .then(function () { submit.disabled = false; });
    } else if (d.email) {
      var body = data.message + '\n\n' + data.name + (data.company ? ' (' + data.company + ')' : '') +
        '\n' + data.email + (data.phone ? '\n' + data.phone : '');
      window.location.href = 'mailto:' + d.email + '?subject=' + encodeURIComponent(data.topic + ' - ' + data.name) +
        '&body=' + encodeURIComponent(body);
      say(d.msgMailto, 'info');
    } else {
      say(d.msgNotready, 'info');
    }
  });

  form.addEventListener('input', function (e) { e.target.classList.remove('invalid'); });
})();
