import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const backend = 'http://localhost:8000';

const proxyTargets = [
  '/auth',
  '/users',
  '/products',
  '/recipes',
  '/meals',
  '/leaderboard',
];

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: Object.fromEntries(
      proxyTargets.map((p) => [
        p,
        {
          target: backend,
          changeOrigin: true,
          // Przepisuje domain w Set-Cookie z backend'u na localhost,
          // żeby przeglądarka przypisała cookie do frontendu (port 5173)
          cookieDomainRewrite: 'localhost',
        },
      ])
    ),
  },
});
