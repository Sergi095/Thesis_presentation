"""Refresh synthetic fixtures from a local Thesis checkout; never runs experiments.

Usage: python tests/generate-lab-reference.py /path/to/Thesis
The generated data contains formula outputs only, no research trajectories.
"""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

thesis = Path(sys.argv[1])
root = Path(__file__).resolve().parents[1]
v2 = thesis / 'swarm/implementing_paper/simulation_v2'
sys.path.insert(0, str(v2))
from planarEnvVEC import environment_agent, predator_equilibrium_profile, rotate_points_toward

profiles = {}
for adm in [False, True]:
    profiles['adm' if adm else 'dm'] = [[]] + [
        rotate_points_toward(predator_equilibrium_profile(
            n, adm=adm, sigma_dm=.7*.3, sigma_adm=np.sqrt(2)*.7*.3,
            cutoff_dm=3.5*.3, cutoff_adm=3.5*.3)['positions'], np.array([0., 1.])).tolist()
        for n in range(1, 13)
    ]
(root / 'web/lab/formations.json').write_text(json.dumps(profiles, separators=(',', ':'))+'\n')

rng = np.random.default_rng(91622)  # Synthetic test inputs only.
samples = []
for adm in [False, True]:
    for sample in range(8):
        env = environment_agent.__new__(environment_agent)
        env.boundaries = [4.4, 7.9]
        env.k_rep, env.L0, env.Dr = 2., .5, .5
        env.epsilon = env.epsilon_prey = 12.
        env.sigma_i_predator = env.sigma_i_prey = .7*.3
        env.sigma_i_pred_non_sensing = .75*.3
        env.sigma_i_pred_DM = env.sigma_i_prey_adm = np.sqrt(2)*.7*.3
        env.sigma_i_pred_non_sensing_DM = 2.*.3
        env.Dp = env.Dp_prey = env.Dp_pm = env.Dp_pm_prey = 3.5*.3
        env.sensor_range = env.sensing_range = .9
        env.lambda_predator = env.lambda_prey = .2
        env.rep_mode, env.use_target, env.mutual_sensing_after_chase_line = 'grad_rep', False, False
        preds, preys = np.ones((5,5)), np.ones((4,6))
        for agents in [preds, preys]:
            agents[:,:2] = rng.uniform([.12,.14], [2.,1.8], (len(agents),2))
            agents[:,2] = rng.uniform(-np.pi,np.pi,len(agents))
        preds[0,3] = 0  # Source-row sensor gating.
        if sample == 0:
            # Close sensed predators produce negative prey sigma in DM.
            preds[1,:2] = preys[1,:2] + [.02,0.]
        ps=env.get_distance_from_swarm_preys(preys,preds)
        qs=env.get_distance_from_swarm_predators(preys,preds)
        pf=(env.p_vector_DM(preds,ps) if adm else env.p_vector(preds,ps))+.3*env.r_vector(preds,env.boundaries)
        qf=env.p_vector(preys,qs)+.3*env.r_vector(preys,env.boundaries)
        samples.append(dict(adm=adm,predators=preds.tolist(),prey=preys[:,:5].tolist(),predator_force=pf.tolist(),prey_force=qf.tolist()))
source = v2 / 'planarEnvVEC.py'
fixture = dict(source='Thesis planarEnvVEC.py; bounded non-target profile, lambda=0.2, gamma=0.3',
    sha256=hashlib.sha256(source.read_bytes()).hexdigest(), samples=samples)
(root/'tests/lab-controller-fixture.json').write_text(json.dumps(fixture,indent=2)+'\n')

# Match the bounded runner's 120 Hz PID and commanded yaw rates as well.
sys.path.insert(0, str(thesis/'swarm/3D_implementation'))
from control.DSLPIDControl import DSLPIDControl
from utils.enums import DroneModel
pid = DSLPIDControl(DroneModel.CF2X)
flight = json.loads((root/'tests/flight-control-fixture.json').read_text())
for i,s in enumerate(flight['samples']):
    s['dt'] = 1/120
    s['targetYawRate'] = .2*np.sin(i*.4)
    s['targetPosition'][:2] = s['position'][:2]
    rpm,_,_ = pid.computeControl(s['dt'],np.array(s['position']),np.array(s['quaternion']),
        np.array(s['velocity']),np.zeros(3),np.array(s['targetPosition']),
        np.array([0,0,s['targetYaw']]),np.array(s['targetVelocity']),np.array([0,0,s['targetYawRate']]))
    s['rpm'] = rpm.tolist()
flight['source'] = 'Thesis DSLPIDControl, velocity mode at 120 Hz including commanded yaw rate; synthetic states'
(root/'tests/lab-flight-fixture.json').write_text(json.dumps(flight,indent=2)+'\n')
