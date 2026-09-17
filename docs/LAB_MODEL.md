# Laboratory simulator

The second simulator is available at `#/lab`, alongside the original 2D
playground at `#/13`. The laboratory follows the current thesis bounded PyBullet profile,
without a target. The original 2D playground retains its published controller.

## Physical model

- Lab interior: 4.40 × 7.90 × 2.20 m, taken from the physical-lab configuration.
- Crazyflie CF2X mass: 0.027 kg. Principal inertia: 1.4e-5, 1.4e-5, 2.17e-5 kg m².
- Rotor locations: (±0.028, ±0.028, 0) m, using the CF2X URDF link locations.
- Thrust coefficient: 3.16e-10 N/RPM²; torque coefficient: 7.94e-12 Nm/RPM².
- Collision shape: cylinder of radius 0.06 m and height 0.025 m.
- Gravity: 9.8 m/s². Bullet simulates rigid-body motion and contacts at 240 Hz.
- The standard DSLPIDControl position/attitude controller computes motor RPMs
  at 120 Hz, holding RPMs for two physics steps. Net body thrust and rotor moments are transformed into world forces
  and torques before each physical step.

`ammojs3@0.0.11` provides Bullet through WebAssembly; Three.js displays the lab.
This is not the Python PyBullet API and should not be described as an identical
PyBullet execution. No aerodynamic drag, ground effect or downwash is added.
Bullet's small default-style rigid-body damping (0.04) is applied; this is not
an aerodynamic model. Walls, floor and ceiling are physical collision objects.
Front walls and ceiling are outlined rather than filled for visibility.

## Swarm coupling and initial conditions

Every 0.05 s, measured physical XY positions are supplied to the Rust controller.
The high-level heading integrator is retained between calls, independently of
measured body yaw, exactly as in `SimulationV2PyBulletAdapter.synchronize_state`.
Velocity commands include the scaled uniform motion noise. The PID receives the
commanded yaw **and yaw rate**, with XY position targets reset to measured XY at
each 120 Hz update (PyBullet velocity mode). Bullet determines the actual motion.

The laboratory controller uses the bounded test profile: DM for both roles by
default, optional predator ADM, `rep_mode=grad_rep`, lambda=0.2 for both roles,
with positive predator and negative prey modulation of interaction spacing.
The nominal sigmas are 0.7 for DM and sqrt(2)×0.7 for ADM, both scaled once by
0.3. All interaction cutoffs are 3.5×0.3. The canonical distance epsilon and
source-row/receiver-column broadcasting are retained. There is no extra direct
prey-repulsion force and no target force. See `wasm/src/lab.rs`.

Default populations are five predators and four prey, at 0.60 m and 0.50 m
respectively, matching `run_bounded_test.sh`. Initial positions use the thesis
force-balanced hexagonal formations, rotated along the long lab axis and placed
with an exact minimum cross-swarm XY gap of 0.5×effective R: **0.45 m at R=3**.
This replaces the earlier arbitrary grids, whose centres were 2.3 m apart and
outside sensing range. Both formations are translated together to the arena
centre, preserving their shape and gap. Headings use fresh random draws.
The formation coordinates are generated formula outputs, not research data.

Capture is checked on measured **XY distance at 20 Hz**, matching the planar
PyBullet adapter. The default nominal capture setting remains 0.5 (effective
0.15 m); the bounded thesis shell script defaults to 0.1 unless overridden.
Captured agents leave swarm interactions and are hidden/removed in this demo;
the thesis runner instead lands them. Runs stop when all prey are captured or
the selected duration is reached. The original 2D simulator is unchanged.

## 0.30 parameter scale and boundary repulsion

Scaling follows `scale_controller_parameters(..., 0.30, scale_speed_caps=False)`
in the thesis `swarm/implementing_paper/simulation_v2/simulation_parameters.py`
and its use in `swarm/3D_implementation/Prey_Predator/run.py`.
The laboratory uses the nominal controller parameters of the current bounded
PyBullet test; the original 2D presentation model remains isolated.

| Parameter | Laboratory treatment |
| --- | --- |
| Predator/prey sensing and capture radius | Input × 0.30, once |
| All interaction sigmas and cutoffs | Current thesis value × 0.30 |
| Motion noise | ±0.05 becomes ±0.015 before multiplication by dt |
| Direct prey-repulsion gain | Disabled in gradient mode |
| Boundary weight gamma | Explicitly enabled at nominal 1; effective 0.30 |
| Speed caps, unicycle gains, dt, angular caps, epsilon | Unchanged |
| Dimensionless alpha / lambda | alpha=1, lambda=0.2, unscaled |
| Fixed boundary constants | k_rep=2; L0=Dr=0.50 m, unchanged |
| Lab geometry, spawn centres, altitude, drone mass/inertia, PID | Physical values, unchanged |

Both swarms receive the canonical `planarEnvVEC.r_vector` wall force before
the unicycle update. For each wall at distance `d < 0.50 m`, its inward
contribution is `2 × (1/d − 1/0.50) / d³`, weighted by gamma=0.30.
The original exact-on-wall fallback substitutes d=0.50; no clipping,
reflection or new boundary law is introduced. Physical walls remain present.
The field is horizontal; altitude is controlled by the flight PID.

The current thesis default gamma is zero, which disables that existing field.
The presentation explicitly enables it to satisfy the requested wall repulsion;
this is a documented configuration difference, not an assertion that the thesis
default already uses a nonzero boundary weight. There is no target, target force,
target-reaching status or target-triggered pursuit phase.

The UI accepts nominal sensing/capture settings and displays effective metres.
Downloaded states include both `config` and `effective` values, including scale,
boundary weight/radius, speed limit and `target: false`. The laboratory setup
rejects a second scale application; starting the 2D model resets scaling entirely.

## Validation

`node tests/lab-physics.mjs` checks:

- 32 sequential controller calls against recorded Python DSLPIDControl outputs.
  The fixture uses synthetic inputs and checks the PID integrator state as well
  as individual motor RPMs (maximum observed difference 1.46e-11 RPM).
- Another 32 sequential Python PID reference calls at 120 Hz with nonzero yaw-rate commands.
- Hover thrust equals weight and symmetric motors produce zero net torque.
- A ten-second coupled run maintains the altitude setpoint within 3 cm.
- Unpowered free fall, floor/wall collision, and capture using physical position.
- Scaled capture thresholds and actual WASM wall responses for both roles.

Rust tests check the boundary formula on every wall, at corners, at the cutoff
and exactly on a wall; scaled sigmas, cutoffs and noise; unchanged speed/angular
caps; single-application scaling and reset isolation from the original model.
Sixteen synthetic reference cases compare both swarm force fields directly with
the current thesis Python implementation, covering DM/ADM, disabled sensors,
near-wall states and signed prey-sigma modulation. Reference fixtures and
formation tables can be regenerated with
`python tests/generate-lab-reference.py /path/to/Thesis`. No experiments run.

The PID fixture was generated from the existing CF2X DSLPIDControl implementation
(SHA-256 `3a73314023cc48b2c089a894dd8da422ffb3e16c2d156d8defd01bc1fc7a51af`).
It contains synthetic unit-test states only, not experimental results.

Browser tests exercise the actual worker, WebGL view, pause/resume, export,
duration limit, mobile layout, and switching back to the original simulator.
Runtime scripts, workers and the swarm WASM module have content-based filenames
so a newer worker cannot reuse a cached pre-laboratory `core.wasm`. Browser
tests inject obsolete files at the old URLs and verify they are never loaded.
The laboratory also checks required module exports before enabling Run.
The original Python/Rust trajectory checks and native/WASM checks still run.
These checks validate components and coupling; they do not establish matching
long-run trajectories or experimental outcome distributions across engines.

See [third-party attribution](THIRD_PARTY.md).

## Run the corresponding PyBullet configuration

From the Thesis checkout, activate its existing environment and run:

```bash
conda activate swarm
cd ~/repos/Thesis/swarm/3D_implementation/Prey_Predator
bash run_bounded_test.sh --capture_distance 0.5 --gamma 1
```

This uses five predators/four prey, DM, R=3, scale=0.3, lambda=0.2,
20 Hz swarm / 120 Hz PID / 240 Hz physics, and no target. `--gamma 1` enables
the same wall field (effective gamma=0.3); it is zero in the script's defaults.
Use `--pdm True` for the optional predator ADM setting.

To save a headless run, supply a new output directory:

```bash
bash run_bounded_test.sh --capture_distance 0.5 --gamma 1 \
  --gui False --plot False --save \
  --output_folder "$HOME/pybullet-lab-results/run-$(date +%Y%m%d-%H%M%S)"
```

The existing script uses a 30,000-step horizon. `--save` requests its full
trajectory output; the normal preview does not save it. These commands launch
individual bounded runs, not the separate multi-case August experiment batch.
