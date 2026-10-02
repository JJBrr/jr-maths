/* Real PDF files, merged locally for an individual selection. No print dialog required. */
const pdfButton=document.querySelector('#recap-print');
if(pdfButton){
 const choices=[...document.querySelectorAll('[data-recap-choice]')],context=document.querySelector('#recap-explanations');
 const status=document.querySelector('#pdf-status'),result=document.querySelector('#pdf-result'),openLink=document.querySelector('#pdf-open'),shareButton=document.querySelector('#pdf-share');
 const root=document.body.dataset.root||'';let objectURL=null,readyBytes=null,readyHref=null,busy=false,revision=0;
 const reset=()=>{
   revision++;result.hidden=true;status.textContent='';readyBytes=null;readyHref=null;
   if(objectURL){URL.revokeObjectURL(objectURL);objectURL=null;}
 };
 document.addEventListener('recapchange',reset);
 const prepare=async()=>{
   if(busy)return;
   const chosen=choices.filter(x=>x.checked);if(!chosen.length){status.textContent='Wähle zuerst mindestens ein Kapitel.';return;}
   busy=true;const atRevision=revision;pdfButton.disabled=true;pdfButton.textContent='PDF wird erstellt …';status.textContent='Deine ausgewählten Kapitel werden vorbereitet.';result.hidden=true;
   const suffix=context.checked?'full':'compact',stage=chosen[0].dataset.stage;
   const fullStage=chosen.every(c=>c.dataset.stage===stage)&&chosen.length===choices.filter(c=>c.dataset.stage===stage).length;
   const filename=`JR-Maths-${fullStage?stage:'meine-Formelsammlung'}.pdf`;
   try{
     let href;
     if(fullStage){href=`${root}assets/pdfs/JR-Maths-${stage}-${suffix}.pdf`;}
     else if(chosen.length===1){href=`${root}assets/pdfs/${chosen[0].value}-${suffix}.pdf`;}
     else{
       if(!window.PDFLib)throw new Error('Die PDF-Funktion konnte nicht geladen werden. Lade die Seite bitte neu.');
       const merged=await PDFLib.PDFDocument.create();
       const buffers=await Promise.all(chosen.map(async c=>{
         const response=await fetch(`${root}assets/pdfs/${c.value}-${suffix}.pdf`);
         if(!response.ok)throw new Error('Ein Kapitel-PDF konnte nicht geladen werden. Bitte versuche es erneut.');
         return response.arrayBuffer();
       }));
       for(const bytes of buffers){const source=await PDFLib.PDFDocument.load(bytes);const pages=await merged.copyPages(source,source.getPageIndices());pages.forEach(p=>merged.addPage(p));}
       merged.setTitle('JR Maths - Meine Formelsammlung');merged.setAuthor('JR Maths');
       const bytes=await merged.save();if(atRevision!==revision)return;
       readyBytes=bytes;objectURL=URL.createObjectURL(new Blob([bytes],{type:'application/pdf'}));href=objectURL;
     }
     if(atRevision!==revision)return;
     readyHref=href;openLink.href=href;openLink.download=filename;openLink.textContent='PDF öffnen / speichern';
     shareButton.dataset.filename=filename;
     shareButton.hidden=true;
     if(typeof File!=='undefined' && navigator.canShare){
       try{
         const supported=navigator.canShare({files:[new File([''],filename,{type:'application/pdf'})]});
         if(supported && readyBytes)shareButton.hidden=false;
         else if(supported){
           fetch(href).then(r=>{if(!r.ok)throw new Error('PDF');return r.arrayBuffer();}).then(buffer=>{
             if(atRevision===revision){readyBytes=new Uint8Array(buffer);shareButton.hidden=false;}
           }).catch(()=>{ /* Direct PDF link remains available. */ });
         }
       }catch{ /* Sharing is optional; opening the PDF still works. */ }
     }
     result.hidden=false;status.textContent=`PDF bereit: ${chosen.length} Kapitel. Tippe auf „PDF öffnen / speichern“.`;
   }catch(error){if(atRevision===revision)status.textContent=error.message||'PDF konnte nicht erstellt werden. Bitte versuche es noch einmal.';}
   finally{busy=false;pdfButton.disabled=!choices.some(c=>c.checked);pdfButton.textContent='PDF erstellen';}
 };
 pdfButton.addEventListener('click',prepare);
 shareButton.addEventListener('click',async()=>{
   try{if(!readyBytes)return;const file=new File([readyBytes],shareButton.dataset.filename,{type:'application/pdf'});await navigator.share({files:[file],title:'JR Maths · Formelsammlung'});}
   catch(error){if(error.name!=='AbortError')status.textContent='Nutze bitte „PDF öffnen / speichern“. Dort kannst du die Datei über das Teilen-Menü sichern.';}
 });
}
