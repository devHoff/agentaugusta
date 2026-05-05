/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        augusta: {
          50: '#f0f4ff',
          100: '#e0e8ff',
          500: '#4f6ef7',
          600: '#3b5ce6',
          700: '#2d4acf',
          900: '#1a2d7a',
        }
      }
    },
  },
  plugins: [],
}
