// ── NAVBAR SCROLL ──
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 50);
});

// ── SEARCH MODAL ──
const searchBtn = document.getElementById('searchBtn');
const searchModal = document.getElementById('searchModal');
const searchClose = document.getElementById('searchClose');

searchBtn.addEventListener('click', () => {
  searchModal.classList.add('open');
  searchModal.querySelector('input').focus();
});

searchClose.addEventListener('click', () => searchModal.classList.remove('open'));
searchModal.addEventListener('click', e => { 
  if (e.target === searchModal) searchModal.classList.remove('open'); 
});

document.addEventListener('keydown', e => { 
  if (e.key === 'Escape') searchModal.classList.remove('open'); 
});

// ── HAMBURGER & MOBILE MENU ──
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');

hamburger.addEventListener('click', () => {
  mobileMenu.classList.toggle('open');
  const spans = hamburger.querySelectorAll('span');
  
  if (mobileMenu.classList.contains('open')) {
    spans[0].style.transform = 'translateY(7px) rotate(45deg)';
    spans[1].style.opacity = '0';
    spans[2].style.transform = 'translateY(-7px) rotate(-45deg)';
  } else {
    spans.forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
  }
});

mobileMenu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
  mobileMenu.classList.remove('open');
  hamburger.querySelectorAll('span').forEach(s => { 
    s.style.transform = ''; 
    s.style.opacity = ''; 
  });
}));

// ── SCROLL REVEAL (Animaciones al hacer Scroll) ──
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.08 });

document.querySelectorAll('.featured-side, .featured-main').forEach((el, i) => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(28px)';
  el.style.transition = `opacity 0.55s ${i * 0.06}s cubic-bezier(.22,1,.36,1), transform 0.55s ${i * 0.06}s cubic-bezier(.22,1,.36,1)`;
  observer.observe(el);
});