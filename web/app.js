import { marked } from 'marked';
import katex from 'katex';
import { arrangeSlide } from './slide-layout.js';

// Parse equations before Markdown can treat their underscores as emphasis.
marked.use({ extensions: [{
  name: 'inlineMath', level: 'inline',
  start: source => source.indexOf('$'),
  tokenizer(source) {
    const match = /^\$([^$\n]+)\$/.exec(source);
    if (match) return { type: 'inlineMath', raw: match[0], text: match[1] };
  },
  renderer: token => katex.renderToString(token.text, { throwOnError: false }),
}] });

const $ = id => document.getElementById(id);
let slides = [], index = 0, worker, workerReady = false, state = 'loading', latest, config, bounds;
const form = $('simulation-controls');
const canvas = $('arena');
const ctx = canvas.getContext('2d');

function internalLink(value) {
  if (/^\/\d+$/.test(value)) return `#${value}`;
  if (value.startsWith('/assets/')) return `.${value}`;
  return value;
}
function dedent(text) {
  const lines = String(text || '').replace(/^\n/, '').split('\n');
  const indents = lines.filter(x => x.trim()).map(x => /^\s*/.exec(x)[0].length);
  const n = Math.min(...indents, 0xFFFF);
  return lines.map(x => x.slice(n)).join('\n');
}
function render(component) {
  if (component == null) return document.createTextNode('');
  if (Array.isArray(component)) { const f = document.createDocumentFragment(); component.forEach(c => f.append(render(c))); return f; }
  if (typeof component !== 'object') return document.createTextNode(String(component));
  const { type, attrs = {}, children } = component;
  if (type === 'markdown') {
    const el = document.createElement('div');
    const source = dedent(component.text).trim();
    if (/^\$[^$]+\$$/.test(source)) {
      el.className = 'equation-block';
      katex.render(source.slice(1, -1), el, { displayMode: true, throwOnError: false });
    } else el.innerHTML = marked.parse(source, { breaks: false });
    el.querySelectorAll('a').forEach(a => a.setAttribute('href', internalLink(a.getAttribute('href'))));
    return el;
  }
  if (type === 'equation') {
    const el = document.createElement('div'); el.className = 'math-block';
    katex.render(component.text || '', el, { displayMode: true, throwOnError: false });
    return el;
  }
  const tags = ['div', 'a', 'img', 'iframe', 'br', 'span', 'h1', 'h2', 'h3', 'button', 'label'];
  if (!tags.includes(type)) throw new Error(`Unsupported slide element: ${type}`);
  const el = document.createElement(type);
  for (const key of ['src', 'href', 'width', 'height', 'download']) {
    if (attrs[key] != null) el.setAttribute(key, internalLink(String(attrs[key])));
  }
  if (type === 'img') { el.alt = attrs.alt || 'Research illustration'; el.loading = 'lazy'; }
  if (type === 'iframe') { el.title = attrs.title || 'Interactive experiment results'; el.loading = 'lazy'; }
  if (type === 'button') el.type = 'button';
  if (children != null) el.append(render(children));
  return el;
}

function showSlide() {
  const match = /^#\/(\d+)$/.exec(location.hash);
  index = Math.max(0, Math.min(slides.length - 1, match ? Number(match[1]) : 0));
  const playground = index === 13;
  document.body.classList.toggle('playground-mode', playground);
  $('playground').hidden = !playground;
  $('slide-title').replaceChildren(render(slides[index].title));
  // Slide 13's old hosting warning is superseded by the local playground.
  $('slide-content').replaceChildren(...(playground ? [] : [render(slides[index].content)]));
  $('slide-select').value = String(index);
  $('slide-counter').textContent = `${index + 1} / ${slides.length}`;
  $('previous').disabled = index === 0; $('next').disabled = index === slides.length - 1;
  if (!playground) arrangeSlide($('slide-content'), index);
  if (playground) { ensureWorker(); requestAnimationFrame(draw); }
  else if (worker && state === 'running') worker.postMessage({ type: 'pause' });
}
function navigate(n) { location.hash = `/${Math.max(0, Math.min(slides.length - 1, n))}`; }
$('previous').onclick = () => navigate(index - 1);
$('next').onclick = () => navigate(index + 1);
$('slide-select').onchange = e => navigate(Number(e.target.value));
window.addEventListener('hashchange', showSlide);
window.addEventListener('keydown', e => {
  if (e.target.closest('input,select,textarea,button') || e.altKey || e.ctrlKey || e.metaKey) return;
  if (e.key === 'ArrowRight') { e.preventDefault(); navigate(index + 1); }
  if (e.key === 'ArrowLeft') { e.preventDefault(); navigate(index - 1); }
});
$('fullscreen').onclick = async () => {
  try { if (document.fullscreenElement) await document.exitFullscreen(); else await document.documentElement.requestFullscreen(); } catch {}
};
document.addEventListener('fullscreenchange', () => { $('fullscreen').textContent = document.fullscreenElement ? 'Exit fullscreen ⛶' : 'Fullscreen ⛶'; });

function readConfig() {
  const values = new FormData(form);
  const seed = crypto.getRandomValues(new Uint32Array(1))[0];
  const result = { model: values.get('model'), seed };
  for (const name of ['predators', 'prey', 'predatorRange', 'preyRange', 'sensing', 'capture', 'steps']) result[name] = Number(values.get(name));
  return result;
}
function setStatus(next) {
  state = next;
  $('parameters').disabled = next === 'running' || next === 'paused';
  $('run').disabled = !workerReady || next === 'running';
  $('run').textContent = !workerReady ? 'Loading simulator…' : next === 'paused' ? 'Resume' : next === 'complete' ? 'Run again' : 'Run';
  $('pause').disabled = next !== 'running'; $('reset').disabled = !workerReady;
  $('export').disabled = !latest;
  const messages = { ready: 'Ready. Press Run to begin.', running: 'Running on your device.', paused: 'Paused. Resume to continue this run.', complete: latest?.[4] >= latest?.[3] ? 'Finished: all prey captured.' : 'Finished: step limit reached.', error: 'Simulation stopped.' };
  const message = messages[next] || 'Preparing local simulator.';
  if ($('run-status').textContent !== message) $('run-status').textContent = message;
}
function fail(message) { $('simulation-error').hidden = false; $('simulation-error').textContent = message; setStatus('error'); }
function newRun(run = false) {
  // Re-enable settings before reading them: disabled fields are absent in FormData.
  $('parameters').disabled = false;
  if (!form.reportValidity()) { setStatus(state); return; }
  config = readConfig(); bounds = undefined; $('simulation-error').hidden = true;
  worker.postMessage({ type: 'init', config, run });
}
function ensureWorker() {
  if (worker) return;
  worker = new Worker(new URL('./simulation-worker.js', import.meta.url), { type: 'module' });
  worker.onerror = e => fail(`Simulator error: ${e.message}`);
  worker.onmessage = ({ data }) => {
    if (data.type === 'ready') { workerReady = true; worker.postMessage({ type: 'pace', value: Number($('pace').value) }); newRun(); }
    else if (data.type === 'error') fail(data.message);
    else if (data.type === 'frame') {
      latest = data.frame; setStatus(data.status);
      $('sim-time').textContent = `${latest[1].toFixed(2)} s`;
      $('captured').textContent = `${latest[4]} / ${latest[3]}`;
      $('pred-order').textContent = Number.isFinite(latest[5]) ? latest[5].toFixed(3) : '—';
      $('prey-order').textContent = Number.isFinite(latest[6]) ? latest[6].toFixed(3) : '—';
      $('step-count').textContent = `Step ${latest[0]} / ${config.steps}`;
      draw();
    }
  };
}
form.onsubmit = e => { e.preventDefault(); if (!workerReady || state === 'running') return; if (state === 'paused') worker.postMessage({ type: 'run' }); else newRun(true); };
$('pause').onclick = () => worker?.postMessage({ type: 'pause' });
$('reset').onclick = () => newRun(false);
$('pace').oninput = e => { $('pace-label').textContent = `${e.target.value}×`; worker?.postMessage({ type: 'pace', value: Number(e.target.value) }); };
$('fit').onclick = () => { bounds = undefined; draw(); };
document.addEventListener('visibilitychange', () => { if (document.hidden && state === 'running') worker?.postMessage({ type: 'pause' }); });

function draw() {
  if (!latest || $('playground').hidden) return;
  const rect = canvas.getBoundingClientRect();
  if (rect.width < 1 || rect.height < 1) return;
  const dpr = Math.min(2, window.devicePixelRatio || 1);
  const width = rect.width, height = rect.height;
  if (canvas.width !== Math.round(width * dpr) || canvas.height !== Math.round(height * dpr)) { canvas.width = Math.round(width * dpr); canvas.height = Math.round(height * dpr); }
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, width, height);
  const n = latest[2], m = latest[3], agents = [];
  for (let i = 0; i < n + m; i++) {
    const o = 8 + i * 5, prey = i >= n;
    if (prey && latest[o + 4] === -1) continue;
    agents.push({ x: latest[o], y: latest[o + 1], angle: latest[o + 2], prey, sensing: latest[o + 3] !== 0 });
  }
  const xs = agents.map(a => a.x), ys = agents.map(a => a.y);
  const needed = { minX: Math.min(...xs) - 2, maxX: Math.max(...xs) + 2, minY: Math.min(...ys) - 2, maxY: Math.max(...ys) + 2 };
  if (!bounds) bounds = needed;
  else bounds = { minX: Math.min(bounds.minX, needed.minX), maxX: Math.max(bounds.maxX, needed.maxX), minY: Math.min(bounds.minY, needed.minY), maxY: Math.max(bounds.maxY, needed.maxY) };
  const scale = Math.min((width - 50) / (bounds.maxX - bounds.minX), (height - 40) / (bounds.maxY - bounds.minY));
  const cx = (bounds.minX + bounds.maxX) / 2, cy = (bounds.minY + bounds.maxY) / 2;
  const px = x => width / 2 + (x - cx) * scale, py = y => height / 2 - (y - cy) * scale;
  ctx.strokeStyle = '#223348'; ctx.lineWidth = 1; ctx.fillStyle = '#698196'; ctx.font = '10px system-ui';
  const unit = Math.max(1, 10 ** Math.floor(Math.log10(70 / scale)));
  for (let x = Math.ceil((cx - width / scale / 2) / unit) * unit; x < cx + width / scale / 2; x += unit) {
    ctx.beginPath(); ctx.moveTo(px(x), 0); ctx.lineTo(px(x), height); ctx.stroke(); ctx.fillText(x.toFixed(0), px(x) + 4, height - 7);
  }
  for (let y = Math.ceil((cy - height / scale / 2) / unit) * unit; y < cy + height / scale / 2; y += unit) {
    ctx.beginPath(); ctx.moveTo(0, py(y)); ctx.lineTo(width, py(y)); ctx.stroke(); ctx.fillText(y.toFixed(0), 5, py(y) - 4);
  }
  for (const a of agents) {
    ctx.save(); ctx.translate(px(a.x), py(a.y)); ctx.rotate(-a.angle);
    ctx.fillStyle = a.prey ? '#ffad55' : a.sensing ? '#55bcef' : '#99a7bd';
    const size = Math.max(3, Math.min(6, scale * .16));
    ctx.beginPath(); ctx.moveTo(size * 1.55, 0); ctx.lineTo(-size, -size * .8); ctx.lineTo(-size * .45, 0); ctx.lineTo(-size, size * .8); ctx.closePath(); ctx.fill(); ctx.restore();
  }
}
new ResizeObserver(draw).observe(canvas);
$('export').onclick = () => {
  if (!latest) return;
  const n = latest[2], m = latest[3];
  const row = i => Array.from(latest.slice(8 + i * 5, 13 + i * 5));
  const output = { schema: 'thesis-presentation.snapshot.v1', model: 'published DM/ADM model', config, dt: .05, step: latest[0], simulationTime: latest[1], captured: latest[4], predatorColumns: ['x', 'y', 'heading', 'sensing', 'id'], preyColumns: ['x', 'y', 'heading', 'id', 'status'], predators: Array.from({ length: n }, (_, i) => row(i)), prey: Array.from({ length: m }, (_, i) => row(n + i)) };
  const url = URL.createObjectURL(new Blob([JSON.stringify(output, null, 2)], { type: 'application/json' }));
  const a = document.createElement('a'); a.href = url; a.download = `predator-prey-step-${latest[0]}.json`; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
};

try {
  const response = await fetch(new URL('./slides.json', import.meta.url));
  if (!response.ok) throw new Error(`Slide request failed (${response.status})`);
  slides = await response.json();
  slides.forEach((slide, i) => { const option = document.createElement('option'); const title = typeof slide.title === 'string' ? slide.title : 'Introduction & outline'; option.value = i; option.textContent = `${String(i).padStart(2, '0')} · ${title}`; $('slide-select').append(option); });
  showSlide();
} catch (error) { $('slide-content').textContent = `Unable to load this presentation: ${error.message}`; }
