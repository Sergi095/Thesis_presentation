# Laboratory simulator

The second simulator is available at `#/lab`, alongside the original 2D
playground at `#/13`. Both retain the published DM/ADM swarm equations.

## Physical model

- Lab interior: 4.40 × 7.90 × 2.20 m, taken from the physical-lab configuration.
- Crazyflie CF2X mass: 0.027 kg. Principal inertia: 1.4e-5, 1.4e-5, 2.17e-5 kg m².
- Rotor locations: (±0.028, ±0.028, 0) m, using the CF2X URDF link locations.
- Thrust coefficient: 3.16e-10 N/RPM²; torque coefficient: 7.94e-12 Nm/RPM².
- Collision shape: cylinder of radius 0.06 m and height 0.025 m.
- Gravity: 9.8 m/s². Bullet simulates rigid-body motion and contacts at 240 Hz.
- The standard DSLPIDControl position/attitude controller computes motor RPMs
  at 240 Hz. Net body thrust and rotor moments are transformed into world forces
  and torques before each physical step.

`ammojs3@0.0.11` provides Bullet through WebAssembly; Three.js displays the lab.
This is not the Python PyBullet API and should not be described as an identical
PyBullet execution. No aerodynamic drag, ground effect or downwash is added.
Bullet's small default-style rigid-body damping (0.04) is applied; this is not
an aerodynamic model. Walls, floor and ceiling are physical collision objects.
Front walls and ceiling are outlined rather than filled for visibility.

## Swarm coupling and initial conditions

Every 0.05 s, observed physical XY positions and yaw are supplied to the existing
Rust controller. The original update produces desired XY positions/headings;
the lab converts displacement to velocity setpoints. The controller's ideal
positions are then discarded. The flight controller tracks these held targets
while Bullet integrates twelve physical steps. This retains the swarm's original
noise as command noise, rather than teleporting physical drones.

The 2D simulator's updates are unchanged. The laboratory adapter uses separate
exports. Capture decisions from speculative swarm updates are discarded; lab
captures require actual three-dimensional separation within the selected radius.
Captured prey leave the physical world and future swarm interactions.

Default settings are five predators and four prey, both at 0.60 m altitude.
Initial grids use 0.50 m spacing, centred across the lab at Y=4.8 m for predators
and Y=2.5 m for prey. Headings use fresh random draws. All predators sense prey.
The selectable maximum is twelve agents per swarm so the initial grids fit the
lab. These are demonstration initial conditions, not a reproduction of any HPC
experiment configuration. There is no additional wall-avoidance or geofence law.

Default capture distance is 0.15 m, slightly above the 0.12 m collision diameter;
the user can change it. Values below the body diameter can make contact captures
infeasible when drones remain level at the same height. The original 2D default
remains 0.1. Runs stop when all prey are captured or the duration is reached.

## Validation

`node tests/lab-physics.mjs` checks:

- 32 sequential controller calls against recorded Python DSLPIDControl outputs.
  The fixture uses synthetic inputs and checks the PID integrator state as well
  as individual motor RPMs (maximum observed difference 1.46e-11 RPM).
- Hover thrust equals weight and symmetric motors produce zero net torque.
- A ten-second coupled run maintains the altitude setpoint within 3 cm.
- Unpowered free fall, floor/wall collision, and capture using physical position.

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
