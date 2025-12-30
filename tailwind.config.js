/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Use CSS variables for theming
        primary: 'var(--color-primary)',
        'primary-hover': 'var(--color-primary-hover)',
        accent: 'var(--color-accent)',
        'accent-hover': 'var(--color-accent-hover)',
        'bg-page': 'var(--color-bg-page)',
        'bg-card': 'var(--color-bg-card)',
        'bg-sidebar': 'var(--color-bg-sidebar)',
      },
      fontFamily: {
        'sans': ['Arial', 'Helvetica', 'sans-serif'],
        'arabic': ['Droid Arabic Kufi', 'Arial', 'sans-serif'],
      },
      fontSize: {
        'xs': '12px',
        'sm': '13px',
        'base': '14px',
        'lg': '16px',
        'xl': '18px',
        '2xl': '20px',
        '3xl': '22px',
      },
    },
    borderRadius: {
      'none': '0',
      'sm': '2px',
      'DEFAULT': '0px',
      'md': '0px',
      'lg': '0px',
      'xl': '0px',
      '2xl': '0px',
      'full': '9999px',
    },
  },
  plugins: [],
}