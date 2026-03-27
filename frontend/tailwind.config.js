/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        parchment: "#F5E6C8",
        wood:      "#8B5E3C",
        bark:      "#3D2B1F",
        grass:     "#4A9E2F",
        gold:      "#F0C040",
        sky:       "#87CEEB",
        stone:     "#A09080",
      },
      fontFamily: {
        pixel: ['"VT323"', "monospace"],
      },
    },
  },
  plugins: [],
};
