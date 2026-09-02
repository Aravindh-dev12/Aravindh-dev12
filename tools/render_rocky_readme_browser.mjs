import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
import path from 'node:path';

const chrome=process.env.CHROME_BIN || '/usr/bin/google-chrome';
const out=path.resolve('assets');
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
    '--window-size=560,560'
  ]
});

const page=await browser.newPage();
await page.setViewport({width:560,height:560,deviceScaleFactor:1});
page.on('console',m=>console.log('[browser]',m.text()));
page.on('pageerror',e=>console.error('[pageerror]',e.message));

await page.goto('http://127.0.0.1:8765/rocky-model-viewer/index.html',{
  waitUntil:'domcontentloaded',
  timeout:120000
});

// Viewer removes the poster only when the real Rocky GLB is loaded.
await page.waitForFunction(
  ()=>document.querySelector('#poster')?.classList.contains('hidden'),
  {timeout:120000}
);

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

// One clean frame from the actual GLB for the GitHub README.
await new Promise(r=>setTimeout(r,500));
const filename=path.join(out,'rocky-readme-original.png');
await page.screenshot({path:filename,type:'png',omitBackground:true});
console.log('captured original Rocky GLB README frame:',filename);

await browser.close();
