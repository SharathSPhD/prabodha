/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        // prabodha color system — distinctive and grounded in research
        primary: '#1a1a2e',      // deep indigo (workspace band)
        accent: '#e94b3c',       // rust/terracotta (activation/write)
        bright: '#ffd166',       // gold (gating events / sphuraṭṭā)
        neutral: '#d4d4d4',      // recessive text
        muted: '#7a7a8e',        // secondary text
        success: '#6ecb63',      // calibration/transfer
        warning: '#f7b32b',      // honest negatives / margins
        surface: '#ffffff',      // light mode
        'surface-dark': '#0f0f1a', // dark mode
        band: '#3d3d5c',         // mid band
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Crimson Text', 'Georgia', 'serif'],
        mono: ['IBM Plex Mono', 'monospace'],
      },
      typography: {
        DEFAULT: {
          css: {
            color: '#1a1a2e',
            a: { color: '#e94b3c', textDecoration: 'none' },
            'a:hover': { textDecoration: 'underline' },
            'code::before': { content: '""' },
            'code::after': { content: '""' },
            code: { color: '#e94b3c', backgroundColor: '#f5f5f7', padding: '0.125rem 0.375rem' },
          }
        }
      }
    },
  },
  plugins: [],
  darkMode: ['class', '[data-theme="dark"]'],
};
