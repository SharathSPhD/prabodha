/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        // Neuro-lab bioluminescent palette
        bg: 'var(--bg)',
        'bg-elevated': 'var(--bg-elevated)',
        'bg-panel': 'var(--bg-panel)',
        'bg-inset': 'var(--bg-inset)',
        ink: 'var(--ink)',
        'ink-soft': 'var(--ink-soft)',
        'ink-faint': 'var(--ink-faint)',
        hairline: 'var(--hairline)',
        cyan: 'var(--cyan)',
        'cyan-dim': 'var(--cyan-dim)',
        violet: 'var(--violet)',
        'violet-dim': 'var(--violet-dim)',
        amber: 'var(--amber)',
        rose: 'var(--rose)',
        // Defense arms
        'arm-none': 'var(--arm-none)',
        'arm-bruteforce': 'var(--arm-bruteforce)',
        'arm-moat': 'var(--arm-moat)',
        'detect-cyan': 'var(--detect-cyan)',
        // Semantic
        accept: 'var(--accept)',
        reject: 'var(--reject)',
      },
      fontFamily: {
        sans: ['var(--font-sans)'],
        serif: ['var(--font-serif)'],
        mono: ['var(--font-mono)'],
      },
      boxShadow: {
        'glow-cyan': 'var(--glow-cyan)',
        'glow-violet': 'var(--glow-violet)',
      },
      typography: {
        DEFAULT: {
          css: {
            color: 'var(--ink)',
            a: { color: 'var(--cyan)', textDecoration: 'none' },
            'a:hover': { textDecoration: 'underline' },
            'code::before': { content: '""' },
            'code::after': { content: '""' },
            code: { color: 'var(--cyan)', backgroundColor: 'var(--bg-panel)', padding: '0.125rem 0.375rem' },
          }
        }
      }
    },
  },
  plugins: [],
  darkMode: ['class', '[data-theme="dark"]'],
};
