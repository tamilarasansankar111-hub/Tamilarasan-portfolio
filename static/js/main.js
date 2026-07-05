/*
 * main.js — public-facing site behavior.
 * Handles: loader, theme toggle, mobile nav, scroll-reveal animations,
 * skill progress bars, the hero typing effect, and the contact form.
 * Admin-only logic lives in admin.js (loaded only on /admin).
 */

// ===== Loader =====
window.addEventListener('load', () => {
  const loader = document.getElementById('loader');
  if (loader) setTimeout(() => loader.classList.add('hidden'), 700);
});

// ===== Year =====
const yearEl = document.getElementById('year');
if (yearEl) yearEl.textContent = new Date().getFullYear();

// ===== Theme toggle (persists across pages via localStorage — display preference only) =====
const themeToggle = document.getElementById('themeToggle');
const body = document.body;
const savedTheme = localStorage.getItem('portfolio_theme') || 'light';
body.setAttribute('data-theme', savedTheme);

function setThemeIcon(theme) {
  if (!themeToggle) return;
  themeToggle.innerHTML = theme === 'dark' ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
}
setThemeIcon(savedTheme);

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const next = body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    body.setAttribute('data-theme', next);
    localStorage.setItem('portfolio_theme', next);
    setThemeIcon(next);
  });
}

// ===== Mobile menu =====
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');
if (hamburger && mobileMenu) {
  hamburger.addEventListener('click', () => {
    mobileMenu.classList.toggle('open');
    const icon = hamburger.querySelector('i');
    icon.classList.toggle('fa-bars');
    icon.classList.toggle('fa-xmark');
  });
  mobileMenu.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      mobileMenu.classList.remove('open');
      hamburger.querySelector('i').classList.add('fa-bars');
      hamburger.querySelector('i').classList.remove('fa-xmark');
    });
  });
}

// ===== Scroll reveal =====
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('in');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.15 });
document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

// ===== Skill bars (width comes from data-width, rendered server-side by Jinja) =====
const skillObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.width = entry.target.dataset.width;
      skillObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.3 });
document.querySelectorAll('.skill-bar span').forEach(bar => skillObserver.observe(bar));

// ===== Typing terminal effect (home page only) =====
const typedEl = document.getElementById('typed');
if (typedEl) {
  const phrases = [
    typedEl.dataset.phrase1 || 'Building things with Python, HTML, CSS & curiosity_',
    typedEl.dataset.phrase2 || 'Passionate about full stack & AI-driven web dev_',
    typedEl.dataset.phrase3 || 'Turning ideas into responsive web applications_'
  ];
  let phraseIndex = 0, charIndex = 0, deleting = false;
  function typeLoop() {
    const current = phrases[phraseIndex];
    if (!deleting) {
      charIndex++;
      typedEl.textContent = current.slice(0, charIndex);
      if (charIndex === current.length) { deleting = true; setTimeout(typeLoop, 1600); return; }
    } else {
      charIndex--;
      typedEl.textContent = current.slice(0, charIndex);
      if (charIndex === 0) { deleting = false; phraseIndex = (phraseIndex + 1) % phrases.length; }
    }
    setTimeout(typeLoop, deleting ? 30 : 55);
  }
  typeLoop();
}

// ===== Contact form -> mailto =====
const contactForm = document.getElementById('contactForm');
if (contactForm) {
  contactForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const message = document.getElementById('message').value;
    const toEmail = contactForm.dataset.toEmail || 'tamilarasansankar111@gmail.com';
    const subject = encodeURIComponent(`Portfolio Contact from ${name}`);
    const body2 = encodeURIComponent(`${message}\n\n— ${name} (${email})`);
    window.location.href = `mailto:${toEmail}?subject=${subject}&body=${body2}`;
  });
}
