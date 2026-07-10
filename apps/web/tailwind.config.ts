import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Deep indigo / teal / saffron tri-accent (prabodha palette)
        indigo: {
          50: "#f3f0ff",
          100: "#e8e0ff",
          200: "#d4c5ff",
          300: "#b5a0ff",
          400: "#9176ff",
          500: "#7c4dff",
          600: "#6d35d0",
          700: "#5e2ab8",
          800: "#512196",
          900: "#45197a",
        },
        teal: {
          50: "#f0fdf9",
          100: "#e0fdf4",
          200: "#b3fbe6",
          300: "#6ffee2",
          400: "#2ff5d3",
          500: "#14dcbb",
          600: "#0dbd9f",
          700: "#0d9688",
          800: "#126d6b",
          900: "#115858",
        },
        saffron: {
          50: "#fffbf0",
          100: "#fff6e0",
          200: "#ffebcc",
          300: "#ffd966",
          400: "#ffcd33",
          500: "#ffc107",
          600: "#f5a623",
          700: "#e67e22",
          800: "#d9650d",
          900: "#8b4513",
        },
        night: {
          950: "#050a14",
          900: "#0a1123",
          800: "#1a1f3a",
          700: "#252d47",
          600: "#34395a",
          500: "#4a5178",
        },
      },
      fontFamily: {
        sans: ["system-ui", "sans-serif"],
        serif: ["Georgia", "serif"],
        mono: ["Monaco", "monospace"],
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
      },
      boxShadow: {
        glow: "0 0 24px rgba(124, 77, 255, 0.15)",
        "glow-teal": "0 0 24px rgba(20, 220, 187, 0.15)",
      },
      animation: {
        pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        fade: "fade 0.3s ease-in-out",
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
      },
    },
  },
  plugins: [],
};

export default config;
