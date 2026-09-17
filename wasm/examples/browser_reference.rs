use predator_prey_core::{Config, Simulation};
use serde_json::json;
fn main() {
    let mut s = Simulation::new(
        12,
        7,
        Config {
            sensing_fraction: 0.5,
            ..Config::default()
        },
        314159,
    )
    .unwrap();
    for _ in 0..100 {
        s.step().unwrap();
    }
    println!("{}", json!(s.snapshot()));
}
