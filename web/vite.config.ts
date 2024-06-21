import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

import postcss from "./postcss.config.cjs";

export default defineConfig({
	css: {
		postcss,
	},
	plugins: [
		sveltekit(),
	],
	optimizeDeps: {
		exclude: [],
	},
	assetsInclude: [],
});
