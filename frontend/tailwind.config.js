/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: '#0F2A30',
          light: '#123B44',
        },
        teal: {
          50: '#EAF3F3',
          100: '#CFE6E6',
          400: '#2E8C97',
          500: '#1F6F7A',
          600: '#175A63',
          700: '#123B44',
          900: '#0F2A30',
        },
        gold: {
          400: '#E4B75C',
          500: '#D9A441',
          600: '#B88430',
        },
        positive: '#2F9E64',
        negative: '#C4483B',
        surface: '#F4F6F5',
        slate: {
          500: '#4B5A63',
          700: '#2A363C',
        },
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['"Inter"', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
}
