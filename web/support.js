// prabodha web support library
// Handles hero canvas animation, scroll-spy navigation, and interactive embeds.
// Respects prefers-reduced-motion.

(function() {
  'use strict';

  // ============================================================================
  // SETUP & UTILITIES
  // ============================================================================

  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const sections = document.querySelectorAll('[data-section]');
  const scrollSpyDots = document.querySelectorAll('[data-dot]');
  const heroCanvas = document.getElementById('prabodha-hero-canvas');

  // ============================================================================
  // HERO CANVAS ANIMATION: J-space band with flowing token stream
  // ============================================================================
  // Concept: vimarśa (reflexive awareness) — the token stream flows through the
  // J-space band; gated writes light up the band on certain tokens (marked by
  // the trace data passed in via window.PRABODHA.replays).

  let heroCtx = null;
  let heroAnimationId = null;
  let heroTime = 0;
  const HERO_FPS = 60;
  const HERO_DT = 1 / HERO_FPS;

  function initHeroCanvas() {
    if (!heroCanvas) return;

    // Size canvas to window
    function resizeCanvas() {
      const rect = heroCanvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      heroCanvas.width = rect.width * dpr;
      heroCanvas.height = rect.height * dpr;
      if (heroCtx) heroCtx.scale(dpr, dpr);
    }

    heroCtx = heroCanvas.getContext('2d');
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    if (!prefersReduced) {
      animateHeroCanvas();
    } else {
      // Reduced motion: draw a static frame
      drawHeroCanvasFrame(0);
    }
  }

  function drawHeroCanvasFrame(t) {
    if (!heroCtx) return;

    const w = heroCanvas.width;
    const h = heroCanvas.height;
    const dpr = window.devicePixelRatio || 1;

    // Clear with gradient background
    const grad = heroCtx.createLinearGradient(0, 0, 0, h);
    grad.addColorStop(0, '#0A0D14');
    grad.addColorStop(1, '#1a1a2e');
    heroCtx.fillStyle = grad;
    heroCtx.fillRect(0, 0, w / dpr, h / dpr);

    // Draw the J-space band: a horizontal ribbon at mid-canvas
    const bandY = (h / dpr) * 0.5;
    const bandHeight = 80;
    const bandX0 = 60;
    const bandX1 = (w / dpr) - 60;
    const bandLength = bandX1 - bandX0;

    // Band background (teal gradient, faint)
    heroCtx.fillStyle = 'rgba(79, 216, 206, 0.1)';
    heroCtx.fillRect(bandX0, bandY - bandHeight / 2, bandLength, bandHeight);

    // Band border (teal outline)
    heroCtx.strokeStyle = 'rgba(79, 216, 206, 0.4)';
    heroCtx.lineWidth = 1;
    heroCtx.strokeRect(bandX0, bandY - bandHeight / 2, bandLength, bandHeight);

    // Token stream (dots flowing left-to-right through the band)
    const numTokens = 12;
    const tokenRadius = 3.5;
    const tokenSpeed = 0.3; // pixels per frame
    const tokenPhase = (t * tokenSpeed) % bandLength;

    for (let i = 0; i < numTokens; i++) {
      const tokenX = bandX0 + ((i / numTokens) * bandLength + tokenPhase) % bandLength;

      // Base color: teal for most tokens, indigo/saffron for "gated" ones
      const isGated = i % 4 === 0;  // every 4th token is "gated" for visual interest
      const hue = isGated ? 'rgba(180, 155, 240, 0.6)' : 'rgba(79, 216, 206, 0.5)';

      heroCtx.fillStyle = hue;
      heroCtx.beginPath();
      heroCtx.arc(tokenX, bandY, tokenRadius, 0, 2 * Math.PI);
      heroCtx.fill();

      // Glow for active tokens
      if (isGated) {
        heroCtx.strokeStyle = 'rgba(180, 155, 240, 0.3)';
        heroCtx.lineWidth = 1;
        heroCtx.beginPath();
        heroCtx.arc(tokenX, bandY, tokenRadius + 6, 0, 2 * Math.PI);
        heroCtx.stroke();
      }
    }

    // Label: "J-space band" (light text)
    heroCtx.fillStyle = 'rgba(217, 211, 199, 0.7)';
    heroCtx.font = '13px "Space Grotesk", sans-serif';
    heroCtx.textAlign = 'left';
    heroCtx.fillText('J-space workspace band', bandX0 + 8, bandY - bandHeight / 2 - 8);

    // Annotations: sphuraṭṭā (gating event) label
    heroCtx.fillStyle = 'rgba(240, 162, 75, 0.5)';
    heroCtx.font = '11px "JetBrains Mono", monospace';
    heroCtx.textAlign = 'right';
    heroCtx.fillText('sphuraṭṭā: gating event', bandX1 - 8, bandY + bandHeight / 2 + 20);
  }

  function animateHeroCanvas() {
    function frame() {
      heroTime += HERO_DT;
      drawHeroCanvasFrame(heroTime);
      heroAnimationId = requestAnimationFrame(frame);
    }
    if (heroAnimationId === null) {
      heroAnimationId = requestAnimationFrame(frame);
    }
  }

  // ============================================================================
  // SCROLL-SPY NAVIGATION
  // ============================================================================

  function updateScrollSpy() {
    let activeSection = null;
    let maxIntersection = 0;

    sections.forEach(section => {
      const rect = section.getBoundingClientRect();
      const intersection = Math.max(0, Math.min(window.innerHeight, rect.bottom) - Math.max(0, rect.top));

      if (intersection > maxIntersection) {
        maxIntersection = intersection;
        activeSection = section.getAttribute('data-section');
      }
    });

    scrollSpyDots.forEach(dot => {
      const dotId = dot.getAttribute('data-dot');
      if (dotId === activeSection) {
        dot.classList.add('active');
        dot.setAttribute('aria-current', 'page');
      } else {
        dot.classList.remove('active');
        dot.removeAttribute('aria-current');
      }
    });
  }

  // ============================================================================
  // PROGRESS BAR
  // ============================================================================

  const progressBar = document.getElementById('prabodha-progress');
  if (progressBar) {
    window.addEventListener('scroll', () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrolled = (scrollTop / docHeight) * 100;
      progressBar.style.width = scrolled + '%';
    });
  }

  // ============================================================================
  // INTERACTIVE EMBEDS (slice heatmap, result charts)
  // ============================================================================

  // Embed click handlers: when user clicks an embed trigger, load and render
  // the full interactive visualization (D3 for slice heatmap, basic SVG for charts).

  document.addEventListener('click', (e) => {
    const embed = e.target.closest('[data-embed]');
    if (!embed) return;

    const embedType = embed.getAttribute('data-embed');
    const container = embed.parentElement;

    if (embedType === 'fire-slice') {
      loadFireSliceHeatmap(container);
    } else if (embedType === 'results-chart') {
      loadResultsChart(container);
    }
  });

  async function loadFireSliceHeatmap(container) {
    // Load fire_slice.json and render D3 heatmap inline.
    // The actual D3 code is light and lives in index.html's <script> block.
    const button = container.querySelector('[data-embed]');
    if (button) button.disabled = true;

    try {
      const res = await fetch('data/fire_slice.json');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      // Dispatch custom event for the D3 code to listen for
      window.dispatchEvent(new CustomEvent('fireSliceDataLoaded', { detail: data }));

      // Render placeholder until D3 initializes
      container.innerHTML = '<div style="background:#1a1a2e;height:400px;border:1px solid #4FD8CE4a;border-radius:4px;display:flex;align-items:center;justify-content:center;color:#9B9FA0;font-size:13px;">Loading fire-case slice visualization...</div>';
    } catch (err) {
      container.innerHTML = `<div style="color:#b00;font-size:12px;">Error loading slice data: ${err.message}</div>`;
      if (button) button.disabled = false;
    }
  }

  function loadResultsChart(container) {
    // Render results table from window.PRABODHA.results.claims
    if (!window.PRABODHA || !window.PRABODHA.results) {
      container.innerHTML = '<div style="color:#999;font-size:12px;">Results data not available.</div>';
      return;
    }

    const claims = window.PRABODHA.results.claims;
    let html = '<table style="width:100%;border-collapse:collapse;font-size:13px;font-family:\'JetBrains Mono\',monospace;">';
    html += '<tr style="border-bottom:1px solid #4FD8CE4a;"><th style="text-align:left;padding:8px;color:#4FD8CE;font-weight:600;">Claim</th><th style="text-align:left;padding:8px;color:#4FD8CE;font-weight:600;">Tier</th><th style="text-align:left;padding:8px;color:#4FD8CE;font-weight:600;">Numbers</th></tr>';

    claims.forEach(claim => {
      const nums = claim.numbers ? Object.entries(claim.numbers).map(([k, v]) => `${k}=${v}`).join(', ') : '—';
      html += `<tr style="border-bottom:1px solid #4FD8CE1a;"><td style="padding:8px;">${claim.text}</td><td style="padding:8px;color:#9B9FA0;font-size:11px;">${claim.tier}</td><td style="padding:8px;color:#9B9FA0;font-size:11px;"><code>${nums}</code></td></tr>`;
    });

    html += '</table>';
    container.innerHTML = html;
  }

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  document.addEventListener('DOMContentLoaded', () => {
    initHeroCanvas();
    updateScrollSpy();
    window.addEventListener('scroll', updateScrollSpy, { passive: true });
  });

  // Export for testing
  window.prabodhaSupport = { updateScrollSpy, drawHeroCanvasFrame };
})();
