import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Wszystko spiete jawnie po IPv4 (127.0.0.1). Mieszanie rodzin adresow
// (np. Vite na ::1, backend na 127.0.0.1) konczy sie 2-sekundowymi timeoutami
// na Windows, bo SYN do zamknietego portu loopback jest upuszczany, nie odrzucany.
const backend = 'http://127.0.0.1:8000';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    proxy: {
      // Tylko ruch /api idzie do backendu; reszta sciezek to trasy SPA,
      // ktore Vite serwuje (dziala odswiezanie /recipes, /products itd.).
      '/api': {
        target: backend,
        changeOrigin: true,
        // Backend nie zna prefiksu /api — zdejmujemy go przed przekazaniem.
        rewrite: (path) => path.replace(/^\/api/, ''),
        // Przepisuje domain w Set-Cookie z backend'u na localhost,
        // żeby przeglądarka przypisała cookie do frontendu (port 5173)
        cookieDomainRewrite: 'localhost',
      },
    },
  },
});
