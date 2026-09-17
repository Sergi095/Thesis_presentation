use predator_prey_core::{Agent, Config, Noise, Simulation};
use serde_json::{json, Value};
use std::io::{self, Read};
fn agents(v: &Value) -> Vec<Agent> {
    v.as_array()
        .unwrap()
        .iter()
        .map(|a| {
            let x = a.as_array().unwrap();
            std::array::from_fn(|i| x[i].as_f64().unwrap())
        })
        .collect()
}
fn numbers(v: &Value) -> Vec<f64> {
    v.as_array()
        .unwrap()
        .iter()
        .map(|x| x.as_f64().unwrap())
        .collect()
}
fn main() {
    let mut text = String::new();
    io::stdin().read_to_string(&mut text).unwrap();
    let f: Value = serde_json::from_str(&text).unwrap();
    let c = &f["config"];
    let cfg = Config {
        predator_range: c["predator_range"].as_f64().unwrap(),
        prey_range: c["prey_range"].as_f64().unwrap(),
        sensing_fraction: 1.,
        adm: c["adm"].as_bool().unwrap(),
        prey_adm: c["prey_adm"].as_bool().unwrap(),
        capture_distance: c["capture_distance"].as_f64().unwrap(),
    };
    let mut sim =
        Simulation::from_state(cfg, agents(&f["predators"]), agents(&f["prey"]), 1).unwrap();
    let mut frames = Vec::new();
    for noise in f["noise"].as_array().unwrap() {
        sim.step_with_noise(&Noise {
            predator_x: numbers(&noise["predator_x"]),
            predator_y: numbers(&noise["predator_y"]),
            prey_x: numbers(&noise["prey_x"]),
            prey_y: numbers(&noise["prey_y"]),
        })
        .unwrap();
        frames.push(json!({"predators":sim.predators,"prey":sim.prey}));
    }
    println!("{}", serde_json::to_string(&frames).unwrap());
}
