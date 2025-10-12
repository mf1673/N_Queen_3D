import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../static',   // Flask servirà da questa cartella, salva il bundle in /static
    emptyOutDir: true,
    rollupOptions: {
      input: 'src/main.jsx',
      output: {
        entryFileNames: 'viewer.js',  // nome del bundle finale
        name: 'Queen3DViewerApp'
      }
    }
  }
})
