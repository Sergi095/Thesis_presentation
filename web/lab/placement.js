import formations from './formations.json' with {type:'json'};

// Canonical equilibrium hexagons, generated from Thesis planarEnvVEC.py.
// Orient facing points along the lab's long axis and solve the same 0.5R gap.
export function initialPositions(config, lab) {
  const predators=formations[config.model][config.predators];
  const prey=formations.dm[config.prey].map(p=>p.map(v=>-v));
  const gap=.5*config.range*lab.parameterScale;
  const minimum=shift=>Math.min(...predators.flatMap(p=>prey.map(q=>Math.hypot(p[0]-q[0],p[1]-q[1]-shift))));
  let lower=0,upper=Math.max(...predators.map(p=>Math.hypot(...p)))+Math.max(...prey.map(p=>Math.hypot(...p)))+gap+1;
  for(let i=0;i<80;i++){const mid=(lower+upper)/2;if(minimum(mid)<gap)lower=mid;else upper=mid;}
  const positions=[...predators.map(p=>[...p,lab.altitude]),...prey.map(p=>[p[0],p[1]+lower,lab.preyAltitude])];
  // Translate only, keeping the equilibrium formations and their exact gap.
  const min=[0,1].map(k=>Math.min(...positions.map(p=>p[k]))),max=[0,1].map(k=>Math.max(...positions.map(p=>p[k])));
  const shift=[lab.width/2-(min[0]+max[0])/2,lab.length/2-(min[1]+max[1])/2];
  return positions.map(p=>[p[0]+shift[0],p[1]+shift[1],p[2]]);
}
