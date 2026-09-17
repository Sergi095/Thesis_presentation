import { build } from 'esbuild';
import { execFileSync } from 'node:child_process';
import { cp, mkdir, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { createHash } from 'node:crypto';

const root = path.resolve(fileURLToPath(new URL('..', import.meta.url)));
process.chdir(root);
execFileSync('cargo', ['build', '--locked', '--release', '--target', 'wasm32-unknown-unknown', '--manifest-path', 'wasm/Cargo.toml'], { stdio: 'inherit' });
await rm('dist', { recursive: true, force: true });
await mkdir('dist/vendor', { recursive: true });
// Every changing runtime entry gets its own URL. A cached worker must never
// load a different release's WASM module under an unchanged core.wasm URL.
async function fingerprint(source, name, extension) {
  const bytes = await readFile(source);
  const hash = createHash('sha256').update(bytes).digest('hex').slice(0, 16);
  const file = `${name}-${hash}.${extension}`;
  await writeFile(`dist/${file}`, bytes);
  return file;
}
const slidesAsset = await fingerprint('web/slides.json', 'slides', 'json');
await cp('assets', 'dist/assets', { recursive: true });
let html = await readFile('web/index.html', 'utf8');
for (const name of ['style', 'slides', 'lab']) {
  const file = await fingerprint(`web/${name}.css`, name, 'css');
  html = html.replace(`./${name}.css`, `./${file}`);
}
await cp('node_modules/ammojs3/builds/ammo.wasm.js', 'dist/vendor/ammo.wasm.js');
await cp('node_modules/ammojs3/builds/ammo.wasm.wasm', 'dist/vendor/ammo.wasm.wasm');
await cp('node_modules/ammojs3/LICENSE', 'dist/vendor/ammo.LICENSE');
await cp('node_modules/three/LICENSE', 'dist/vendor/three.LICENSE');
await cp('docs/licenses/gym-pybullet-drones.txt', 'dist/vendor/flight-control.LICENSE');
const coreAsset = await fingerprint('wasm/target/wasm32-unknown-unknown/release/predator_prey_core.wasm', 'core', 'wasm');
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
const options = { bundle: true, target: 'es2022', outdir: 'dist', minify: true, metafile: true, entryNames: '[name]-[hash]' };
function entryFile(result, entry) {
  const output = Object.entries(result.metafile.outputs).find(([, info]) => info.entryPoint === entry);
  if (!output) throw new Error(`Missing build entry: ${entry}`);
  return path.basename(output[0]);
}
const workerDefines = { __CORE_ASSET__: JSON.stringify(`./${coreAsset}`) };
const swarmBuild = await build({ ...options, entryPoints: ['web/simulation-worker.js'], format: 'esm', define: workerDefines });
const labBuild = await build({ ...options, entryPoints: ['web/lab-worker.js'], format: 'iife', define: workerDefines });
const swarmWorker = entryFile(swarmBuild, 'web/simulation-worker.js');
const labWorker = entryFile(labBuild, 'web/lab-worker.js');
const siteBuild = await build({ ...options, entryPoints: ['web/app.js'], splitting: true, format: 'esm', define: {
  __SWARM_WORKER_ASSET__: JSON.stringify(`./${swarmWorker}`),
  __LAB_WORKER_ASSET__: JSON.stringify(`./${labWorker}`),
  __SLIDES_ASSET__: JSON.stringify(`./${slidesAsset}`),
} });
const appAsset = entryFile(siteBuild, 'web/app.js');
await writeFile('dist/index.html', html.replace('./app.js', `./${appAsset}`));
await writeFile('dist/.nojekyll', '');
let revision = 'local';
try { revision = execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(); } catch {}
await writeFile('dist/build.json', JSON.stringify({ revision, model: 'published DM/ADM model', runtime: 'Rust/WebAssembly in a Web Worker', assets: { core: coreAsset, app: appAsset, swarmWorker, labWorker, slides: slidesAsset } }));
console.log('Built dist/: static slides, assets and local-compute simulator.');
