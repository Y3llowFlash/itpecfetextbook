import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

export default defineConfig({
  site: 'https://itpectextbook.com',
  output: 'static',
  trailingSlash: 'always',
  integrations: [react()],
  devToolbar: { enabled: false },
});
