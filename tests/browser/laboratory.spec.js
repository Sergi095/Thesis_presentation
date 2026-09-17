import {test,expect} from '@playwright/test';

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
