<img width="1440" height="974" alt="image" src="https://github.com/user-attachments/assets/28f10373-fa2c-49c8-afa0-fad9e719e95c" /><!---<h1> Hey there! :wave:<br>
I am <a href="https://www.amitramrakhyani.me/" target="_blank">Aravindh </a></h1>

### :man_technologist: About Me
:mag: A CSE sophomore with keen interest in coding, robotics, astronomy and rocket science.

<a href="https://www.linkedin.com/in/amit-ramrakhyani-73b076214/"><img src="https://user-images.githubusercontent.com/94364976/211248544-dfb2e806-e605-412a-918c-40eb1cd4023c.png" width="40" height="40"></a>
<a href="https://twitter.com/AmitR_0911"><img src="https://user-images.githubusercontent.com/94364976/211249579-06b03ee3-710a-41b9-8396-e305853e1001.png" width="40" height="40"></a>
<a href="https://www.instagram.com/amit_ramrakhyani_/"><img src="https://user-images.githubusercontent.com/94364976/211249851-926edd5b-eb81-4647-a3bc-49cd0e78ce32.png" width="40" height="40"></a>
-->


<!--horizontal divider(gradiant)-->
<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif">

<!--profile visit count-->
<div align="center">
  
[![](https://visitcount.itsvg.in/api?id=Amit-Ramrakhyani&label=Profile%20Views&color=0&icon=0&pretty=true)](https://visitcount.itsvg.in)  
</div>

<!--h1 without bottom border-->
<div id="user-content-toc">
  <ul align="center">
    <summary><h1 style="display: inline-block">Hi 👋, I'm <a href="https://aravindh-portfolio-rsds.onrender.com/portfolio/" target="_blank">Aravindh</a></h1></summary>
  </ul>

<!-- ![Snake animation](https://github.com/Amit-Ramrakhyani/Amit-Ramrakhyani/blob/output/github-contribution-grid-snake.svg) -->


<canvas id="c" style="display:block;border-radius:12px;width:100%"></canvas>
<script>
const cv=document.getElementById('c');
const cx=cv.getContext('2d');
const W=680,H=460;
cv.width=W;cv.height=H;
const CX=W/2,CY=H/2+20;

const PLANETS=[
  {name:'Mercury', au:0.387, period:0.241, ecc:0.206, color:'#a8a8a8', r:2.8,  rings:false, moons:0},
  {name:'Venus',   au:0.723, period:0.615, ecc:0.007, color:'#e8c97a', r:5.5,  rings:false, moons:0},
  {name:'Earth',   au:1.000, period:1.000, ecc:0.017, color:'#4a90d9', r:6,    rings:false, moons:1, moonDist:10, moonAngle:0, moonPeriod:0.075},
  {name:'Mars',    au:1.524, period:1.881, ecc:0.093, color:'#c1440e', r:4,    rings:false, moons:0},
  {name:'Jupiter', au:2.6,   period:11.86, ecc:0.049, color:'#c8863a', r:14,   rings:false, moons:0},
  {name:'Saturn',  au:3.3,   period:29.46, ecc:0.057, color:'#e4d191', r:11,   rings:true,  moons:0},
  {name:'Uranus',  au:3.9,   period:84.01, ecc:0.046, color:'#7de8e8', r:8,    rings:false, moons:0},
  {name:'Neptune', au:4.4,   period:164.8, ecc:0.010, color:'#3f54ba', r:7,    rings:false, moons:0},
];

const AU=62;
const START=[4.40,3.18,1.75,6.20,0.60,5.93,2.98,4.52];
PLANETS.forEach((p,i)=>{p.angle=START[i];});

const STARS=[];
for(let i=0;i<300;i++){
  STARS.push({x:Math.random()*W,y:Math.random()*H,s:Math.random()*1.5+0.2,ph:Math.random()*6.28,mag:Math.random()*0.7+0.3});
}

const ASTEROIDS=[];
for(let i=0;i<140;i++){
  const a=Math.random()*Math.PI*2;
  const d=(AU*2.05)+(Math.random()*(AU*0.45));
  ASTEROIDS.push({a,d,da:(Math.random()-0.5)*0.00025,s:Math.random()*0.8+0.3});
}

// Shooting stars
const SHOOTS=[];
let shootTimer=0;

let frame=0;

function getPlanetXY(p){
  const a=p.au*AU;
  const b=a*Math.sqrt(1-p.ecc*p.ecc);
  const x=CX+a*Math.cos(p.angle)-a*p.ecc;
  const y=CY+b*Math.sin(p.angle);
  return{x,y};
}

function drawStars(){
  STARS.forEach(s=>{
    s.ph+=0.008;
    const a=(0.3+Math.sin(s.ph)*0.25)*s.mag;
    cx.beginPath();cx.arc(s.x,s.y,s.s,0,6.28);
    cx.fillStyle=`rgba(255,255,255,${a})`;cx.fill();
  });
}

function drawShoots(){
  shootTimer++;
  if(shootTimer>90){
    shootTimer=0;
    if(Math.random()<0.6){
      SHOOTS.push({
        x:Math.random()*W*0.6,
        y:Math.random()*H*0.3,
        vx:Math.random()*4+3,
        vy:Math.random()*2+1,
        life:1,
        len:Math.random()*40+20
      });
    }
  }
  for(let i=SHOOTS.length-1;i>=0;i--){
    const s=SHOOTS[i];
    s.x+=s.vx;s.y+=s.vy;s.life-=0.03;
    if(s.life<=0||s.x>W||s.y>H){SHOOTS.splice(i,1);continue;}
    const grad=cx.createLinearGradient(s.x-s.vx*s.len/s.vx,s.y-s.vy*s.len/s.vx,s.x,s.y);
    grad.addColorStop(0,`rgba(255,255,255,0)`);
    grad.addColorStop(1,`rgba(255,255,255,${s.life*0.9})`);
    cx.beginPath();
    cx.moveTo(s.x-s.vx*(s.len/5),s.y-s.vy*(s.len/5));
    cx.lineTo(s.x,s.y);
    cx.strokeStyle=grad;cx.lineWidth=1.2;cx.stroke();
    cx.beginPath();cx.arc(s.x,s.y,1,0,6.28);
    cx.fillStyle=`rgba(255,255,255,${s.life})`;cx.fill();
  }
}

function drawOrbits(){
  PLANETS.forEach(p=>{
    const a=p.au*AU;
    const b=a*Math.sqrt(1-p.ecc*p.ecc);
    cx.save();
    cx.translate(CX-a*p.ecc,CY);
    cx.beginPath();cx.ellipse(0,0,a,b,0,0,6.28);
    cx.strokeStyle='rgba(255,255,255,0.07)';
    cx.lineWidth=0.5;cx.stroke();
    cx.restore();
  });
}

function drawAsteroids(){
  ASTEROIDS.forEach(a=>{
    a.a+=a.da;
    const focusOffset=(AU*2.05+AU*0.45/2)*0.049;
    const x=CX+Math.cos(a.a)*a.d-focusOffset;
    const y=CY+Math.sin(a.a)*a.d*0.93;
    cx.beginPath();cx.arc(x,y,a.s,0,6.28);
    cx.fillStyle='rgba(180,160,130,0.45)';cx.fill();
  });
}

function drawSun(){
  for(let i=4;i>=0;i--){
    cx.beginPath();cx.arc(CX,CY,22+i*10,0,6.28);
    cx.fillStyle=`rgba(255,${200-i*18},${30-i*5},${0.07-i*0.012})`;
    cx.fill();
  }
  // Animated corona rays
  for(let i=0;i<12;i++){
    const a=(i/12)*6.28+frame*0.003;
    const r1=22,r2=32+Math.sin(frame*0.05+i)*4;
    cx.beginPath();
    cx.moveTo(CX+Math.cos(a)*r1,CY+Math.sin(a)*r1);
    cx.lineTo(CX+Math.cos(a)*r2,CY+Math.sin(a)*r2);
    cx.strokeStyle='rgba(255,220,80,0.15)';cx.lineWidth=1.5;cx.stroke();
  }
  cx.beginPath();cx.arc(CX,CY,20,0,6.28);
  cx.fillStyle='#fff4a0';cx.fill();
  // Surface texture
  cx.beginPath();cx.arc(CX,CY,20,0,6.28);
  cx.strokeStyle='rgba(255,200,50,0.4)';cx.lineWidth=1;cx.stroke();
  // Sunspot
  if(Math.sin(frame*0.012)>0.2){
    cx.beginPath();cx.arc(CX+6,CY+4,2,0,6.28);
    cx.fillStyle='rgba(180,100,0,0.55)';cx.fill();
  }
  if(Math.sin(frame*0.018+1)>0.4){
    cx.beginPath();cx.arc(CX-5,CY-5,1.5,0,6.28);
    cx.fillStyle='rgba(180,100,0,0.4)';cx.fill();
  }
  cx.fillStyle='#fffde0';cx.font='bold 7px monospace';
  cx.textAlign='center';cx.fillText('SOL',CX,CY+3);
}

function drawPlanets(){
  PLANETS.forEach((p,i)=>{
    const{x,y}=getPlanetXY(p);

    // Saturn rings (behind planet)
    if(p.rings){
      cx.save();cx.translate(x,y);cx.scale(1,0.28);
      cx.beginPath();cx.arc(0,0,p.r+12,0,6.28);
      cx.strokeStyle='rgba(228,209,145,0.6)';cx.lineWidth=5;cx.stroke();
      cx.beginPath();cx.arc(0,0,p.r+7,0,6.28);
      cx.strokeStyle='rgba(200,180,110,0.35)';cx.lineWidth=2.5;cx.stroke();
      cx.restore();
    }

    // Atmosphere glow
    const rr=parseInt(p.color.slice(1,3),16);
    const gg=parseInt(p.color.slice(3,5),16);
    const bb=parseInt(p.color.slice(5,7),16);
    cx.beginPath();cx.arc(x,y,p.r+5,0,6.28);
    cx.fillStyle=`rgba(${rr},${gg},${bb},0.13)`;cx.fill();
    cx.beginPath();cx.arc(x,y,p.r+3,0,6.28);
    cx.fillStyle=`rgba(${rr},${gg},${bb},0.1)`;cx.fill();

    // Planet body
    cx.beginPath();cx.arc(x,y,p.r,0,6.28);
    cx.fillStyle=p.color;cx.fill();

    // Surface detail
    if(i===2){ // Earth — blue shimmer + cloud band
      cx.save();cx.beginPath();cx.arc(x,y,p.r,0,6.28);cx.clip();
      cx.fillStyle='rgba(34,100,60,0.5)';
      cx.fillRect(x-p.r,y-1,p.r*0.6,p.r*0.8);
      cx.fillRect(x+p.r*0.2,y+1,p.r*0.5,p.r*0.6);
      cx.fillStyle='rgba(255,255,255,0.18)';
      cx.fillRect(x-p.r,y-p.r*0.3,p.r*2,p.r*0.25);
      cx.restore();
      cx.beginPath();cx.arc(x,y,p.r,0,6.28);
      cx.strokeStyle='rgba(150,200,255,0.3)';cx.lineWidth=1;cx.stroke();
    }
    if(i===4){ // Jupiter bands
      cx.save();cx.beginPath();cx.arc(x,y,p.r,0,6.28);cx.clip();
      cx.fillStyle='rgba(180,120,60,0.35)';
      cx.fillRect(x-p.r,y-3,p.r*2,4);
      cx.fillRect(x-p.r,y+5,p.r*2,3);
      cx.fillRect(x-p.r,y-8,p.r*2,2.5);
      cx.fillStyle='rgba(220,160,80,0.2)';
      cx.fillRect(x-p.r,y+1,p.r*2,2);
      cx.restore();
      // Great Red Spot
      cx.save();cx.beginPath();cx.arc(x,y,p.r,0,6.28);cx.clip();
      cx.beginPath();cx.ellipse(x+4,y+5,3,2,0,0,6.28);
      cx.fillStyle='rgba(200,80,50,0.6)';cx.fill();
      cx.restore();
    }
    if(i===5){ // Saturn surface bands
      cx.save();cx.beginPath();cx.arc(x,y,p.r,0,6.28);cx.clip();
      cx.fillStyle='rgba(180,160,80,0.3)';
      cx.fillRect(x-p.r,y-2,p.r*2,3);
      cx.fillRect(x-p.r,y+4,p.r*2,2);
      cx.restore();
    }
    if(i===6){ // Uranus tilt line
      cx.save();cx.beginPath();cx.arc(x,y,p.r,0,6.28);cx.clip();
      cx.strokeStyle='rgba(120,230,230,0.3)';cx.lineWidth=2;
      cx.beginPath();cx.moveTo(x-p.r,y);cx.lineTo(x+p.r,y+2);cx.stroke();
      cx.restore();
    }
    if(i===0){ // Mercury craters
      cx.save();cx.beginPath();cx.arc(x,y,p.r,0,6.28);cx.clip();
      cx.beginPath();cx.arc(x-1,y-0.5,0.7,0,6.28);
      cx.strokeStyle='rgba(80,80,80,0.6)';cx.lineWidth=0.5;cx.stroke();
      cx.restore();
    }

    // Planet outline
    cx.beginPath();cx.arc(x,y,p.r,0,6.28);
    cx.strokeStyle=`rgba(${rr},${gg},${bb},0.5)`;cx.lineWidth=0.5;cx.stroke();

    // Moon (Earth)
    if(p.moons){
      p.moonAngle+=0.022;
      const mx=x+Math.cos(p.moonAngle)*p.moonDist;
      const my=y+Math.sin(p.moonAngle)*p.moonDist*0.55;
      cx.beginPath();cx.arc(mx,my,1.8,0,6.28);
      cx.fillStyle='#cccccc';cx.fill();
      cx.beginPath();cx.arc(mx,my,1.8,0,6.28);
      cx.strokeStyle='rgba(200,200,200,0.4)';cx.lineWidth=0.5;cx.stroke();
    }

    // Label
    cx.fillStyle='rgba(200,225,210,0.7)';
    cx.font='8px monospace';cx.textAlign='center';
    cx.fillText(p.name,x,y-p.r-5);
  });
}

function drawHUD(){
  // Speed legend / info
  cx.fillStyle='rgba(0,10,5,0.7)';
  cx.fillRect(6,6,178,50);
  cx.strokeStyle='rgba(100,180,255,0.25)';cx.lineWidth=0.5;cx.strokeRect(6,6,178,50);
  cx.fillStyle='#88ccff';cx.font='bold 9px monospace';cx.textAlign='left';
  cx.fillText('SOLAR SYSTEM — REAL ORBITS',12,20);
  cx.fillStyle='rgba(150,200,255,0.65)';cx.font='8px monospace';
  cx.fillText('8 PLANETS  •  ASTEROID BELT',12,34);
  cx.fillText('KEPLER ELLIPTICAL MECHANICS',12,46);
}

function updatePlanets(){
  const ts=0.00065;
  PLANETS.forEach(p=>{
    p.angle+=((2*Math.PI)/p.period)*ts;
  });
}

function tick(){
  cx.clearRect(0,0,W,H);
  cx.fillStyle='#000008';cx.fillRect(0,0,W,H);
  drawStars();
  drawShoots();
  drawOrbits();
  drawAsteroids();
  drawSun();
  drawPlanets();
  drawHUD();
  updatePlanets();
  frame++;
  requestAnimationFrame(tick);
}

tick();
</script>


</div>

<!--h2 without bottom border-->
<div id="user-content-toc">
  <ul align="center">
    <summary><h2 style="display: inline-block">Confusion is part of Programming</h2></summary>
  </ul>
</div>


<!--Intro start-->
- 🔭 I’m currently working on **Python, LangChain, Supabase**

- 🌱 I’m currently learning **React Native, Nextjs, AWS**

- 💬 Ask me about **Python, Generative AI, Mobile App Development, SaaS**

- 📫 Feel free to reach me out **[aravindh1653@gmail.com](mailto:aravindh1653@gmail.com)**


<div align="center"> 
  <a href="mailto:aravindh1653@gmail.com">
    <img src="https://img.shields.io/badge/Gmail-333333?style=for-the-badge&logo=gmail&logoColor=red" />
  </a>
  <a href="[https://linkedin.com/in/amitramrakhyani](https://www.linkedin.com/in/aravindhanb/)" target="_blank">
    <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" target="_blank" />
  </a>
</div>


<!--- stats & Trophy (start) -->
<p align="center">
  <!--- stats (start) -->
<table align="center">
<tr border="none">
  <td width="50%" align="center">
    <img  align="center"  src="https://github-readme-stats.anuraghazra1.vercel.app/api/top-langs/?username=amyth9&theme=react&hide_border=false&no-bg=true&no-frame=true&langs_count=7"/>
  </td>
</tr>
</table>
<!--- stats (end) -->

<!--- trophy (start) -->
<div align=center>
  <a href="https://github.com/ryo-ma/github-profile-trophy" title="Go to Source">
      <img align="center" width=84% src="https://github-profile-trophy.vercel.app/?username=amyth9&theme=tokyonight&row=1&column=7&margin-h=15&margin-w=5&no-bg=true" alt="TROPHY" />
    </a>
</div>
<!--- trophy (start) -->

<br/>

</p>        
<!--- stats (end) -->
<div align="center">
<h2 align="center">Skills</h2>
    <div align="center">
        <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" /></a>
        <a href="https://www.langchain.com/"><img src="https://img.shields.io/badge/LangChain-%2335495e.svg?style=for-the-badge" /></a>
        <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" /></a>
        <a href="https://reactnative.dev/"><img src="https://img.shields.io/badge/react_native-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB" /></a>
        <a href="https://nextjs.org/"><img src="https://img.shields.io/badge/Next-black?style=for-the-badge&logo=next.js&logoColor=white" /></a>
    </div>
    <div align="center">
        <a href="https://supabase.com/"><img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" /></a>
        <a href="https://www.mongodb.com/"><img src="https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white" /></a>
        <a href="https://expo.dev/"><img src="https://img.shields.io/badge/expo-1C1E24?style=for-the-badge&logo=expo&logoColor=#D04A37" /></a>
        <a href="https://www.typescriptlang.org/"><img src="https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white" /></a>
    </div>
</div>
<br/>

<!--h1 without bottom border-->
<div id="user-content-toc">
  <ul align="center">
    <summary><h2 style="display: inline-block">⚒️ Languages-Frameworks-Tools ⚒️</h2></summary>
  </ul>
<!--tech stack icons-->
<p align="center">
  <a href="https://www.python.org/"><img src="https://skillicons.dev/icons?i=py" /></a>&nbsp;
  <a href="https://fastapi.tiangolo.com/"><img src="https://skillicons.dev/icons?i=fastapi" /></a>&nbsp;
  <a href="https://nextjs.org/"><img src="https://skillicons.dev/icons?i=nextjs" /></a>&nbsp;
  <a href="https://supabase.com/"><img src="https://skillicons.dev/icons?i=supabase" /></a>&nbsp;
  <a href="https://www.typescriptlang.org/"><img src="https://skillicons.dev/icons?i=ts" /></a>&nbsp;
  <a href="https://www.mongodb.com/"><img src="https://skillicons.dev/icons?i=mongodb" /></a>&nbsp;
  <a href="https://react.dev/"><img src="https://skillicons.dev/icons?i=react" /></a>&nbsp;
  <a href="https://www.javascript.com/"><img src="https://skillicons.dev/icons?i=js" /></a>&nbsp;
  <a href="https://www.linux.org/"><img src="https://skillicons.dev/icons?i=linux" /></a>&nbsp;
  <a href="https://www.docker.com/"><img src="https://skillicons.dev/icons?i=docker" /></a><br>
  <a href="https://git-scm.com/"><img src="https://skillicons.dev/icons?i=git" /></a>&nbsp;
  <a href="https://github.com/"><img src="https://skillicons.dev/icons?i=github" /></a>&nbsp;
  <a href="https://aws.amazon.com/"><img src="https://skillicons.dev/icons?i=aws" /></a>&nbsp;
  <a href="https://flask.palletsprojects.com/en/"><img src="https://skillicons.dev/icons?i=flask" /></a>&nbsp;
  <a href="https://www.postgresql.org/"><img src="https://skillicons.dev/icons?i=postgres" /></a>&nbsp;
  <a href="https://www.mysql.com/"><img src="https://skillicons.dev/icons?i=mysql" /></a>&nbsp;
  <a href="https://nodejs.org/"><img src="https://skillicons.dev/icons?i=nodejs" /></a>&nbsp;
  <a href="https://expressjs.com/"><img src="https://skillicons.dev/icons?i=express" /></a>&nbsp;
  <a href="https://isocpp.org/"><img src="https://skillicons.dev/icons?i=cpp" /></a>&nbsp;
  <a href="https://pytorch.org/"><img src="https://skillicons.dev/icons?i=pytorch" /></a><br>
  <a href="https://www.tensorflow.org/"><img src="https://skillicons.dev/icons?i=tensorflow" /></a>&nbsp;
  <a href="https://opencv.org/"><img src="https://skillicons.dev/icons?i=opencv" /></a>&nbsp;
  <a href="https://firebase.google.com/"><img src="https://skillicons.dev/icons?i=firebase" /></a>&nbsp;
  <a href="https://www.postman.com/"><img src="https://skillicons.dev/icons?i=postman" /></a>&nbsp;
  <a href="https://vercel.com/"><img src="https://skillicons.dev/icons?i=vercel" /></a>&nbsp;
  <a href="https://www.arduino.cc/"><img src="https://skillicons.dev/icons?i=arduino" /></a>&nbsp;
  <a href="https://html.com/"><img src="https://skillicons.dev/icons?i=html" /></a>&nbsp;
  <a href="https://skillicons.dev/icons?i=css"><img src="https://skillicons.dev/icons?i=css" /></a>&nbsp;
  <a href="https://ubuntu.com/"><img src="https://skillicons.dev/icons?i=ubuntu" /></a>&nbsp;
  <a href="https://www.markdownguide.org/"><img src="https://skillicons.dev/icons?i=md" /></a><br>
  <a href="https://code.visualstudio.com/"><img src="https://skillicons.dev/icons?i=vscode" /></a>&nbsp;
  <a href="https://discord.com/"><img src="https://skillicons.dev/icons?i=discord" /></a>&nbsp;
  <a href="https://www.figma.com/"><img src="https://skillicons.dev/icons?i=figma" /></a>&nbsp;
  <a href="https://www.notion.so/"><img src="https://skillicons.dev/icons?i=notion" /></a><br>
</p>
</div>

<!-- Connect with me -->
<!--h2 without bottom border-->
<div id="user-content-toc">
  <ul align="center">
    <summary><h2 style="display: inline-block">Connect With Me🤝</h2></summary>
  </ul>chrome-extension://ajiejmhbejpdgkkigpddefnjmgcbkenk/popup.html#
</div>

<!--icons and links-->
<p align="center">
<a href="https://aravindh-portfolio-rsds.onrender.com/portfolio/" target="blank"><img align="center" src="https://github.com/user-attachments/assets/2ea1190d-ce9c-4b82-af1f-9ab0b5a48506" alt="portfolio" height="50" width="50" /></a>
<a href="https://www.linkedin.com/in/aravindhanb/" target="blank"><img align="center" src="https://user-images.githubusercontent.com/88904952/234979284-68c11d7f-1acc-4f0c-ac78-044e1037d7b0.png" alt="linkedin" height="50" width="50" /></a>
<a href="https://x.com/aravindh213" target="blank"><img align="center" src="https://user-images.githubusercontent.com/88904952/234980676-61bfb021-ecc8-48f7-88e6-34c1b06c4a58.png" alt="X" height="50" width="50" /></a> 
<!-- <a href="https://leetcode.com/u/" target="blank"><img align="center" src="https://github.com/user-attachments/assets/155dc343-9754-473d-bc54-5baa6c0a5604" alt="leetcode" height="50" width="50" /></a> -->

</p>

<!--horizontal divider(gradiant)-->
<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif">
