/* Progressive enhancement: Erklärungen und Lösungen funktionieren auch ohne JS. */
document.documentElement.classList.add('js-enabled');
function normalized(value) {
  return value.toLocaleLowerCase('de').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/ß/g, 'ss');
}

const levelSelect = document.querySelector('#task-level');
if (levelSelect) {
  const picks=[...document.querySelectorAll('[data-level-pick]')];
  const applyLevel = () => {
    let count = 0;
    document.querySelectorAll('[data-task-level]').forEach(task => {
      task.hidden = levelSelect.value !== 'alle' && task.dataset.taskLevel !== levelSelect.value;
      if (!task.hidden) count++;
    });
    document.querySelectorAll('[data-level-group]').forEach(group=>{group.hidden=levelSelect.value!=='alle'&&group.dataset.levelGroup!==levelSelect.value;});
    picks.forEach(p=>p.setAttribute('aria-current',String(p.dataset.levelPick===levelSelect.value)));
    document.querySelector('#task-count').textContent = `${count} Aufgaben · ${levelSelect.value==='alle'?'alle Niveaus':levelSelect.value}`;
    const visibleSolutions=[...document.querySelectorAll('.task:not([hidden]) [data-solution]')];
    const allOpen=visibleSolutions.length>0&&visibleSolutions.every(d=>d.open);
    const button=document.querySelector('[data-solutions]');
    button.setAttribute('aria-pressed',String(allOpen));button.textContent=allOpen?'Lösungen zuklappen':'Lösungen aufklappen';
    const url=new URL(location.href);if(levelSelect.value==='alle')url.searchParams.delete('niveau');else url.searchParams.set('niveau',levelSelect.value);
    history.replaceState(null,'',url);
  };
  levelSelect.addEventListener('change', applyLevel);
  picks.forEach(p=>p.addEventListener('click',event=>{event.preventDefault();levelSelect.value=p.dataset.levelPick;applyLevel();location.hash='aufgaben';document.querySelector('#aufgaben').scrollIntoView({block:'start'});}));
  const initial=new URLSearchParams(location.search).get('niveau');
  if(['Einfach','Mittel','Schwierig'].includes(initial))levelSelect.value=initial;
  applyLevel();
}

function revealLinkedTask() {
  let id;
  try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
  const target = document.getElementById(id);
  if (!target || !target.matches('[data-exercise-id]')) return;
  if (levelSelect) {
    levelSelect.value = 'alle';
    levelSelect.dispatchEvent(new Event('change'));
  }
  target.scrollIntoView({block: 'start'});
}
window.addEventListener('hashchange', revealLinkedTask);
revealLinkedTask();

document.querySelectorAll('[data-print]').forEach(button => button.addEventListener('click', () => window.print()));
document.querySelectorAll('[data-solutions]').forEach(button => {
  button.addEventListener('click', () => {
    const open = button.getAttribute('aria-pressed') !== 'true';
    document.querySelectorAll('.task:not([hidden]) [data-solution]').forEach(detail => { detail.open = open; });
    button.setAttribute('aria-pressed', String(open));
    button.textContent = open ? 'Lösungen zuklappen' : 'Lösungen aufklappen';
  });
});

const randomTaskButton=document.querySelector('[data-random-task]');
if(randomTaskButton){
 let previous=null;
 randomTaskButton.addEventListener('click',()=>{
  const visible=[...document.querySelectorAll('[data-task-level]')].filter(t=>!t.hidden);
  const pool=visible.length>1?visible.filter(t=>t!==previous):visible;
  if(!pool.length)return;
  const task=pool[Math.floor(Math.random()*pool.length)];previous=task;
  document.querySelectorAll('.random-selected').forEach(t=>t.classList.remove('random-selected'));
  task.querySelectorAll('details').forEach(d=>d.open=false);task.classList.add('random-selected');task.setAttribute('tabindex','-1');
  task.focus({preventScroll:true});task.scrollIntoView({block:'start',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
  document.querySelector('#random-task-status').textContent=`Deine Zufallsaufgabe: ${task.querySelector('h3').textContent}. Niveau ${task.dataset.taskLevel}.`;
 });
}
