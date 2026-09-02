import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
import path from 'node:path';

const chrome=process.env.CHROME_BIN || '/usr/bin/google-chrome';
const out=path.resolve('assets/rocky-readme-browser-frames');
fs.mkdirSync(out,{recursive:true});

const browser=await puppeteer.launch({
  headless:true,
  executablePath:chrome,
  args:[
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--enable-webgl',
    '--ignore-gpu-blocklist',
    '--use-angle=swiftshader',
    '--enable-unsafe-swiftshader',
    '--window-size=480,480'
  ]
});

const page=await browser.newPage();
await page.setViewport({width:480,height:480,deviceScaleFactor:1});
page.on('console',m=>console.log('[browser]',m.text()));
page.on('pageerror',e=>console.error('[pageerror]',e.message));

await page.goto('http://127.0.0.1:8765/rocky-model-viewer/index.html',{
  waitUntil:'domcontentloaded',
  timeout:120000
});

await page.waitForFunction(
  ()=>document.querySelector('#poster')?.classList.contains('hidden'),
  {timeout:120000}
);

// Start the real baked Auto animation while the control is still visible.
await page.waitForSelector('button[data-a="Auto"]',{visible:true,timeout:30000});
await page.click('button[data-a="Auto"]');
await new Promise(r=>setTimeout(r,250));

await page.addStyleTag({content:`
html,body{background:transparent!important;margin:0!important;overflow:hidden!important}
.hud,.controls,.tip,.loadbox,.poster,.error{display:none!important}
#stage{background:transparent!important}
canvas{display:block!important}
`});
await page.evaluate(()=>{
  document.documentElement.style.background='transparent';
  document.body.style.background='transparent';
});

// Ten real GLB frames: enough to show the original Rocky design moving in README
// without making GitHub's software WebGL runner spend minutes on screenshots.
const frames=10;
const interval=1800;
const start=Date.now();
for(let i=0;i<frames;i++){
  const target=start+i*interval;
  const wait=target-Date.now();
  if(wait>0) await new Promise(r=>setTimeout(r,wait));
  const filename=path.join(out,`frame_${String(i).padStart(3,'0')}.png`);
  await page.screenshot({path:filename,type:'png',omitBackground:true});
  console.log('captured original Rocky frame',i+1,'/',frames);
}

await browser.close();
console.log('captured original Rocky GLB animation to',out);
