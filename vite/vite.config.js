import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss()],
  build: {
    rollupOptions: {
      input: {
        main: "./src/main.js",
        styles: "./src/styles.css",
      },
      output: {
        entryFileNames: "[name].js",
        assetFileNames: "[name].css",
      },
    },
    outDir: "dist",
    assetsDir: "",
    manifest: false,
  },
});
