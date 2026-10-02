/* Graphen rechnen mit expliziten Modellen; kein eval und keine externen Dienste. */
document.querySelectorAll('[data-graph-lab]').forEach(lab => {
 const c=JSON.parse(lab.dataset.graphLab), input=lab.querySelector('[data-lab-x]'), aInput=lab.querySelector('[data-lab-a]');
 const X=x=>65+(x-c.xmin)*510/(c.xmax-c.xmin),Y=y=>315-(y-c.ymin)*270/(c.ymax-c.ymin);
 const fmt=v=>Number(v.toFixed(4)).toLocaleString('de-DE',{maximumFractionDigits:4});
 const bin=[1,6,15,20,15,6,1].map(x=>x/64);
 const f=(x,a)=>({power:()=>x*x,exponential:()=>2**x,trig:()=>Math.sin(x),derivative:()=>x*x,cubic:()=>x*x*x-3*x,integral:()=>x-1,growth:()=>8-6*Math.exp(-.5*x),inverse:()=>Math.abs(x)<1e-9?null:1/x,parameter:()=>a*x*x+1,binomial:()=>bin[Math.round(x)],sequence:()=>4*.5**x}[c.kind]());
 const update=()=>{
   const x=Number(input.value),a=aInput?Number(aInput.value):1,y=f(x,a),point=lab.querySelector('.lab-point'),guide=lab.querySelector('.lab-guide');
   lab.querySelector('[data-x-output]').value=fmt(x);
   if(aInput){lab.querySelector('[data-a-output]').value=fmt(a);const curve=lab.querySelector('.lab-curve'),pts=[];for(let i=0;i<=500;i++){const xx=c.xmin+(c.xmax-c.xmin)*i/500;pts.push(`${i?'L':'M'}${X(xx)},${Y(f(xx,a))}`);}curve.setAttribute('d',pts.join(' '));}
   point.style.display=y===null?'none':'';guide.style.display=y===null?'none':'';
   if(y!==null){point.setAttribute('cx',X(x));point.setAttribute('cy',Y(y));guide.setAttribute('d',`M${X(x)} ${Y(0)}V${Y(y)}H${X(0)}`);}
   let result=y===null?'Bei x = 0 gibt es keinen Funktionswert: Durch 0 darfst du nicht teilen.':`Punkt (${fmt(x)} | ${fmt(y)}): Eingabe ${fmt(x)} → Funktionswert ${fmt(y)}.`;
   if(c.kind==='parameter')result+=` a = ${fmt(a)}: ${a===0?'waagerechte Gerade bei y = 1':a>0?'nach oben geöffnet':'nach unten geöffnet'}.`;
   if(c.kind==='derivative'){lab.querySelector('.lab-tangent').setAttribute('d',`M${X(c.xmin)} ${Y(2*x*c.xmin-x*x)}L${X(c.xmax)} ${Y(2*x*c.xmax-x*x)}`);result+=` Tangentensteigung ${fmt(2*x)}: ${x===0?'waagerecht':x>0?'steigend':'fallend'}.`;}
   if(c.kind==='integral'){
     const b=x,m=Math.min(1,b),neg=m*m/2-m,pos=b>1?(b-1)**2/2:0;
     lab.querySelector('.area-negative').setAttribute('d',`M${X(0)} ${Y(0)}L${X(0)} ${Y(-1)}L${X(m)} ${Y(m-1)}L${X(m)} ${Y(0)}Z`);
     lab.querySelector('.area-positive').setAttribute('d',b>1?`M${X(1)} ${Y(0)}L${X(b)} ${Y(b-1)}L${X(b)} ${Y(0)}Z`:'');
     result=`Von 0 bis ${fmt(b)}: Integral = ${fmt(neg+pos)}; geometrische Fläche = ${fmt(-neg+pos)}. Höhe am rechten Rand = ${fmt(y)}.`;
   }
   if(c.kind==='binomial')result=`P(X = ${x}) = ${fmt(y)} = ${fmt(100*y)} %. P(X ≤ ${x}) = ${fmt(bin.slice(0,x+1).reduce((a,b)=>a+b,0))}.`;
   if(c.kind==='sequence')result=`Schritt n = ${x}: aₙ = ${fmt(y)}. Vom vorherigen zum nächsten Punkt gilt immer Faktor 0,5.`;
   if(c.kind==='growth')result+=` Änderungsrate ${fmt(3*Math.exp(-.5*x))}: positiv, aber immer kleiner.`;
   if(y!==null && (y<c.ymin||y>c.ymax))result+=' Der Punkt liegt außerhalb des sichtbaren Ausschnitts.';
   lab.querySelector('[data-lab-reading]').textContent=result;
   lab.querySelector('#lab-desc').textContent=c.meaning+' '+result;
 };
 input.addEventListener('input',update);if(aInput)aInput.addEventListener('input',update);
 lab.querySelector('[data-lab-reset]').addEventListener('click',()=>{input.value=c.x;if(aInput)aInput.value=1;update();});update();
});
