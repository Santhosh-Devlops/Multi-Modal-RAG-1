/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
        mono: ['"Fira Code"', 'Consolas', 'Monaco', 'monospace'],
      },
      fontSize: {
        'xs': ['0.8125rem', { lineHeight: '1.25rem' }],
        'sm': ['0.9375rem', { lineHeight: '1.4rem' }],
        'base': ['1.0625rem', { lineHeight: '1.65rem' }],
        'lg': ['1.1875rem', { lineHeight: '1.75rem' }],
        'xl': ['1.3125rem', { lineHeight: '1.85rem' }],
        '2xl': ['1.625rem', { lineHeight: '2.1rem' }],
        '3xl': ['2rem', { lineHeight: '2.4rem' }],
      },
      colors: {
        // HCLTech Brand Palette
        brand: {
          50: '#F5F0FA',
          100: '#E8DCF7',
          200: '#CEB5EF',
          300: '#B088E5',
          400: '#8E57D8',
          500: '#542580', // HCLTech Signature Purple/Violet
          600: '#471B70',
          700: '#3A125E',
          800: '#2C0A4B',
          900: '#1B0432',
          950: '#0E021B',
        },
        hclblue: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          400: '#388BFD',
          500: '#0057FF', // HCLTech Signature Blue
          600: '#0047D6',
          700: '#0037A8',
        },
        hclsurface: {
          light: '#FFFFFF',
          lightsubtle: '#F8F9FB',
          dark: '#0D0A1C', // HCLTech Deep Navy
          darkcard: '#16122E',
          darkborder: '#282252',
        }
      }
    },
  },
  plugins: [],
}
