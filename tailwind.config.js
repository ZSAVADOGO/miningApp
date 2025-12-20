/** @type {import('tailwindcss').Config} */
//module.exports = {
  //content: ["./src/**/*.{html,js,ts}"],
//  theme: {
//    extend: {},
//  },
//  plugins: [],
//}

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './miningText/templates/**/*.html',
    './miningText/**/*.py',
    // Ajoutez d'autres apps si nécessaire
    // './blog/templates/**/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}