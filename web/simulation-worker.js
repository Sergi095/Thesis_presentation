let core, config, running = false, timer, pace = 10;
const ready = (async () => {
  const result = await WebAssembly.instantiateStreaming(fetch(new URL(__CORE_ASSET__, import.meta.url)), {});
  core = result.instance.exports;
  postMessage({ type: 'ready' });
})();
ready.catch(error => postMessage({ type: 'error', message: `Could not load the simulator: ${error.message}` }));

function frame() {
  const ptr = core.simulation_snapshot();
  // Copy before transferring: the Rust allocation remains owned by the core.
  return new Float64Array(core.memory.buffer, ptr, core.simulation_snapshot_len()).slice();
}
function publish(status) {
  const data = frame();
  postMessage({ type: 'frame', status, frame: data }, [data.buffer]);
}
function pause() { running = false; clearTimeout(timer); }
function pump() {
  if (!running) return;
  const start = performance.now();
  let current = frame();
  const quota = Math.max(1, Math.round(20 * pace / 30));
  for (let i = 0; i < quota && performance.now() - start < 10; i++) {
    if (current[0] >= config.steps || current[4] >= current[3]) break;
    if (core.simulation_step(1) !== 0) {
      pause();
      postMessage({ type: 'error', message: 'The model reached a non-finite state. Start a new run or change the parameters.' });
      return;
    }
    current = frame();
  }
  const finished = current[0] >= config.steps || current[4] >= current[3];
  if (finished) pause();
  postMessage({ type: 'frame', status: finished ? 'complete' : 'running', frame: current }, [current.buffer]);
  if (running) timer = setTimeout(pump, Math.max(0, 1000 / 30 - (performance.now() - start)));
}
self.onmessage = async ({ data }) => {
  try {
    await ready;
    if (data.type === 'init') {
      pause();
      config = data.config;
      if (!Number.isInteger(config.steps) || config.steps < 1 || config.steps > 100000) throw new Error('Invalid step limit.');
      const result = core.simulation_init(config.predators, config.prey, config.predatorRange, config.preyRange,
        config.sensing / 100, config.model === 'adm' ? 1 : 0, config.capture, config.seed);
      if (result !== 0) throw new Error('Invalid simulation parameters.');
      publish('ready');
      if (data.run) { running = true; pump(); }
    } else if (data.type === 'run') {
      if (!config) throw new Error('Initialize a run first.');
      if (!running) { running = true; pump(); }
    } else if (data.type === 'pause') { pause(); if (config) publish('paused'); }
    else if (data.type === 'pace') {
      if (Number.isFinite(data.value)) pace = Math.max(1, Math.min(50, data.value));
    }
  } catch (error) {
    pause();
    postMessage({ type: 'error', message: error.message });
  }
};
