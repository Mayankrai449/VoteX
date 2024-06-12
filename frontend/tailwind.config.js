/** @type {import('tailwindcss').Config} */
export const content = [
  "./src/**/*.{js,jsx,ts,tsx}",
  "node_modules/flowbite/**/*.js"
];
export const theme = {
  extend: {},
};
export const plugins = [
  require('flowbite/plugin')
];

