/* Auswahl ist als URL teilbar. Keine Konten und keine Speicherung von Schülerdaten. */
const recapChecks=[...document.querySelectorAll('[data-recap-choice]')];
if(recapChecks.length){
 const cards=[...document.querySelectorAll('[data-recap-id]')],overviews=[...document.querySelectorAll('[data-recap-stage]')],presets=[...document.querySelectorAll('[data-recap-preset]')];
 const printButton=document.querySelector('#recap-print'),explanations=document.querySelector('#recap-explanations'),params=new URLSearchParams(location.search);
 const initial=params.has('kapitel')?new Set(params.get('kapitel').split(',')):null;
 const stage=['Q1','Q2','Q3','Q4'].includes(params.get('stufe'))?params.get('stufe'):'Q1';
 recapChecks.forEach(c=>{c.checked=initial?initial.has(c.value):c.dataset.stage===stage;});
 if(params.get('kurz')==='1')explanations.checked=false;
 const update=()=>{
   const checked=recapChecks.filter(c=>c.checked),ids=new Set(checked.map(c=>c.value)),stages=new Set(checked.map(c=>c.dataset.stage));
   let formulas=0;
   cards.forEach(card=>{card.hidden=!ids.has(card.dataset.recapId);if(!card.hidden)formulas+=card.querySelectorAll('.formula-card').length;});
   overviews.forEach(block=>block.hidden=!stages.has(block.dataset.recapStage));
   document.querySelectorAll('.recap-note').forEach(p=>p.hidden=!explanations.checked);
   document.querySelector('#recap-empty').hidden=ids.size>0;document.querySelector('#recap-scope').hidden=ids.size===0;
   document.querySelector('#recap-title').textContent=stages.size===1?`${[...stages][0]} · Meine Zusammenfassung`:'Meine Formelsammlung';
   document.querySelector('#recap-count').textContent=`${ids.size} Kapitel · ${formulas} Formel- und Merkkarten`;
   printButton.disabled=!ids.size;
   const url=new URL(location.href);url.searchParams.delete('stufe');url.searchParams.set('kapitel',[...ids].join(','));
   if(explanations.checked)url.searchParams.delete('kurz');else url.searchParams.set('kurz','1');
   history.replaceState(null,'',url);
   document.dispatchEvent(new Event('recapchange'));
   presets.forEach(button=>{const matches=stages.size===1&&stages.has(button.dataset.recapPreset)&&checked.length===recapChecks.filter(c=>c.dataset.stage===button.dataset.recapPreset).length;button.setAttribute('aria-pressed',String(matches));});
 };
 recapChecks.forEach(c=>c.addEventListener('change',update));explanations.addEventListener('change',update);
 presets.forEach(button=>button.addEventListener('click',()=>{recapChecks.forEach(c=>c.checked=c.dataset.stage===button.dataset.recapPreset);update();}));
 document.querySelector('[data-recap-all]').addEventListener('click',()=>{recapChecks.forEach(c=>c.checked=true);update();});
 document.querySelector('[data-recap-none]').addEventListener('click',()=>{recapChecks.forEach(c=>c.checked=false);update();});

 update();
}

const practiceButton=document.querySelector('#recap-practice');
if(practiceButton){
 let practice=false;
 document.querySelectorAll('.formula-card').forEach((card,index)=>{
  const cover=document.createElement('div');cover.className='recall-cover';cover.hidden=true;
  const text=document.createElement('p');text.textContent='Welche Formel oder Regel passt? Erkläre sie zuerst in eigenen Worten.';
  const button=document.createElement('button');button.type='button';button.textContent='Formel aufdecken';
  button.addEventListener('click',()=>{card.classList.remove('formula-covered');cover.hidden=true;});
  cover.append(text,button);card.querySelector('.math-line').after(cover);
 });
 practiceButton.addEventListener('click',()=>{
  practice=!practice;practiceButton.setAttribute('aria-pressed',String(practice));practiceButton.textContent=practice?'Abfragemodus beenden':'Formeln üben';
  document.querySelectorAll('.formula-card').forEach(card=>{card.classList.toggle('formula-covered',practice);card.querySelector('.recall-cover').hidden=!practice;});
 });
}
