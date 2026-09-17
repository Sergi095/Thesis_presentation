import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import assert from 'node:assert/strict';
const native = JSON.parse(execFileSync('cargo', ['run', '--locked', '--quiet', '--manifest-path', 'wasm/Cargo.toml', '--example', 'browser_reference'], { encoding: 'utf8' }));
const { assets } = JSON.parse(readFileSync('dist/build.json'));
const { instance } = await WebAssembly.instantiate(readFileSync(`dist/${assets.core}`), {});
const c = instance.exports;
assert.equal(c.simulation_init(12, 7, 3, 3, .5, 1, .1, 314159), 0);
assert.equal(c.simulation_step(100), 0);
const ptr = c.simulation_snapshot();
const actual = new Float64Array(c.memory.buffer, ptr, c.simulation_snapshot_len());
assert.equal(actual.length, native.length);
let error = 0;
for (let i = 0; i < native.length; i++) { error = Math.max(error, Math.abs(native[i] - actual[i])); assert.ok(Math.abs(native[i] - actual[i]) < 1e-9, `WASM/native mismatch at ${i}`); }
console.log(`Actual WebAssembly module matches native Rust after 100 steps; max error ${error}.`);
