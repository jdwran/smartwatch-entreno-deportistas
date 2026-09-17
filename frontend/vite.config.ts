import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5180,
    strictPort: false, // Busca automáticamente el siguiente puerto libre si 5180 está ocupado
    host: true,
  },
})
