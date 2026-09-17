//! Non-target controller used by the thesis bounded PyBullet profile.
//! Kept separate from the frozen published 2D model.
use super::{boundary_force, distance, Agent, LAB_SCALE};

pub const LAMBDA: f64 = 0.2;

pub fn forces(
    agents: &[Agent],
    others: &[Agent],
    range: f64,
    adm: bool,
    prey: bool,
    bounds: [f64; 2],
) -> Vec<[f64; 2]> {
    let signals: Vec<f64> = agents
        .iter()
        .map(|a| {
            let visible: Vec<f64> = others
                .iter()
                .map(|b| distance(a, b))
                .filter(|d| *d <= range)
                .collect();
            let sum: f64 = visible.iter().sum();
            if sum > 0. {
                visible.len() as f64 / sum
            } else {
                0.
            }
        })
        .collect();
    let bases: Vec<f64> = agents
        .iter()
        .map(|a| {
            (if adm {
                if !prey && a[3] == 0. {
                    2.
                } else {
                    2_f64.sqrt() * 0.7
                }
            } else if !prey && a[3] == 0. {
                0.75
            } else {
                0.7
            }) * LAB_SCALE
        })
        .collect();
    let mut forces: Vec<[f64; 2]> = agents
        .iter()
        .map(|a| {
            let r = boundary_force(a, bounds);
            [LAB_SCALE * r[0], LAB_SCALE * r[1]]
        })
        .collect();
    for (i, a) in agents.iter().enumerate() {
        for (j, b) in agents.iter().enumerate() {
            if i == j {
                continue;
            }
            // Match v2's distance epsilon, source/receiver broadcasting and
            // signed prey sigma (the DM law uses even powers).
            let d = distance(a, b) + 1e-9;
            if d > 3.5 * LAB_SCALE {
                continue;
            }
            let mut sigma = bases[i]
                + if prey {
                    -LAMBDA * signals[j] * bases[j]
                } else if a[3] != 0. {
                    LAMBDA * signals[j] * bases[j]
                } else {
                    0.
                };
            if adm && !prey {
                sigma = sigma.max(0.0001);
            }
            let magnitude = if adm {
                -12. * (sigma / d - (sigma / d).max(0.).sqrt())
            } else {
                -12. * (2. * sigma.powi(4) / d.powi(5) - sigma.powi(2) / d.powi(3))
            };
            let angle = (a[1] - b[1]).atan2(a[0] - b[0]);
            forces[j][0] += magnitude * angle.cos();
            forces[j][1] += magnitude * angle.sin();
        }
    }
    forces
}
