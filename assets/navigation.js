/* Die Suche verwendet denselben Kapitelbestand wie der Seitenaufbau. */
function searchChapters(entries, query) {
  const q=normalized(query.trim()),terms=q.split(/\s+/).filter(Boolean);
  if(!terms.length)return [];
  return entries.map((entry,index)=>{
    const title=normalized(entry.title),hay=normalized(`${entry.stage} ${entry.title} ${entry.keywords}`);
    if(!terms.every(term=>hay.includes(term)))return null;
    const score=(title===q?100:0)+(title.startsWith(q)?30:0)+terms.reduce((sum,t)=>sum+(title.split(/[^a-z0-9]+/).some(w=>w.startsWith(t))?8:title.includes(t)?4:0),0);
    return {entry,index,score};
  }).filter(Boolean).sort((a,b)=>b.score-a.score||a.index-b.index).map(x=>x.entry);
}
const navigationToggle=document.querySelector('.nav-toggle');
if(navigationToggle){
 const rail=document.querySelector('.learning-rail');
 navigationToggle.addEventListener('click',()=>{
   const open=navigationToggle.getAttribute('aria-expanded')!=='true';
   navigationToggle.setAttribute('aria-expanded',String(open));rail.classList.toggle('nav-open',open);
   navigationToggle.textContent=open?'Menü schließen':'Menü';
 });
}
const globalSearch=document.querySelector('#global-search');
if(globalSearch){
 const container=document.querySelector('.global-search'),panel=document.querySelector('#search-panel'),list=document.querySelector('#search-results'),status=document.querySelector('#search-status');
 const entries=window.MATHEPFAD_SEARCH||[],root=document.body.dataset.root||'';
 let active=-1,links=[];
 const close=()=>{panel.hidden=true;globalSearch.setAttribute('aria-expanded','false');globalSearch.removeAttribute('aria-activedescendant');active=-1;};
 const select=index=>{
   active=index;links.forEach((link,i)=>link.setAttribute('aria-selected',String(i===active)));
   if(active>=0){globalSearch.setAttribute('aria-activedescendant',links[active].id);links[active].scrollIntoView({block:'nearest'});}else globalSearch.removeAttribute('aria-activedescendant');
 };
 const markTitle=(title,query,node)=>{
   const terms=query.toLocaleLowerCase('de').trim().split(/\s+/).filter(Boolean);
   // Mark only exact spans of the source title; normalization still applies to matching.
   const lower=title.toLocaleLowerCase('de');let cursor=0;
   while(cursor<title.length){
     let start=title.length,len=0;
     for(const t of terms){const i=lower.indexOf(t,cursor);if(i>=0&&(i<start||(i===start&&t.length>len))){start=i;len=t.length;}}
     node.append(document.createTextNode(title.slice(cursor,start)));
     if(!len)break;
     const mark=document.createElement('mark');mark.textContent=title.slice(start,start+len);node.append(mark);cursor=start+len;
   }
 };
 const update=()=>{
   const query=globalSearch.value.trim();list.replaceChildren();links=[];active=-1;globalSearch.removeAttribute('aria-activedescendant');
   if(!query){close();return;}
   const matches=searchChapters(entries,query);
   matches.forEach((entry,i)=>{
     const li=document.createElement('li');li.setAttribute('role','presentation');
     const link=document.createElement('a');link.href=root+entry.path;link.id=`search-result-${i}`;link.setAttribute('role','option');link.setAttribute('aria-selected','false');link.tabIndex=-1;
     const label=document.createElement('strong');markTitle(entry.title,query,label);
     const meta=document.createElement('span');meta.textContent=`${entry.stage} · ${entry.type||'Kapitel'}${entry.course?' · '+entry.course:''}`;
     link.append(label,meta);li.append(link);list.append(li);links.push(link);
   });
   status.textContent=matches.length?`${matches.length} Treffer · direkt öffnen oder mit ↑ ↓ und Enter auswählen`:'Kein passendes Kapitel. Versuche einen kürzeren Begriff, z. B. „wurz“ oder „integral“.';
   panel.hidden=false;globalSearch.setAttribute('aria-expanded','true');
 };
 globalSearch.addEventListener('input',update);globalSearch.addEventListener('focus',update);
 globalSearch.addEventListener('keydown',event=>{
   if(event.key==='Escape'){event.preventDefault();close();return;}
   if(event.key==='ArrowDown'||event.key==='ArrowUp'){
     event.preventDefault();if(panel.hidden)update();if(!links.length)return;
     const next=event.key==='ArrowDown'?(active+1)%links.length:(active<=0?links.length-1:active-1);select(next);
   }else if(event.key==='Enter'&&!panel.hidden&&links.length){event.preventDefault();links[active<0?0:active].click();}
 });
 container.addEventListener('focusout',()=>setTimeout(()=>{if(!container.contains(document.activeElement))close();},0));
 document.addEventListener('pointerdown',event=>{if(!container.contains(event.target))close();});
}
