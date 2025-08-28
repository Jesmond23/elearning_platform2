module.exports = {
  content: [
    "./**/templates/**/*.html",  // Match ALL templates in any app
    "./templates/**/*.html",     // Root templates folder (optional)
    "./static/js/**/*.js"        // Only if using Tailwind in JS
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Nunito', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}