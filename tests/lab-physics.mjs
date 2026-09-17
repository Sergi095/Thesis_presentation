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
const hover=Math.sqrt(DRONE.mass*DRONE.gravity/(4*DRONE.kf));
const wrench=motorWrench([hover,hover,hover,hover]);
assert.ok(Math.abs(wrench.force[2]-DRONE.mass*DRONE.gravity)<1e-12);assert.deepEqual(wrench.torque,[0,0,0]);
const require=createRequire(import.meta.url);
const A=await require('ammojs3/builds/ammo.wasm.js')({wasmBinary:fs.readFileSync('node_modules/ammojs3/builds/ammo.wasm.wasm')});
const core=(await WebAssembly.instantiate(fs.readFileSync('dist/core.wasm'),{})).instance.exports;
const config={predators:5,prey:4,range:3,model:'adm',capture:.15,seed:20,duration:120};
const lab=new Laboratory(A,core,config);
for(let i=0;i<2400;i++)lab.step();
for(const a of lab.snapshot().agents.filter(a=>a.active))assert.ok(Math.abs(a.position[2]-.6)<.03,'Flight remains close to altitude setpoint');
lab.destroy();
// Drop an unpowered drone: gravity must accelerate it and the floor must stop it.
const falling=new Laboratory(A,core,config), drone=falling.drones[0];
for(let i=0;i<24;i++)falling.world.stepSimulation(1/240,0);
assert.ok(falling.state(drone).velocity[2]<-.8,'Gravity acts without motor thrust');
for(let i=0;i<480;i++)falling.world.stepSimulation(1/240,0);
assert.ok(falling.state(drone).position[2]>=0&&falling.state(drone).position[2]<.1,'Floor collision stops free fall');
// A driven rigid body must not pass through the lab wall.
const v=new A.btVector3(20,0,0);drone.body.setLinearVelocity(v);A.destroy(v);
for(let i=0;i<240;i++)falling.world.stepSimulation(1/240,0);
assert.ok(falling.state(drone).position[0]<LAB.width,'Wall collision confines physical body');
falling.destroy();
// Capture depends on observed 3D separation, not the speculative controller step.
const capture=new Laboratory(A,core,{...config,predators:1,prey:1,capture:.5});
const transform=capture.drones[1].body.getWorldTransform();const near=new A.btVector3(2.2,4.6,.6);transform.setOrigin(near);capture.drones[1].body.setWorldTransform(transform);A.destroy(near);
capture.step();assert.equal(capture.snapshot().captured,1);assert.equal(core.simulation_snapshot_len()>0,true);capture.destroy();
console.log(`PASS: ${fixture.samples.length} reference PID calls (max RPM error ${error}), motor wrench, altitude, gravity, floor/wall contact, and physical capture.`);
