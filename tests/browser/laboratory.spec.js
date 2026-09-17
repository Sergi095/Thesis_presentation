import {test,expect} from '@playwright/test';

test('lab avoids stale unversioned scripts and physics modules',async({page,context})=>{
  const legacy=[];const requests=[];
  context.on('request',r=>requests.push(new URL(r.url()).pathname));
  await context.route(/\/(core\.wasm|app\.js|lab-worker\.js|simulation-worker\.js)$/,route=>{
    legacy.push(route.request().url());
    // A stale cache entry at the former URL must not affect this release.
    return route.fulfill({status:200,contentType:'application/wasm',body:Buffer.from([0,97,115,109,1,0,0,0])});
  });
  await page.goto('./#/lab');await expect(page.locator('#lab-run')).toBeEnabled({timeout:30000});
  await page.locator('#lab-controls input[name=duration]').fill('1');await page.locator('#lab-run').click();
  await expect(page.locator('#lab-status')).toHaveText('Finished: time limit reached.');
  expect(legacy).toEqual([]);
  expect(requests.some(path=>/\/core-[a-f0-9]{16}\.wasm$/.test(path))).toBe(true);
  expect(requests.some(path=>/\/lab-worker-[A-Z0-9]+\.js$/.test(path))).toBe(true);
});

test('incompatible physics module is rejected before enabling Run',async({page,context})=>{
  await context.route(/\/core-[a-f0-9]+\.wasm$/,route=>route.fulfill({status:200,contentType:'application/wasm',body:Buffer.from([0,97,115,109,1,0,0,0])}));
  await page.goto('./#/lab');
  await expect(page.locator('#lab-error')).toContainText('The simulator files do not match.');
  await expect(page.locator('#lab-run')).toBeDisabled();
});

test('second simulator advances physical drones, pauses, exports and retains the original simulator',async({page})=>{
  const errors=[],failures=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)failures.push(r.url());});
  await page.goto('./#/lab');await expect(page.locator('#lab-run')).toBeEnabled({timeout:30000});
  await expect(page.locator('#lab-scene canvas')).toBeVisible();
  await expect(page.locator('#playground')).toBeHidden();
  await page.locator('#lab-run').click();await expect(page.locator('#lab-time')).not.toHaveText('0.00 s');
  await page.locator('#lab-pause').click();await expect(page.locator('#lab-run')).toHaveText('Resume');
  const time=await page.locator('#lab-time').textContent();await page.waitForTimeout(200);await expect(page.locator('#lab-time')).toHaveText(time);
  const downloadPromise=page.waitForEvent('download');await page.locator('#lab-export').click();const download=await downloadPromise;
  const stream=await download.createReadStream();let text='';for await(const chunk of stream)text+=chunk;const snapshot=JSON.parse(text);
  expect(snapshot.agents).toHaveLength(9);expect(snapshot.agents.filter(a=>a.prey)).toHaveLength(4);
  for(const a of snapshot.agents){expect(a.position[2]).toBeGreaterThan(.5);expect(a.position[2]).toBeLessThan(.7);expect(a.rpm).toHaveLength(4);}
  await page.locator('#lab-run').click();await page.getByRole('link',{name:'2D swarm',exact:true}).click();
  await expect(page.locator('#run')).toBeEnabled();await expect(page.locator('#lab-status')).toContainText('Paused');
  await page.getByRole('link',{name:'3D laboratory',exact:true}).click();await expect(page.locator('#lab-run')).toHaveText('Resume');
  await page.locator('#lab-reset').click();await expect(page.locator('#lab-status')).toContainText('Ready');
  await page.locator('#lab-controls input[name=duration]').fill('1');await page.locator('#lab-run').click();
  await expect(page.locator('#lab-status')).toHaveText('Finished: time limit reached.');
  await page.setViewportSize({width:390,height:844});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
  expect(errors).toEqual([]);expect(failures).toEqual([]);
});
