import { Laboratory } from './lab/physics.js';
let world,core,ammo,running=false,timer,pace=1;
const ready=(async()=>{
  importScripts(new URL('./vendor/ammo.wasm.js',self.location.href).href);
  ammo=await self.Ammo({locateFile:name=>new URL(`./vendor/${name}`,self.location.href).href});
  core=(await WebAssembly.instantiateStreaming(fetch(new URL('./core.wasm',self.location.href)),{})).instance.exports;
  postMessage({type:'ready'});
})();
ready.catch(error=>postMessage({type:'error',message:`Could not load the physics simulator: ${error.message}`}));
function pause(){running=false;clearTimeout(timer);}
function publish(status){postMessage({type:'frame',status,frame:world.snapshot()});}
function pump(){
  if(!running)return;
  try {
    const start=performance.now(), quota=Math.round(8*pace);
    for(let i=0;i<quota&&performance.now()-start<14;i++) {
      if(world.ticks>=world.config.duration*240||world.drones.every(d=>!d.prey||!d.active))break;
      world.step();
    }
    const finished=world.ticks>=world.config.duration*240||world.drones.every(d=>!d.prey||!d.active);
    if(finished)pause();publish(finished?'complete':'running');
    if(running)timer=setTimeout(pump,Math.max(0,1000/30-(performance.now()-start)));
  } catch(error){pause();postMessage({type:'error',message:error.message});}
}
self.onmessage=async({data})=>{
  try {
    await ready;
    if(data.type==='init') {
      pause();
      const c=data.config;
      if(![c.predators,c.prey].every(n=>Number.isInteger(n)&&n>=1&&n<=12)||!Number.isFinite(c.duration)||c.duration<1||c.duration>600||!Number.isFinite(c.range)||c.range<.1||c.range>10||!Number.isFinite(c.capture)||c.capture<.05||c.capture>1) throw Error('Invalid laboratory settings.');
      world?.destroy();world=new Laboratory(ammo,core,c);publish('ready');
      if(data.run){running=true;pump();}
    }else if(data.type==='run'&&world&&!running){running=true;pump();}
    else if(data.type==='pause'){pause();if(world)publish('paused');}
    else if(data.type==='pace'&&Number.isFinite(data.value))pace=Math.max(1,Math.min(5,data.value));
  }catch(error){pause();postMessage({type:'error',message:error.message});}
};
