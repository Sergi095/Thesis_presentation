import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRequire} from 'node:module';
import {FlightControl,DRONE,motorWrench} from '../web/lab/flight-control.js';
import {Laboratory,LAB} from '../web/lab/physics.js';
const fixture=JSON.parse(fs.readFileSync(new URL('./flight-control-fixture.json',import.meta.url)));
const pid=new FlightControl();let error=0;
for(const s of fixture.samples) {
  const actual=pid.compute(s.dt,s.position,s.quaternion,s.velocity,s.targetPosition,s.targetVelocity,s.targetYaw);
  actual.forEach((rpm,i)=>{error=Math.max(error,Math.abs(rpm-s.rpm[i]));assert.ok(Math.abs(rpm-s.rpm[i])<1e-7);});
}
const turningFixture=JSON.parse(fs.readFileSync(new URL('./lab-flight-fixture.json',import.meta.url)));
const turningPid=new FlightControl();
for(const s of turningFixture.samples) {
  const actual=turningPid.compute(s.dt,s.position,s.quaternion,s.velocity,s.targetPosition,s.targetVelocity,s.targetYaw,s.targetYawRate);
  actual.forEach((rpm,i)=>assert.ok(Math.abs(rpm-s.rpm[i])<1e-7,'120 Hz PID including commanded yaw rate matches PyBullet'));
}
const hover=Math.sqrt(DRONE.mass*DRONE.gravity/(4*DRONE.kf));
const wrench=motorWrench([hover,hover,hover,hover]);
assert.ok(Math.abs(wrench.force[2]-DRONE.mass*DRONE.gravity)<1e-12);assert.deepEqual(wrench.torque,[0,0,0]);
const require=createRequire(import.meta.url);
const A=await require('ammojs3/builds/ammo.wasm.js')({wasmBinary:fs.readFileSync('node_modules/ammojs3/builds/ammo.wasm.wasm')});
const {assets}=JSON.parse(fs.readFileSync('dist/build.json'));
const core=(await WebAssembly.instantiate(fs.readFileSync(`dist/${assets.core}`),{})).instance.exports;
const config={predators:5,prey:4,range:3,model:'dm',capture:.5,seed:20,duration:120};
const lab=new Laboratory(A,core,config);
assert.ok(Math.abs(lab.snapshot().effective.range-.9)<1e-15);
assert.equal(lab.snapshot().effective.capture,.15);
assert.equal(lab.snapshot().effective.target,false);
const start=lab.snapshot();
const initialGap=Math.min(...start.agents.filter(a=>!a.prey).flatMap(p=>start.agents.filter(a=>a.prey).map(q=>Math.hypot(p.position[0]-q.position[0],p.position[1]-q.position[1]))));
assert.ok(Math.abs(initialGap-.45)<1e-6,'Swarms begin at the PyBullet 0.5R gap, inside sensing range');
for(let i=0;i<2400;i++)lab.step();
for(const a of lab.snapshot().agents.filter(a=>a.active))assert.ok(Math.abs(a.position[2]-(a.prey?.5:.6))<.03,'Flight remains close to its role-specific altitude setpoint');
lab.destroy();
// Drop an unpowered drone: gravity must accelerate it and the floor must stop it.
const falling=new Laboratory(A,core,{...config,predators:1,prey:1}), drone=falling.drones[0];
for(let i=0;i<24;i++)falling.world.stepSimulation(1/240,0);
assert.ok(falling.state(drone).velocity[2]<-.8,'Gravity acts without motor thrust');
for(let i=0;i<480;i++)falling.world.stepSimulation(1/240,0);
assert.ok(falling.state(drone).position[2]>=0&&falling.state(drone).position[2]<.1,'Floor collision stops free fall');
// Isolate wall contact above the floor, without a high-speed floor impact.
const wallPose=drone.body.getWorldTransform(), origin=new A.btVector3(4,3,1.2);
const upright=new A.btQuaternion(0,0,0,1);
wallPose.setOrigin(origin);wallPose.setRotation(upright);drone.body.setWorldTransform(wallPose);A.destroy(origin);A.destroy(upright);
const v=new A.btVector3(2,0,0);drone.body.setLinearVelocity(v);v.setValue(0,0,0);drone.body.setAngularVelocity(v);A.destroy(v);
for(let i=0;i<60;i++)falling.world.stepSimulation(1/240,0);
assert.ok(falling.state(drone).position[0]<LAB.width,'Wall collision confines physical body');
falling.destroy();
// Capture uses observed XY separation, as in the current planar PyBullet adapter.
const capture=new Laboratory(A,core,{...config,predators:1,prey:1,capture:.5});
let pos=capture.state(capture.drones[0]).position;
const transform=capture.drones[1].body.getWorldTransform();const near=new A.btVector3(pos[0],pos[1]+.2,.5);transform.setOrigin(near);capture.drones[1].body.setWorldTransform(transform);
for(let i=0;i<12;i++)capture.step();assert.equal(capture.snapshot().captured,0,'Nominal .5 capture must be scaled to .15');
pos=capture.state(capture.drones[0]).position;
near.setValue(pos[0],pos[1]+.14,.5);transform.setOrigin(near);capture.drones[1].body.setWorldTransform(transform);A.destroy(near);
for(let i=0;i<12;i++)capture.step();assert.equal(capture.snapshot().captured,1);assert.equal(core.simulation_snapshot_len()>0,true);capture.destroy();
// Exercise the real WASM/Bullet adapter: both roles receive the same wall
// field before the unicycle update, with gamma scaled exactly once.
const bounded=new Laboratory(A,core,{...config,predators:1,prey:1,range:.1});
for(const x of [.49,2.2]) {
  core.lab_set_pose(0,x,3,Math.PI/2);core.lab_set_pose(1,x,4,Math.PI/2);
  assert.equal(core.lab_commands(),0);
  const commands=new Float64Array(core.memory.buffer,core.lab_commands_ptr(),6).slice();
  const force=x===.49?.3*2*(1/.49-1/.5)/(.49**3):0;
  const expectedYaw=Math.PI/2-.05*force*.05;
  assert.ok(Math.abs(commands[2]-expectedYaw)<1e-12);
  assert.ok(Math.abs(commands[5]-expectedYaw)<1e-12);
}
bounded.destroy();
// Measured body yaw must not reset the high-level heading integrator.
const headings=new Laboratory(A,core,config);
headings.drones[0].yaw=1.23;
headings.command();
assert.ok(Math.abs(headings.drones[0].yaw-1.23)<=Math.PI/3/20+1e-12);
headings.destroy();
console.log(`PASS: ${fixture.samples.length} reference PID calls (max RPM error ${error}), motor wrench, altitude, gravity, floor/wall contact, and physical capture.`);
