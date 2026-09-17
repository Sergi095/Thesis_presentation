"""Compare Rust trajectories to the unchanged published Python simulator.

Identical initial states and explicit per-step noise isolate the equations from
the intentionally different NumPy/SplitMix random streams.
"""
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sim import PredatorPreySimulation


def compare(n, m, adm, prey_adm, sensing, pr, qr, capture, seed, steps=100):
    np.random.seed(seed)
    sim = PredatorPreySimulation(boundaries=(100, 100), N=n, N_preys=m,
        predator_sensor_range=pr, prey_sensing_range=qr, no_sensor=sensing, pdm=adm, pdm_prey=prey_adm)
    sim.capture_distance = capture
    predators, prey = sim.generate_agents_and_preys()
    fixture = dict(config=dict(predator_range=pr, prey_range=qr, adm=adm, prey_adm=prey_adm, capture_distance=capture),
                   predators=predators.tolist(), prey=prey.tolist(), noise=[])
    expected = []
    rng = np.random.default_rng(seed+10000)
    for _ in range(steps):
        active = int((prey[:, -1] != -1).sum())
        arrays = [rng.uniform(-.05, .05, size=size) for size in (n, n, active, active)]
        fixture['noise'].append(dict(zip(('predator_x', 'predator_y', 'prey_x', 'prey_y'), (a.tolist() for a in arrays))))
        with patch('numpy.random.uniform', side_effect=arrays):
            prey, predators = sim.simulate(prey, predators)
        assert np.isfinite(predators).all() and np.isfinite(prey).all()
        expected.append(dict(predators=predators.copy(), prey=prey.copy()))
    binary = ROOT / 'wasm/target/debug/examples/parity'
    result = subprocess.run([str(binary)], input=json.dumps(fixture), text=True, capture_output=True, check=True)
    actual = json.loads(result.stdout)
    assert len(actual) == steps
    error = 0.
    for i, (a, e) in enumerate(zip(actual, expected)):
        for species in ('predators', 'prey'):
            np.testing.assert_allclose(a[species], e[species], rtol=1e-10, atol=1e-9,
                err_msg=f'{adm=}, {prey_adm=}, {sensing=}, {pr=}, {qr=}, step={i}, {species}')
            error = max(error, float(np.abs(np.asarray(a[species])-e[species]).max()))
    print(f'PASS N={n}/{m}, ADM={adm}/{prey_adm}, sensing={sensing}, R={pr}/{qr}, capture={capture}: max error {error:.2e}')


def main():
    subprocess.run(['cargo', 'build', '--locked', '--manifest-path', str(ROOT/'wasm/Cargo.toml'), '--example', 'parity'], check=True)
    cases = [
        (12,7,False,False,1.,3.,3.,.1), (12,7,True,False,.5,3.,3.,.1),
        (7,12,False,True,0.,6.,4.,.5), (8,8,True,True,1.,10.,6.,.5),
        (20,10,True,False,.95,3.,5.,.1), (20,10,False,False,.5,4.,3.,.5),
        (1,1,False,False,1.,0.,0.,.1), (2,1,True,False,.5,4.,3.,5.),
        (1,6,True,False,0.,3.,3.,.1), (6,1,False,False,.5,3.,3.,.1),
        (10,10,False,False,1.,0.,0.,.1), (10,10,True,False,1.,100.,100.,.1),
    ]
    for i, case in enumerate(cases):
        compare(*case, seed=710+i)
    print(f'{len(cases)} Python/Rust trajectory comparisons passed (100 steps each).')


if __name__ == '__main__':
    main()
