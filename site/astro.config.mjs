import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  base: '/prabodha',
  integrations: [tailwind()],
  output: 'static',
  vite: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src')
      }
    },
    ssr: {
      external: ['d3']
    }
  }
});
