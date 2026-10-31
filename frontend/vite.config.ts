import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import {tanstackRouter} from "@tanstack/router-plugin/vite"
import tailwindcss from '@tailwindcss/vite'
import path from 'path'
// https://vite.dev/config/
export default defineConfig({
  build: {
    outDir: "../backend/app/frontend",
    emptyOutDir:true
   },
   resolve:{
    alias:{
      "@": path.resolve(import.meta.dirname, "./src")
    }
  },
  plugins: [
    tanstackRouter(),
    react(),
    tailwindcss(),
  ],
})
