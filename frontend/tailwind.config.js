/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          950: '#07090e',
          900: '#0c1017',
          850: '#111622',
          800: '#161c2b',
          700: '#232d42',
        },
        brand: {
          cyan: '#00f2fe',
          teal: '#05df9d',
          orange: '#ff6b35',
          purple: '#8b5cf6',
          rose: '#f43f5e'
        }
      }
    },
  },
  plugins: [],
}
