/** @type {import('tailwindcss').Config} */
import { tailwindConfig } from '@neo4j-ndl/base';

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
  presets:[tailwindConfig],
  corePlugins: {
    preflight: false,
  },
  prefix:""
}

