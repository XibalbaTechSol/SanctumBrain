/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        card: "var(--card)",
        border: "var(--border)",
        "muted-foreground": "var(--muted-foreground)",
        aurora: {
          red: "var(--aurora-red)",
          orange: "var(--aurora-orange)",
          yellow: "var(--aurora-yellow)",
          green: "var(--aurora-green)",
          purple: "var(--aurora-purple)",
          blue: "var(--aurora-blue)",
          cyan: "var(--aurora-cyan)",
        },
        indigo: {
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
        },
      },
      fontFamily: {
        mono: ["'JetBrains Mono'", "'Fira Code'", "monospace"],
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
