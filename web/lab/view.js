import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { LAB } from './physics.js';

export function laboratoryView(container) {
  const scene=new THREE.Scene();scene.background=new THREE.Color('#101d2d');
  const camera=new THREE.PerspectiveCamera(42,1,.01,100);camera.up.set(0,0,1);
  const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));
  renderer.domElement.setAttribute('aria-label','Three-dimensional laboratory with predator and prey drones');container.append(renderer.domElement);
  const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(LAB.width/2,LAB.length/2,.5);controls.maxDistance=22;controls.minDistance=.4;controls.maxPolarAngle=Math.PI*.49;
  const home=()=>{camera.position.set(8.2,-2.8,6.5);controls.target.set(LAB.width/2,LAB.length/2,.5);controls.update();};home();
  scene.add(new THREE.HemisphereLight(0xffffff,0x47586e,2.6));const light=new THREE.DirectionalLight(0xffffff,2);light.position.set(1,-3,9);scene.add(light);
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(LAB.width,LAB.length),new THREE.MeshStandardMaterial({color:0x253b4b,roughness:.9,side:THREE.DoubleSide}));floor.position.set(LAB.width/2,LAB.length/2,-.002);scene.add(floor);
  const points=[];
  for(let x=0;x<=LAB.width;x+=.5)points.push(x,0,0,x,LAB.length,0);
  for(let y=0;y<=LAB.length;y+=.5)points.push(0,y,0,LAB.width,y,0);
  const grid=new THREE.BufferGeometry();grid.setAttribute('position',new THREE.Float32BufferAttribute(points,3));scene.add(new THREE.LineSegments(grid,new THREE.LineBasicMaterial({color:0x4a6271,transparent:true,opacity:.5})));
  const room=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(LAB.width,LAB.length,LAB.height)),new THREE.LineBasicMaterial({color:0x8aa8b8,transparent:true,opacity:.65}));room.position.set(LAB.width/2,LAB.length/2,LAB.height/2);scene.add(room);
  // Rear walls are translucent. Front walls and ceiling retain their outline
  // so all drone positions stay visible; every surface still has collisions.
  for(const [size,pos] of [[[LAB.width,.015,LAB.height],[LAB.width/2,LAB.length,LAB.height/2]],[[.015,LAB.length,LAB.height],[0,LAB.length/2,LAB.height/2]]]) {
    const wall=new THREE.Mesh(new THREE.BoxGeometry(...size),new THREE.MeshStandardMaterial({color:0x8ba9b8,transparent:true,opacity:.12,depthWrite:false}));wall.position.set(...pos);scene.add(wall);
  }
  const droneMeshes=[];
  function makeDrone(prey) {
    const group=new THREE.Group(),color=prey?0xffad55:0x55bcef;
    const material=new THREE.MeshStandardMaterial({color,roughness:.55});
    const body=new THREE.Mesh(new THREE.BoxGeometry(.035,.045,.02),material);group.add(body);
    for(const angle of [Math.PI/4,-Math.PI/4]){const arm=new THREE.Mesh(new THREE.BoxGeometry(.09,.009,.006),material);arm.rotation.z=angle;group.add(arm);}
    for(const x of [-.028,.028])for(const y of [-.028,.028]){const rotor=new THREE.Mesh(new THREE.RingGeometry(.012,.023,16),new THREE.MeshBasicMaterial({color,side:THREE.DoubleSide}));rotor.position.set(x,y,.009);group.add(rotor);}
    const halo=new THREE.Mesh(new THREE.RingGeometry(.085,.093,24),new THREE.MeshBasicMaterial({color,transparent:true,opacity:.65,side:THREE.DoubleSide}));halo.position.z=-.02;group.add(halo);
    group.userData.prey=prey;scene.add(group);return group;
  }
  function update(frame) {
    while(droneMeshes.length<frame.agents.length)droneMeshes.push(makeDrone(frame.agents[droneMeshes.length].prey));
    frame.agents.forEach((a,i)=>{
      if(droneMeshes[i].userData.prey!==a.prey) {
        const old=droneMeshes[i];scene.remove(old);old.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});droneMeshes[i]=makeDrone(a.prey);
      }
      const mesh=droneMeshes[i];mesh.visible=a.active;mesh.position.set(...a.position);mesh.quaternion.set(...a.quaternion);
    });
    for(let i=frame.agents.length;i<droneMeshes.length;i++)droneMeshes[i].visible=false;
    renderer.render(scene,camera);
  }
  function resize(){const {width,height}=container.getBoundingClientRect();if(width<1||height<1)return;renderer.setSize(width,height);camera.aspect=width/height;camera.updateProjectionMatrix();renderer.render(scene,camera);}
  controls.addEventListener('change',()=>renderer.render(scene,camera));new ResizeObserver(resize).observe(container);
  return {update,resize,home};
}
