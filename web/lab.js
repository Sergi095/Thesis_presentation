import { laboratoryView } from './lab/view.js';
export function createLaboratory(root) {
  root.innerHTML=`<div class="playground-heading"><div><p class="eyebrow">PHYSICS & FLIGHT CONTROL</p><h2>Laboratory simulator</h2><p>Explore predator–prey pursuit inside the measured flight arena.</p></div></div>
  <div class="lab-grid"><form id="lab-controls" class="controls"><h3>Experiment settings</h3><fieldset id="lab-parameters"><legend class="sr-only">Laboratory parameters</legend>
  <div class="field-pair"><label>Predators<input name="predators" type="number" min="1" max="12" step="1" value="5" required></label><label>Prey<input name="prey" type="number" min="1" max="12" step="1" value="4" required></label></div>
  <label>Sensing range (m)<input name="range" type="number" min="0.1" max="10" step="0.1" value="3" required></label>
  <label>Predator interaction<select name="model"><option value="adm">ADM</option><option value="dm">DM</option></select></label>
  <label>Capture distance (m)<input name="capture" type="number" min="0.05" max="1" step="0.01" value="0.15" required></label>
  <label>Duration (s)<input name="duration" type="number" min="1" max="600" step="1" value="120" required></label></fieldset>
  <label class="pace-label">Playback pace<output id="lab-pace-label">1×</output><input id="lab-pace" type="range" min="1" max="5" step="1" value="1"></label>
  <div class="run-buttons"><button id="lab-run" class="primary" type="submit" disabled>Loading simulator…</button><button id="lab-pause" type="button" disabled>Pause</button><button id="lab-reset" type="button" disabled>New run</button></div>
  <p id="lab-status" role="status">Preparing simulation.</p><p id="lab-error" role="alert" hidden></p></form>
  <div class="lab-panel"><div class="arena-toolbar"><div class="legend"><span><i class="pred-dot"></i>Predators</span><span><i class="prey-dot"></i>Prey</span></div><button id="lab-home" type="button">Reset view</button></div>
  <div id="lab-scene"></div><div class="lab-dimensions">4.40 m × 7.90 m × 2.20 m <span>Drag to rotate · Scroll to zoom</span></div>
  <div class="metrics"><div><span>Simulation time</span><strong id="lab-time">0.00 s</strong></div><div><span>Prey captured</span><strong id="lab-captured">0 / 4</strong></div><div><span>Mean altitude</span><strong id="lab-altitude">0.60 m</strong></div><div><span>Swarm distance</span><strong id="lab-distance">—</strong></div></div>
  <div class="arena-footer"><span>Gravity · Motor thrust · Collisions</span><button id="lab-export" type="button" disabled>Download current state ↓</button></div></div></div>
  <details class="model-note"><summary>About the laboratory model</summary><p>The arena measures 4.40 × 7.90 × 2.20 metres. Crazyflie drones have a mass of 27 grams, rotor thrust and torque, inertia, and PID flight control. Bullet resolves gravity and collisions with other drones, the floor, walls and ceiling.</p><p>The published DM/ADM swarm controller supplies horizontal flight commands at 20 Hz. Flight control and physics update at 240 Hz, with a 0.60 m altitude setpoint. Capture uses the actual three-dimensional distance; captured prey are removed. There is no added wall-avoidance controller.</p><p>This is a Bullet-based laboratory adaptation of the published model. It is not a replay of PyBullet experiments or a claim of identical trajectories. Aerodynamic drag, ground effect and downwash are not modelled.</p></details>`;
  const $=id=>root.querySelector(`#${id}`), form=$('lab-controls');
  let view, latest, config, state='loading', ready=false;
  try{view=laboratoryView($('lab-scene'));}catch(error){$('lab-error').hidden=false;$('lab-error').textContent=`Could not create the 3D view: ${error.message}`;return {pause(){},show(){}};}
  const worker=new Worker(new URL('./lab-worker.js',import.meta.url));
  function status(next){state=next;$('lab-parameters').disabled=next==='running'||next==='paused';$('lab-run').disabled=!ready||next==='running';$('lab-run').textContent=!ready?'Loading simulator…':next==='paused'?'Resume':next==='complete'?'Run again':'Run';$('lab-pause').disabled=next!=='running';$('lab-reset').disabled=!ready;$('lab-export').disabled=!latest;
    $('lab-status').textContent=({ready:'Ready. Press Run to begin.',running:'Running.',paused:'Paused. Resume to continue.',complete:latest?.captured===config?.prey?'Finished: all prey captured.':'Finished: time limit reached.',error:'Simulation stopped.'})[next]||'Preparing simulation.';}
  function reset(run=false){$('lab-parameters').disabled=false;if(!form.reportValidity()){status(state);return;}const values=new FormData(form);config={seed:crypto.getRandomValues(new Uint32Array(1))[0],model:values.get('model')};for(const key of ['predators','prey','range','capture','duration'])config[key]=Number(values.get(key));$('lab-error').hidden=true;worker.postMessage({type:'init',config,run});}
  worker.onmessage=({data})=>{
    if(data.type==='ready'){ready=true;reset();}
    else if(data.type==='frame'){latest=data.frame;status(data.status);view.update(latest);$('lab-time').textContent=`${latest.time.toFixed(2)} s`;$('lab-captured').textContent=`${latest.captured} / ${config.prey}`;
      const active=latest.agents.filter(a=>a.active);$('lab-altitude').textContent=`${(active.reduce((s,a)=>s+a.position[2],0)/active.length).toFixed(2)} m`;
      const center=prey=>{const agents=active.filter(a=>a.prey===prey);return agents.length?[0,1,2].map(i=>agents.reduce((s,a)=>s+a.position[i],0)/agents.length):null;};const p=center(false),q=center(true);$('lab-distance').textContent=q?`${Math.hypot(...p.map((v,i)=>v-q[i])).toFixed(2)} m`:'—';
    }else if(data.type==='error'){status('error');$('lab-error').hidden=false;$('lab-error').textContent=data.message;}
  };
  worker.onerror=error=>{status('error');$('lab-error').hidden=false;$('lab-error').textContent=error.message;};
  form.onsubmit=event=>{event.preventDefault();if(!ready||state==='running')return;if(state==='paused')worker.postMessage({type:'run'});else reset(true);};
  const pause=()=>{if(state==='running')worker.postMessage({type:'pause'});};
  $('lab-pause').onclick=pause;$('lab-reset').onclick=()=>reset();$('lab-home').onclick=view.home;
  $('lab-pace').oninput=event=>{$('lab-pace-label').textContent=`${event.target.value}×`;worker.postMessage({type:'pace',value:Number(event.target.value)});};
  $('lab-export').onclick=()=>{if(!latest)return;const url=URL.createObjectURL(new Blob([JSON.stringify({schema:'thesis-presentation.lab.v1',...latest},null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='laboratory-state.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
  document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
  return {pause,show(){view.resize();}};
}
