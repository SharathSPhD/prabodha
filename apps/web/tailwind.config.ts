import type { Config } from "tailwindcss";

// Neuro-lab bioluminescent design system — matches the GitHub Pages site.
// Palette class NAMES are kept (indigo/teal/saffron/night) but remapped to the
// neuro-lab tokens so every existing utility usage adopts the new look at once:
//   indigo → violet (#a855f7)   teal → cyan (#22d3ee)
//   saffron → amber (#f59e0b)   night → deep blue-black surfaces
//   rose (new) → reject / arm-none (#fb7185)
const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // primary accent — violet
        indigo: {
          50: "#f5f0ff",
          100: "#ede0ff",
          200: "#ddc4fe",
          300: "#c99bfb",
          400: "#b674f8",
          500: "#a855f7",
          600: "#9333ea",
          700: "#7e22ce",
          800: "#6b21a8",
          900: "#581c87",
        },
        // secondary accent — cyan
        teal: {
          50: "#ecfeff",
          100: "#cffafe",
          200: "#a5f3fc",
          300: "#67e8f9",
          400: "#22d3ee",
          500: "#06b6d4",
          600: "#0891b2",
          700: "#0e7490",
          800: "#155e75",
          900: "#164e63",
        },
        // tertiary accent — amber
        saffron: {
          50: "#fffbeb",
          100: "#fef3c7",
          200: "#fde68a",
          300: "#fcd34d",
          400: "#fbbf24",
          500: "#f59e0b",
          600: "#d97706",
          700: "#b45309",
          800: "#92400e",
          900: "#78350f",
        },
        // warning / reject / arm-none — rose
        rose: {
          300: "#fda4af",
          400: "#fb7185",
          500: "#f43f5e",
          600: "#e11d48",
        },
        // surfaces — deep blue-black
        night: {
          950: "#070a10", // deepest inset
          900: "#0a0e14", // page background
          800: "#0d1420", // panel
          700: "#111824", // elevated card
          600: "#1d2839", // hairline / border
          500: "#2b3a52", // stronger hairline
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        serif: ["var(--font-fraunces)", "Georgia", "serif"],
        mono: ["var(--font-plex-mono)", "SF Mono", "ui-monospace", "monospace"],
      },
      fontSize: {
        xs: ["12px", "16px"],
        sm: ["14px", "20px"],
        base: ["16px", "24px"],
        lg: ["18px", "28px"],
        xl: ["20px", "28px"],
        "2xl": ["24px", "32px"],
        "3xl": ["30px", "36px"],
        "4xl": ["36px", "44px"],
        "5xl": ["48px", "52px"],
      },
      boxShadow: {
        glow: "0 0 24px rgba(168, 85, 247, 0.28)",
        "glow-teal": "0 0 24px rgba(34, 211, 238, 0.28)",
        "glow-amber": "0 0 24px rgba(245, 158, 11, 0.25)",
      },
      animation: {
        pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        fade: "fade 0.3s ease-in-out",
        "pulse-glow": "pulseGlow 2.4s ease-in-out infinite",
      },
      keyframes: {
        pulse: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.5" },
        },
        fade: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        pulseGlow: {
          "0%, 100%": { boxShadow: "0 0 16px rgba(34, 211, 238, 0.20)" },
          "50%": { boxShadow: "0 0 28px rgba(34, 211, 238, 0.45)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
