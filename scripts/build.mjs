import { build } from 'esbuild';
import { execFileSync } from 'node:child_process';
import { cp, mkdir, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
process.chdir(root);
execFileSync('cargo', ['build', '--locked', '--release', '--target', 'wasm32-unknown-unknown', '--manifest-path', 'wasm/Cargo.toml'], { stdio: 'inherit' });
await rm('dist', { recursive: true, force: true });
await mkdir('dist/vendor', { recursive: true });
await cp('web/slides.json', 'dist/slides.json');
await cp('assets', 'dist/assets', { recursive: true });
await cp('web/index.html', 'dist/index.html');
await cp('web/style.css', 'dist/style.css');
await cp('web/slides.css', 'dist/slides.css');
await cp('wasm/target/wasm32-unknown-unknown/release/predator_prey_core.wasm', 'dist/core.wasm');
await cp('node_modules/katex/dist/katex.min.css', 'dist/vendor/katex.min.css');
await cp('node_modules/katex/dist/fonts', 'dist/vendor/fonts', { recursive: true });
await cp('node_modules/plotly.js-dist-min/plotly.min.js', 'dist/vendor/plotly.min.js');
// Keep the existing figures and their exact Plotly version, but serve locally.
for (const name of await readdir('dist/assets')) {
  if (!name.endsWith('.html')) continue;
  const file = `dist/assets/${name}`;
  const html = await readFile(file, 'utf8');
  await writeFile(file, html.replaceAll('https://cdn.plot.ly/plotly-2.32.0.min.js', '../vendor/plotly.min.js'));
}
await build({ entryPoints: ['web/app.js', 'web/simulation-worker.js'], bundle: true, format: 'esm', target: 'es2022', outdir: 'dist', minify: true });
await writeFile('dist/.nojekyll', '');
let revision = 'local';
try { revision = execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(); } catch {}
await writeFile('dist/build.json', JSON.stringify({ revision, model: 'published DM/ADM model', runtime: 'Rust/WebAssembly in a Web Worker' }));
console.log('Built dist/: static slides, assets and local-compute simulator.');
