//! Port of this repository's sim.py, not the newer Thesis/HPC simulator.
//! Keep the source-row / receiver-column force convention and NumPy broadcasts.
use std::cell::RefCell;
use std::f64::consts::{PI, TAU};

pub const DT: f64 = 0.05;
pub type Agent = [f64; 5];

#[derive(Clone, Copy, Debug)]
pub struct Config {
    pub predator_range: f64,
    pub prey_range: f64,
    pub sensing_fraction: f64,
    pub adm: bool,
    pub prey_adm: bool,
    pub capture_distance: f64,
}
impl Default for Config {
    fn default() -> Self {
        Self {
            predator_range: 3.,
            prey_range: 3.,
            sensing_fraction: 1.,
            adm: true,
            prey_adm: false,
            capture_distance: 0.1,
        }
    }
}
impl Config {
    fn valid(&self) -> bool {
        [
            self.predator_range,
            self.prey_range,
            self.sensing_fraction,
            self.capture_distance,
        ]
        .iter()
        .all(|x| x.is_finite())
            && (0.0..=100.0).contains(&self.predator_range)
            && (0.0..=100.0).contains(&self.prey_range)
            && (0.0..=1.0).contains(&self.sensing_fraction)
            && (0.001..=5.0).contains(&self.capture_distance)
    }
}

#[derive(Clone)]
struct Random(u64);
impl Random {
    // SplitMix64. Browser supplies a fresh crypto seed. This is deliberately
    // documented as a different stream from NumPy, not seed-identical output.
    fn unit(&mut self) -> f64 {
        self.0 = self.0.wrapping_add(0x9e3779b97f4a7c15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94d049bb133111eb);
        z ^= z >> 31;
        ((z >> 11) as f64) / ((1u64 << 53) as f64)
    }
    fn noise(&mut self, n: usize) -> Vec<f64> {
        (0..n).map(|_| (2. * self.unit() - 1.) * 0.05).collect()
    }
}

pub struct Noise {
    pub predator_x: Vec<f64>,
    pub predator_y: Vec<f64>,
    pub prey_x: Vec<f64>,
    pub prey_y: Vec<f64>,
}

pub struct Simulation {
    pub config: Config,
    pub predators: Vec<Agent>,
    pub prey: Vec<Agent>,
    pub steps: u32,
    rng: Random,
    lab_bounds: Option<[f64; 2]>,
}

// Same bounded-controller scaling policy as the thesis PyBullet adapter.
// Physical geometry, epsilon, dt, unicycle gains and speed caps are exempt.
const LAB_SCALE: f64 = 0.3;

fn boundary_force(a: &Agent, bounds: [f64; 2]) -> [f64; 2] {
    let mut force = [0., 0.];
    // Canonical planarEnvVEC.r_vector: k_rep=2, L0=Dr=0.5.
    for (axis, wall, direction) in [
        (0, 0., 1.),
        (0, bounds[0], -1.),
        (1, 0., 1.),
        (1, bounds[1], -1.),
    ] {
        let mut d = (a[axis] - wall).abs();
        if d < 0.5 {
            if d == 0. {
                d = 0.5;
            }
            force[axis] += direction * 2. * (1. / d - 1. / 0.5) / d.powi(3);
        }
    }
    force
}

fn distance(a: &Agent, b: &Agent) -> f64 {
    ((a[0] - b[0]).powi(2) + (a[1] - b[1]).powi(2)).sqrt()
}

impl Simulation {
    pub fn new(n: usize, m: usize, config: Config, seed: u64) -> Result<Self, &'static str> {
        if !(1..=200).contains(&n) || !(1..=200).contains(&m) || !config.valid() {
            return Err("Invalid configuration");
        }
        let mut rng = Random(seed);
        let side = (n as f64).sqrt().ceil() as usize;
        let mut predators: Vec<Agent> = (0..n)
            .map(|i| {
                [
                    (i / side) as f64 * 0.5 + 0.25,
                    (i % side) as f64 * 0.5 + 0.25,
                    rng.unit() * TAU,
                    1.,
                    i as f64,
                ]
            })
            .collect();
        let gap = (m as f64).sqrt() * 0.7 * 0.5
            + config.predator_range / if m >= 100 { 10. } else { 1.5 };
        let sx = if rng.unit() < 0.5 { -1. } else { 1. };
        let sy = if rng.unit() < 0.5 { -1. } else { 1. };
        let side = (m as f64).sqrt().ceil() as usize;
        let prey: Vec<Agent> = (0..m)
            .map(|i| {
                [
                    (i / side) as f64 * 0.5 + 0.25 + sx * gap,
                    (i % side) as f64 * 0.5 + 0.25 + sy * gap,
                    rng.unit() * TAU,
                    i as f64,
                    1.,
                ]
            })
            .collect();
        let off = 1. - config.sensing_fraction;
        let k = (off * n as f64) as usize;
        let mut indexes: Vec<usize> = (0..n).collect();
        if off >= 0.10 {
            let nearest: Vec<f64> = predators
                .iter()
                .map(|p| {
                    prey.iter()
                        .map(|q| distance(p, q))
                        .fold(f64::INFINITY, f64::min)
                })
                .collect();
            indexes.sort_by(|&a, &b| nearest[a].total_cmp(&nearest[b]).then(a.cmp(&b)));
            indexes.reverse();
        } else {
            for i in 0..k {
                let j = i + (rng.unit() * (n - i) as f64) as usize;
                indexes.swap(i, j);
            }
        }
        for &i in indexes.iter().take(k) {
            predators[i][3] = 0.;
        }
        Ok(Self {
            config,
            predators,
            prey,
            steps: 0,
            rng,
            lab_bounds: None,
        })
    }

    pub fn from_state(
        config: Config,
        predators: Vec<Agent>,
        prey: Vec<Agent>,
        seed: u64,
    ) -> Result<Self, &'static str> {
        if !config.valid()
            || predators.is_empty()
            || prey.is_empty()
            || predators.len() > 200
            || prey.len() > 200
            || !predators
                .iter()
                .chain(prey.iter())
                .flatten()
                .all(|v| v.is_finite())
        {
            return Err("Invalid state");
        }
        Ok(Self {
            config,
            predators,
            prey,
            steps: 0,
            rng: Random(seed),
            lab_bounds: None,
        })
    }

    pub fn active_count(&self) -> usize {
        self.prey.iter().filter(|p| p[4] != -1.).count()
    }

    pub fn step(&mut self) -> Result<(), &'static str> {
        let n = self.predators.len();
        let m = self.active_count();
        let noise = Noise {
            predator_x: self.rng.noise(n),
            predator_y: self.rng.noise(n),
            prey_x: self.rng.noise(m),
            prey_y: self.rng.noise(m),
        };
        self.step_with_noise(&noise)
    }

    pub fn step_with_noise(&mut self, noise: &Noise) -> Result<(), &'static str> {
        let active: Vec<usize> = self
            .prey
            .iter()
            .enumerate()
            .filter(|(_, a)| a[4] != -1.)
            .map(|(i, _)| i)
            .collect();
        if noise.predator_x.len() != self.predators.len()
            || noise.predator_y.len() != self.predators.len()
            || noise.prey_x.len() != active.len()
            || noise.prey_y.len() != active.len()
        {
            return Err("Invalid noise arrays");
        }
        let prey: Vec<Agent> = active.iter().map(|&i| self.prey[i]).collect();
        let mut signal = vec![0.; self.predators.len()];
        for (i, p) in self.predators.iter().enumerate() {
            let visible: Vec<f64> = prey
                .iter()
                .map(|q| distance(p, q))
                .filter(|d| *d <= self.config.predator_range)
                .collect();
            if !visible.is_empty() {
                signal[i] = 1. / (visible.iter().sum::<f64>() / visible.len() as f64);
            }
        }
        let scale = if self.lab_bounds.is_some() {
            LAB_SCALE
        } else {
            1.
        };
        let mut pred_force = proximal(&self.predators, &signal, self.config.adm, false, scale);
        let mut prey_force = proximal(&prey, &[], self.config.prey_adm, true, scale);
        for (i, q) in prey.iter().enumerate() {
            let mut center = [0., 0.];
            let mut count = 0;
            for p in &self.predators {
                if distance(q, p) <= self.config.prey_range {
                    center[0] += p[0];
                    center[1] += p[1];
                    count += 1;
                }
            }
            if count > 0 {
                let dx = q[0] - center[0] / count as f64;
                let dy = q[1] - center[1] / count as f64;
                let gain = 2. * scale / (1. + (dx * dx + dy * dy).sqrt());
                prey_force[i][0] += gain * dx;
                prey_force[i][1] += gain * dy;
            }
        }
        if let Some(bounds) = self.lab_bounds {
            for (agents, forces) in [(&self.predators, &mut pred_force), (&prey, &mut prey_force)] {
                for (a, f) in agents.iter().zip(forces.iter_mut()) {
                    let r = boundary_force(a, bounds);
                    // Explicitly enable wall repulsion: nominal gamma=1,
                    // scaled once to 0.3, for both swarms. No target force.
                    f[0] += LAB_SCALE * r[0];
                    f[1] += LAB_SCALE * r[1];
                }
            }
        }
        let next_pred = advance_agents(
            &self.predators,
            &pred_force,
            &noise.predator_x,
            &noise.predator_y,
            scale,
        );
        let next_prey = advance_agents(&prey, &prey_force, &noise.prey_x, &noise.prey_y, scale);
        if !next_pred
            .iter()
            .chain(next_prey.iter())
            .flatten()
            .all(|v| v.is_finite())
        {
            return Err("Non-finite state: overlapping agents or a singular force");
        }
        self.predators = next_pred;
        for (k, &i) in active.iter().enumerate() {
            self.prey[i] = next_prey[k];
            if self
                .predators
                .iter()
                .any(|p| distance(p, &self.prey[i]) <= self.config.capture_distance)
            {
                self.prey[i][4] = -1.;
            }
        }
        self.steps += 1;
        Ok(())
    }

    pub fn snapshot(&self) -> Vec<f64> {
        let mut out = vec![
            self.steps as f64,
            self.steps as f64 * DT,
            self.predators.len() as f64,
            self.prey.len() as f64,
            (self.prey.len() - self.active_count()) as f64,
            order(self.predators.iter()),
            order(self.prey.iter().filter(|p| p[4] != -1.)),
            self.predators.iter().filter(|p| p[3] != 0.).count() as f64,
        ];
        out.extend(
            self.predators
                .iter()
                .chain(self.prey.iter())
                .flatten()
                .copied(),
        );
        out
    }
}

fn proximal(agents: &[Agent], signal: &[f64], adm: bool, prey: bool, scale: f64) -> Vec<[f64; 2]> {
    let n = agents.len();
    let mut force = vec![[0., 0.]; n];
    let base: Vec<f64> = agents
        .iter()
        .map(|p| {
            if prey {
                0.7
            } else if adm {
                if p[3] == 0. {
                    1.7
                } else {
                    1.4
                }
            } else if p[3] == 0. {
                0.75
            } else {
                0.7
            }
        })
        .map(|sigma| sigma * scale)
        .collect();
    let cutoff = (if prey || adm { 3.5 } else { 4. }) * scale;
    for i in 0..n {
        for j in 0..n {
            if i == j {
                continue;
            }
            let d = distance(&agents[i], &agents[j]);
            if d > cutoff {
                continue;
            }
            // Faithful to sim.py's NumPy broadcasting: source i's base and
            // sensor gate, receiver j's sensed signal and diagonal base.
            let sigma = base[i]
                + if !prey && agents[i][3] != 0. {
                    signal[j] * base[j]
                } else {
                    0.
                };
            let magnitude = if adm {
                -12. * (sigma / d - (sigma / d).sqrt())
            } else {
                -12. * (2. * sigma.powi(4) / d.powi(5) - sigma.powi(2) / d.powi(3))
            };
            let angle = (agents[i][1] - agents[j][1]).atan2(agents[i][0] - agents[j][0]);
            force[j][0] += magnitude * angle.cos();
            force[j][1] += magnitude * angle.sin();
        }
    }
    force
}

fn advance_agents(
    agents: &[Agent],
    forces: &[[f64; 2]],
    nx: &[f64],
    ny: &[f64],
    scale: f64,
) -> Vec<Agent> {
    agents
        .iter()
        .enumerate()
        .map(|(i, a)| {
            let f = forces[i];
            let angle = f[1].atan2(f[0]) - a[2];
            let mag = (f[0] * f[0] + f[1] * f[1]).sqrt();
            let u = (0.5 * mag * angle.cos() + 0.05).clamp(0., 0.15);
            let omega = (0.05 * mag * angle.sin()).clamp(-PI / 3., PI / 3.);
            let mut out = *a;
            out[0] += u * a[2].cos() * DT + nx[i] * scale * DT;
            out[1] += u * a[2].sin() * DT + ny[i] * scale * DT;
            out[2] += omega * DT;
            out
        })
        .collect()
}

fn order<'a>(agents: impl Iterator<Item = &'a Agent>) -> f64 {
    let (mut x, mut y, mut n) = (0., 0., 0);
    for a in agents {
        x += a[2].cos();
        y += a[2].sin();
        n += 1;
    }
    if n < 2 {
        f64::NAN
    } else {
        (x * x + y * y).sqrt() / n as f64
    }
}

thread_local! {
    static ENGINE: RefCell<Option<Simulation>> = const { RefCell::new(None) };
    static FRAME: RefCell<Vec<f64>> = const { RefCell::new(Vec::new()) };
}

// Single-threaded worker ABI, no JS callbacks inside the numerical loop.
#[no_mangle]
pub extern "C" fn simulation_init(
    n: u32,
    m: u32,
    pr: f64,
    qr: f64,
    fraction: f64,
    adm: u32,
    capture: f64,
    seed: u32,
) -> i32 {
    let cfg = Config {
        predator_range: pr,
        prey_range: qr,
        sensing_fraction: fraction,
        adm: adm != 0,
        capture_distance: capture,
        ..Config::default()
    };
    match Simulation::new(n as usize, m as usize, cfg, seed as u64) {
        Ok(sim) => {
            ENGINE.with(|e| *e.borrow_mut() = Some(sim));
            0
        }
        Err(_) => -1,
    }
}
#[no_mangle]
pub extern "C" fn simulation_step(count: u32) -> i32 {
    ENGINE.with(|e| {
        let mut borrow = e.borrow_mut();
        let Some(sim) = borrow.as_mut() else {
            return -1;
        };
        for _ in 0..count.min(1000) {
            if sim.step().is_err() {
                return -2;
            }
        }
        0
    })
}
#[no_mangle]
pub extern "C" fn simulation_snapshot() -> *const f64 {
    ENGINE.with(|e| {
        FRAME.with(|f| {
            *f.borrow_mut() = e
                .borrow()
                .as_ref()
                .map(|s| s.snapshot())
                .unwrap_or_default();
            f.borrow().as_ptr()
        })
    })
}
#[no_mangle]
pub extern "C" fn simulation_snapshot_len() -> usize {
    FRAME.with(|f| f.borrow().len())
}

// Enable scaled parameters once after simulation_init, never for the 2D run.
#[no_mangle]
pub extern "C" fn lab_configure(width: f64, length: f64) -> i32 {
    if ![width, length].iter().all(|v| v.is_finite() && *v > 0.) {
        return -1;
    }
    ENGINE.with(|engine| {
        let mut borrow = engine.borrow_mut();
        let Some(sim) = borrow.as_mut() else {
            return -1;
        };
        if sim.lab_bounds.is_some() {
            return -1;
        }
        sim.config.predator_range *= LAB_SCALE;
        sim.config.prey_range *= LAB_SCALE;
        sim.config.capture_distance *= LAB_SCALE;
        sim.lab_bounds = Some([width, length]);
        0
    })
}

// The lab adapter evaluates the scaled controller at measured physical poses.
// It returns setpoints; Bullet, rather than advance_agents, moves the bodies.
#[no_mangle]
pub extern "C" fn lab_set_pose(index: u32, x: f64, y: f64, yaw: f64) -> i32 {
    if ![x, y, yaw].iter().all(|v| v.is_finite()) {
        return -1;
    }
    ENGINE.with(|engine| {
        let mut borrow = engine.borrow_mut();
        let Some(sim) = borrow.as_mut() else {
            return -1;
        };
        let n = sim.predators.len();
        let agent = if (index as usize) < n {
            sim.predators.get_mut(index as usize)
        } else {
            sim.prey.get_mut(index as usize - n)
        };
        let Some(agent) = agent else {
            return -1;
        };
        agent[0] = x;
        agent[1] = y;
        agent[2] = yaw;
        0
    })
}

#[no_mangle]
pub extern "C" fn lab_mark_captured(index: u32) -> i32 {
    ENGINE.with(|engine| {
        let mut borrow = engine.borrow_mut();
        let Some(sim) = borrow.as_mut() else {
            return -1;
        };
        let Some(prey) = sim.prey.get_mut(index as usize) else {
            return -1;
        };
        prey[4] = -1.;
        0
    })
}

#[no_mangle]
pub extern "C" fn lab_commands() -> i32 {
    ENGINE.with(|engine| {
        let mut borrow = engine.borrow_mut();
        let Some(sim) = borrow.as_mut() else {
            return -1;
        };
        let predators = sim.predators.clone();
        let prey = sim.prey.clone();
        let result = sim.step();
        if result.is_ok() {
            // FRAME stores desired x,y,yaw for each physical drone. Ignore the
            // speculative capture flags: the lab tests actual 3D separation.
            FRAME.with(|frame| {
                *frame.borrow_mut() = sim
                    .predators
                    .iter()
                    .chain(sim.prey.iter())
                    .flat_map(|a| [a[0], a[1], a[2]])
                    .collect()
            });
        }
        sim.predators = predators;
        sim.prey = prey;
        if result.is_ok() {
            0
        } else {
            -2
        }
    })
}

#[no_mangle]
pub extern "C" fn lab_commands_ptr() -> *const f64 {
    FRAME.with(|frame| frame.borrow().as_ptr())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn lab_boundary_matches_thesis_field_on_each_wall_and_corner() {
        let bounds = [4.4, 7.9];
        // Canonical r_vector: 2*(1/.25-1/.5)/.25^3 = 256.
        for (x, y, expected) in [
            (0.25, 3., [256., 0.]),
            (4.15, 3., [-256., 0.]),
            (2., 0.25, [0., 256.]),
            (2., 7.65, [0., -256.]),
            (0.25, 0.25, [256., 256.]),
            (2., 3., [0., 0.]),
            (0.5, 0.5, [0., 0.]),
            // Keep the thesis' exact-on-wall fallback, not a new clamp law.
            (0., 0., [0., 0.]),
        ] {
            let actual = boundary_force(&[x, y, 0., 1., 0.], bounds);
            for k in 0..2 {
                assert!((actual[k] - expected[k]).abs() < 1e-10);
            }
        }
    }
    #[test]
    fn lab_scales_once_and_reset_restores_original_controller() {
        assert_eq!(simulation_init(1, 1, 3., 4., 1., 1, 0.5, 2), 0);
        assert_eq!(lab_configure(4.4, 7.9), 0);
        assert_eq!(lab_configure(4.4, 7.9), -1);
        ENGINE.with(|e| {
            let e = e.borrow();
            let s = e.as_ref().unwrap();
            assert!((s.config.predator_range - 0.9).abs() < 1e-15);
            assert_eq!(s.config.prey_range, 1.2);
            assert_eq!(s.config.capture_distance, 0.15);
        });
        assert_eq!(simulation_init(1, 1, 3., 4., 1., 1, 0.5, 2), 0);
        ENGINE.with(|e| {
            let e = e.borrow();
            let s = e.as_ref().unwrap();
            assert_eq!(s.config.predator_range, 3.);
            assert!(s.lab_bounds.is_none());
        });
    }
    #[test]
    fn lab_scales_sigmas_cutoffs_noise_but_not_speed_or_turn_caps() {
        let agents = [[2., 3., 0., 1., 0.], [2.3, 3., 0., 1., 1.]];
        let forces = proximal(&agents, &[], false, true, LAB_SCALE);
        let d = distance(&agents[0], &agents[1]);
        let sigma: f64 = 0.7 * LAB_SCALE;
        let expected = -12. * (2. * sigma.powi(4) / d.powi(5) - sigma.powi(2) / d.powi(3));
        assert!((forces[1][0] + expected).abs() < 1e-12);
        let far = [[2., 3., 0., 1., 0.], [3.1, 3., 0., 1., 1.]];
        assert_eq!(
            proximal(&far, &[], false, true, LAB_SCALE),
            vec![[0., 0.]; 2]
        );
        assert_ne!(proximal(&far, &[], false, true, 1.), vec![[0., 0.]; 2]);
        let moved = advance_agents(&agents[..1], &[[1e6, 1e6]], &[0.05], &[-0.05], LAB_SCALE);
        assert!((moved[0][0] - (2. + 0.15 * DT + 0.015 * DT)).abs() < 1e-15);
        assert!((moved[0][1] - (3. - 0.015 * DT)).abs() < 1e-15);
        assert!((moved[0][2] - PI / 3. * DT).abs() < 1e-15);
    }
    #[test]
    fn configured_sensors_and_fresh_states() {
        for fraction in [0., 0.5, 0.95, 1.] {
            let s = Simulation::new(
                40,
                30,
                Config {
                    sensing_fraction: fraction,
                    ..Config::default()
                },
                17,
            )
            .unwrap();
            assert_eq!(
                s.predators.iter().filter(|a| a[3] == 0.).count(),
                ((1. - fraction) * 40.) as usize
            );
        }
        let a = Simulation::new(10, 10, Config::default(), 1).unwrap();
        let b = Simulation::new(10, 10, Config::default(), 2).unwrap();
        assert_ne!(a.predators, b.predators);
    }
    #[test]
    fn capture_is_inclusive_and_removed_prey_stays_removed() {
        let mut s = Simulation::from_state(
            Config {
                predator_range: 0.,
                prey_range: 0.,
                ..Config::default()
            },
            vec![[0., 0., 0., 1., 0.]],
            vec![[0.1, 0., 0., 0., 1.]],
            1,
        )
        .unwrap();
        let z = Noise {
            predator_x: vec![0.],
            predator_y: vec![0.],
            prey_x: vec![0.],
            prey_y: vec![0.],
        };
        s.step_with_noise(&z).unwrap();
        assert_eq!(s.active_count(), 0);
        let prey = s.prey.clone();
        s.step().unwrap();
        assert_eq!(s.prey, prey);
    }
    #[test]
    fn invalid_inputs_rejected() {
        assert!(Simulation::new(0, 10, Config::default(), 0).is_err());
        assert!(Simulation::new(
            10,
            10,
            Config {
                predator_range: f64::NAN,
                ..Config::default()
            },
            0
        )
        .is_err());
    }
}
