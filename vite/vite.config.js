import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    tailwindcss(),
  ],
  build: {
    rollupOptions: {
      input: './index.html',
      output: {
        assetFileNames: 'styles.css',
      }
    },
    outDir: 'dist',
    assetsDir: '',
    manifest: false,
  }
})
