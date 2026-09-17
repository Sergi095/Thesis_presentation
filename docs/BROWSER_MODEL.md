# Browser model and numerical verification

The scientific reference is the published Python simulator, preserved verbatim
as `tests/reference/published_sim.py` for numerical tests only. Its original
location was `sim.py`; controller parameters came from `app.py` at commit
`29a0a54`. The Dash application, server entry points, dependencies and Docker
configuration have been removed. This port does not include subsequent
Thesis/HPC cases, datasets or unpublished results.

## What is preserved

- Original grid layout, random headings and diagonal population offset.
- Sensor assignment rule, including farthest-first selection and its tie order.
- DM/ADM proximal equations, sensing radii and cutoffs.
- The exact NumPy source-row/receiver-column modulation and force accumulation.
  This detail matters: the receiver's signal is broadcast across sensing source
  rows. It has not been replaced with a superficially similar vector expression.
- Direct prey repulsion away from the mean position of visible predators.
- Body-frame projection, speed and turning saturation, dt=0.05 and independent
  uniform displacement noise corresponding to velocity noise in [-0.05, 0.05].
- Both swarm forces are evaluated from the old positions before either update.
- Inclusive capture distance, capture after movement, and removal of captured
  prey from future forces. The displayed capture-distance default remains 0.1.
- The unbounded arena; the old `boundaries` argument does not apply wall forces
  in `sim.py` and no walls were added to the browser model.

The browser exposes the existing configurable playground settings and capture
distance. Other controller constants retain the original `app.py` values. Prey
use DM in the published playground. The Rust core also tests the original
`pdm_prey` option but the web UI does not introduce it as a new experiment.

## Deliberate runtime differences

1. Rust uses SplitMix64 instead of NumPy's PRNG. Every New run receives a fresh
   browser `crypto.getRandomValues` seed. A numeric seed does **not** identify the
   same initial state or trajectory across the Python and browser implementations.
2. The browser worker stops scheduling at the requested step limit or after all
   prey are captured. Pause, rendering cadence and automatic pause when leaving
   the tab/slide are execution controls; they do not change the time step.
3. Parameter validation limits browser populations to 1–200 per swarm. A numerical
   singularity is reported and stops the run; it is not silently regularized.
4. Arithmetic order/libm differences can cause roundoff differences and later
   divergence in a nonlinear stochastic simulation. This is not a claim of
   bit-for-bit cross-platform trajectories or statistical equivalence of all
   long-run distributions.

## Tests

`tests/physics_parity.py` supplies identical initial states and explicit noise to
the unchanged Python simulator and Rust, checking every agent at every step.
Twelve 100-step scenarios cover DM/ADM, different populations, mixed/absent
sensors, singleton swarms, no visibility, broad visibility and captures.

`tests/wasm_parity.mjs` executes the actual compiled `.wasm` in a WebAssembly
runtime and compares a 100-step stochastic trajectory with native Rust using
the same generator and seed. Browser integration tests execute that module in
Chrome/Chromium in a Web Worker, including pause/resume, capture termination,
input validation, downloaded state, independent tabs and GitHub Pages subpaths.

Random seeds in tests are reproducible fixtures only. User runs use fresh entropy.

## Architecture and privacy

GitHub Actions compiles Rust and bundles the static website. GitHub Pages serves
those files. Each visitor's Web Worker owns one simulation and executes its steps
on that visitor's device. The main thread draws a Canvas frame and updates UI.
There is no Dash/Flask service, simulation API, VPS, account, Supabase dependency,
analytics or results upload. Plotly and KaTeX are bundled locally as well.

The 16 original slides are stored as static content in `web/slides.json`. The
site build uses Node.js and Rust. Python and NumPy are used only by the numerical
reference tests. Existing images, animations, PDF and interactive result plots
are reused.
The old slide-13 warning about slow server hosting is replaced by the browser
playground. Hash navigation works under `/Thesis_presentation/` without rewrites.
Generated site files and test screenshots are ignored by Git and deployed as a
CI artifact. Existing published assets remain the only scientific assets.

The Download current state action exports parameters, seed, step and positions/
headings/statuses at that moment. It does not save all trajectory steps. This is
an interactive presentation, not an HPC data-collection replacement.
