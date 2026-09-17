import { DRONE, FlightControl, rotation, rotate, euler } from './flight-control.js';
export const LAB = Object.freeze({ width: 4.4, length: 7.9, height: 2.2, altitude: .6, physicsHz: 240, swarmHz: 20, parameterScale: .3 });

export class Laboratory {
  constructor(Ammo, core, config) {
    this.A=Ammo; this.core=core; this.config=config; this.objects=[]; this.bodies=[]; this.drones=[]; this.ticks=0;
    const A=Ammo, own=o=>{this.objects.push(o);return o;}; this.own=own;
    const collision=own(new A.btDefaultCollisionConfiguration()), dispatcher=own(new A.btCollisionDispatcher(collision));
    this.world=own(new A.btDiscreteDynamicsWorld(dispatcher,own(new A.btDbvtBroadphase()),own(new A.btSequentialImpulseConstraintSolver()),collision));
    this.vector=own(new A.btVector3(0,0,-DRONE.gravity));this.world.setGravity(this.vector);
    this.zero=own(new A.btVector3(0,0,0));
    this.tempTransform=own(new A.btTransform());
    const box=(half,pos)=>this.body(own(new A.btBoxShape(own(new A.btVector3(...half)))),0,pos,[0,0,0,1]);
    box([LAB.width/2,LAB.length/2,.05],[LAB.width/2,LAB.length/2,-.05]);
    box([LAB.width/2,LAB.length/2,.05],[LAB.width/2,LAB.length/2,LAB.height+.05]);
    for(const x of [-.05,LAB.width+.05]) box([.05,LAB.length/2,LAB.height/2],[x,LAB.length/2,LAB.height/2]);
    for(const y of [-.05,LAB.length+.05]) box([LAB.width/2,.05,LAB.height/2],[LAB.width/2,y,LAB.height/2]);
    if(core.simulation_init(config.predators,config.prey,config.range,config.range,1,config.model==='adm'?1:0,config.capture,config.seed)!==0) throw Error('Invalid laboratory settings.');
    if(core.lab_configure(LAB.width,LAB.length)!==0) throw Error('Could not configure the scaled laboratory controller.');
    this.effective={parameterScale:LAB.parameterScale,range:config.range*LAB.parameterScale,capture:config.capture*LAB.parameterScale,boundaryGamma:LAB.parameterScale,boundaryRadius:.5,maxSpeed:.15,target:false};
    const snapshot=this.coreSnapshot();
    for(let i=0;i<config.predators+config.prey;i++) {
      const prey=i>=config.predators, j=prey?i-config.predators:i, count=prey?config.prey:config.predators;
      const side=Math.ceil(Math.sqrt(count));
      const spacing=.5*LAB.parameterScale;
      const position=[LAB.width/2+(j%side-(side-1)/2)*spacing,(prey?2.5:4.8)+(Math.floor(j/side)-(Math.ceil(count/side)-1)/2)*spacing,LAB.altitude];
      const yaw=snapshot[8+i*5+2], q=[0,0,Math.sin(yaw/2),Math.cos(yaw/2)];
      const shape=own(new A.btCylinderShapeZ(own(new A.btVector3(DRONE.radius,DRONE.radius,DRONE.height/2))));shape.setMargin(.001);
      const body=this.body(shape,DRONE.mass,position,q,DRONE.inertia);
      body.setActivationState(4);body.setDamping(.04,.04);body.setCcdMotionThreshold(.025);body.setCcdSweptSphereRadius(.012);
      const drone={body,prey,active:true,pid:new FlightControl(),target:position.slice(),velocity:[0,0,0],yaw,rpm:[0,0,0,0]};
      this.drones.push(drone);core.lab_set_pose(i,position[0],position[1],yaw);
    }
    this.status='ready';
  }
  body(shape,mass,position,quaternion,inertia=[0,0,0]) {
    const A=this.A, own=this.own, transform=own(new A.btTransform());transform.setIdentity();
    transform.setOrigin(own(new A.btVector3(...position)));transform.setRotation(own(new A.btQuaternion(...quaternion)));
    const motion=own(new A.btDefaultMotionState(transform));
    const info=own(new A.btRigidBodyConstructionInfo(mass,motion,shape,own(new A.btVector3(...inertia))));
    const body=own(new A.btRigidBody(info));body.setFriction(.5);body.setRestitution(0);this.world.addRigidBody(body);this.bodies.push(body);return body;
  }
  state(drone) {
    const t=drone.body.getWorldTransform(), p=t.getOrigin(), q=t.getRotation(), v=drone.body.getLinearVelocity();
    return {position:[p.x(),p.y(),p.z()],quaternion:[q.x(),q.y(),q.z(),q.w()],velocity:[v.x(),v.y(),v.z()]};
  }
  coreSnapshot() {
    const ptr=this.core.simulation_snapshot();return new Float64Array(this.core.memory.buffer,ptr,this.core.simulation_snapshot_len()).slice();
  }
  command() {
    for(const [i,d] of this.drones.entries()) if(d.active) {
      const s=this.state(d);this.core.lab_set_pose(i,s.position[0],s.position[1],euler(s.quaternion)[2]);
    }
    if(this.core.lab_commands()!==0) throw Error('The swarm controller reached a non-finite state. Start a new run.');
    const commands=new Float64Array(this.core.memory.buffer,this.core.lab_commands_ptr(),this.drones.length*3).slice();
    for(const [i,d] of this.drones.entries()) if(d.active) {
      const position=this.state(d).position;
      d.target=[commands[3*i],commands[3*i+1],LAB.altitude];
      d.velocity=[(d.target[0]-position[0])*LAB.swarmHz,(d.target[1]-position[1])*LAB.swarmHz,0];
      d.yaw=commands[3*i+2];
    }
  }
  step() {
    if(this.ticks%12===0) this.command();
    for(const d of this.drones) if(d.active) {
      const s=this.state(d);
      d.rpm=d.pid.compute(1/LAB.physicsHz,s.position,s.quaternion,s.velocity,d.target,d.velocity,d.yaw);
      const wrench=motorWrenchWorld(d.rpm,s.quaternion);
      this.vector.setValue(...wrench.force);d.body.applyForce(this.vector,this.zero);
      this.vector.setValue(...wrench.torque);d.body.applyTorque(this.vector);
    }
    this.world.stepSimulation(1/LAB.physicsHz,0);this.ticks++;
    const predators=this.drones.filter(d=>!d.prey).map(d=>this.state(d).position);
    for(const [i,d] of this.drones.entries()) if(d.prey&&d.active) {
      const pos=this.state(d).position;
      if(predators.some(p=>Math.hypot(...p.map((v,k)=>v-pos[k]))<=this.effective.capture)) {
        d.active=false;this.world.removeRigidBody(d.body);this.core.lab_mark_captured(i-this.config.predators);
      }
    }
  }
  snapshot() {
    const agents=this.drones.map(d=>({...this.state(d),prey:d.prey,active:d.active,rpm:d.rpm}));
    if(agents.some(a=>![...a.position,...a.quaternion,...a.velocity].every(Number.isFinite))) throw Error('The physics simulation reached an invalid state.');
    return {time:this.ticks/LAB.physicsHz,agents,captured:agents.filter(a=>a.prey&&!a.active).length,config:this.config,effective:this.effective};
  }
  destroy() {
    for(const body of this.bodies) this.world.removeRigidBody(body);
    for(const object of this.objects.reverse()) this.A.destroy(object);
  }
}
import { motorWrench } from './flight-control.js';
function motorWrenchWorld(rpm,q) {const w=motorWrench(rpm), r=rotation(q);return {force:rotate(r,w.force),torque:rotate(r,w.torque)};}
