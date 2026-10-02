"""Modulare JSON-Kapitel → statisches HTML. Keine externen Python-Pakete."""
from pathlib import Path
from html import escape as E
import json, shutil, re
from mathtext import M, F
from graph_lab import graph
from recap import page as recap_page, recap_entry

ROOT=Path(__file__).resolve().parent
BASE=ROOT/'dist'
STAGES=[
('Klasse 10','klasse-10','Sicher in die Oberstufe','Potenzen, Wachstum, Körper, Trigonometrie und Zufall. Die vorhandenen G9-Kapitel, erweitert um Beispiele und Aufgaben.'),
('E-Phase','e-phase','Grundlagen der Analysis','Funktionen verstehen, Änderungen messen und mit Ableitungen arbeiten. E1 und E2 werden gemeinsam geführt; die Schule legt die Verteilung fest.'),
('Q1','q1','Integrale und Modelle','Aus Änderungsraten werden Bestände. Flächen, Wachstum und vertiefende Integrationsmethoden verbinden die Ideen.'),
('Q2','q2','Funktionen und Raum','Neue Funktionsklassen, Vektoren, Geraden und Ebenen. Matrizen stehen als Wahlthemen bereit.'),
('Q3','q3','Zufall und Statistik','Wahrscheinlichkeiten verstehen, Verteilungen berechnen und Daten beurteilen. Hypothesentests sind im LK verbindlich.'),
('Q4','q4','Parameter und Argumente','Funktionenscharen untersuchen und Wissen vernetzen. Problemlösen und komplexe Zahlen ergänzen den Lernpfad.'),
('Abiturtraining','abiturtraining','Wissen zusammenführen','Eigene mehrteilige Trainingsaufgaben in Analysis, Geometrie und Stochastik. Mit vollständigen Lösungswegen, auch für anspruchsvollere Teilfragen.'),
('Realschule','realschule','Fit für den mittleren Abschluss','Eigenständiger Lernpfad für Klasse 10 mit Grundlagenwiederholung. Körper, Ähnlichkeit, Trigonometrie, Wachstum und Daten.')]
STAGE_MAP={s[0]:s for s in STAGES}
UNITS=[json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'content').glob('*.json')]
UNITS.sort(key=lambda u:(list(STAGE_MAP).index(u['stage']),[int(n) for n in re.findall(r'\d+',u['id'])]))
TEMPLATE=(ROOT/'templates/base.html').read_text(encoding='utf-8')

def validate():
    ids,slugs,task_ids=set(),set(),set()
    for u in UNITS:
        assert u['id'] not in ids and u['slug'] not in slugs,'Doppelte Kapitelkennung'
        assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',u['slug'])
        ids.add(u['id']);slugs.add(u['slug'])
        for field in ('name','lead','reference','prerequisites','course'):
            assert u.get(field),f"{u['id']}: {field} fehlt"
        assert len(u['concepts'])>=3 and len(u['examples'])>=3 and len(u['tasks'])>=6
        for task in u['tasks']:
            assert task['id'] not in task_ids,'Doppelte Aufgabenkennung'
            task_ids.add(task['id'])
            assert task['question'] and (task.get('solution') or task.get('steps'))
            assert task['level'].split(' · ')[0] in ('Einfach','Mittel','Schwierig'), 'Unbekanntes Aufgabenniveau'
    return len(task_ids)

def badge(course):
    kind='optional' if 'Wahl' in course else 'lk' if course=='LK' else ''
    return f'<span class="tag {kind}">{E(course)}</span>'

def link(u,root):return root+u['slug']+'/index.html'

def shell(title,desc,content,root='',stage=''):
    nav=f'<a class="stage-link" href="{root}index.html" {"aria-current=page" if not stage else ""}>Übersicht</a>'
    for name,slug,_,_ in STAGES:
        nav+=f'<a class="stage-link {"active-stage" if name==stage else ""}" href="{root}{slug}/index.html" {"aria-current=page" if name==stage and title.startswith(stage+" · ") else ""}>{name}</a>'
        if name==stage:
            chapter_links=''.join(f'<a href="{link(u,root)}" {"aria-current=page" if u["name"]==title else ""}><span>{E(u["id"])}</span>{E(u["name"])}</a>' for u in UNITS if u['stage']==stage)
            nav+=f'<div class="rail-chapters">{chapter_links}</div>'
    values=dict(extra_scripts=(f'<script src="{root}assets/exam-bank.js" defer></script>' if stage=='Probeklausur' else '')+(f'<script src="{root}assets/vendor/pdf-lib.min.js" defer></script><script src="{root}assets/pdf-export.js" defer></script>' if stage=='Formelsammlung' else ''),formula_current='aria-current=page' if stage=='Formelsammlung' else '',recap_query='?stufe='+stage if stage in ('Q1','Q2','Q3','Q4') else '',title=E(title),description=E(desc),root=root,nav=nav,content=content,location=E(stage if stage not in ('','info') else 'Mathematik · Hessen'))
    return re.sub(r'\{\{(\w+)\}\}',lambda m:values[m.group(1)],TEMPLATE)

def write(slug,title,desc,content,stage=''):
    path=BASE/slug/'index.html' if slug else BASE/'index.html'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(shell(title,desc,content,'../' if slug else '',stage),encoding='utf-8')

def unit_card(u,root):
    keywords=' '.join([u['name'],u['lead'],u['stage'],u['course'],u['reference']]+[c['title'] for c in u['concepts']])
    return f'''<a class="unit-card" data-chapter data-search="{E(keywords,quote=True)}" href="{link(u,root)}"><div class="card-tags"><span class="tag">{E(u['id'])}</span>{badge(u['course'])}</div><h3>{E(u['name'])}</h3><p>{E(u['lead'])}</p><div class="card-meta">{len(u['examples'])} Beispiele · {len(u['tasks'])} Aufgaben</div><b>Kapitel öffnen →</b></a>'''

def stage_section(stage,root,index,heading=True):
    name,slug,title,desc=STAGE_MAP[stage]
    units=[u for u in UNITS if u['stage']==stage]
    header=f'<div class="stage-heading"><div><span class="eyebrow">{name.upper()}</span><h2>{title}</h2><p>{desc}</p></div><span class="stage-index" aria-hidden="true">{index:02}</span></div>' if heading else ''
    return f'<section class="curriculum" id="{slug}" data-stage-section>{header}<div class="unit-grid">'+''.join(unit_card(u,root) for u in units)+'</div></section>'

def search_box():
    return ''

def steps(obj):
    return '<ol class="steps">'+''.join(f'<li>{M(s)}</li>' for s in (obj.get('steps') or [obj['solution']]))+'</ol>'

def exercise(task,i):
    level=task['level'].split(' · ')[0]
    hint=f'<details class="task-hint"><summary>Denkimpuls anzeigen</summary><p>{M(task["hint"])}</p></details>' if task.get('hint') else ''
    return f'''<article class="task" id="{E(task['id'])}" data-exercise-id="{E(task['id'])}" data-task-level="{E(level)}"><div class="task-top"><span class="task-nr">AUFGABE {i:02}</span><span class="level">{E(task['level'])}</span><a class="task-link" href="#{E(task['id'])}" aria-label="Direktlink zu Aufgabe {i}">#{E(task['id'])}</a></div><h3>{E(task['title'])}</h3><p>{M(task['question'])}</p>{hint}<details data-solution><summary>Lösung Schritt für Schritt</summary><div class="answer">{steps(task)}</div></details></article>'''

def chapter(u):
    root='../';stage=u['stage']
    note='<p class="note">'+E(u['note'])+'</p>' if u.get('note') else ''
    intro=f'''<header class="chapter-intro"><div class="exam-chapter-actions js-only"><button type="button" data-exam-topic="{E(u['id'])}" aria-pressed="false">＋ Für Probeklausur merken</button><a href="../probeklausur/index.html">Zur Probeklausur →</a></div><div class="badges"><span class="tag">{E(stage)}</span>{badge(u['course'])}</div><span class="eyebrow">{E(u['reference'])}</span><h1>{E(u['name'])}</h1><p>{E(u['lead'])}</p><div class="anchors"><a href="#erklaerung">Erklärung</a><a href="#beispiele">{len(u['examples'])} Beispiele</a><a href="#aufgaben">{len(u['tasks'])} Aufgaben</a></div><div class="prerequisites"><strong>Das solltest du schon können</strong><p>{E(u['prerequisites'])}</p></div>{note}</header>'''
    counts={level:sum(t['level'].split(' · ')[0]==level for t in u['tasks']) for level in ('Einfach','Mittel','Schwierig')}
    descriptions={'Einfach':'Eine Idee üben · Sicherheit gewinnen','Mittel':'Schritte verbinden · Zusammenhänge nutzen','Schwierig':'Übertragen · entscheiden · begründen'}
    choices=''.join(f'<a href="?niveau={level}#aufgaben" data-level-pick="{level}"><span class="level-number">{i+1:02}</span><strong>{level}</strong><span>{descriptions[level]}</span><b>{counts[level]} Aufgaben →</b></a>' for i,level in enumerate(counts))
    picker=f'<nav class="level-picker" aria-label="Aufgabenniveau wählen"><div><span class="eyebrow">DEIN EINSTIEG</span><h2>Auf welchem Niveau möchtest du üben?</h2><p>Wähle eine Stufe. Du kannst jederzeit wechseln. „Schwierig“ bedeutet mehr eigene Entscheidungen, nicht einfach größere Zahlen.</p></div><div class="level-choices">{choices}</div></nav>'
    understanding=u.get('understanding')
    why=''
    if understanding:
        why=f'<section class="understanding"><span class="eyebrow">DAS STECKT DAHINTER</span><h3>Wozu brauche ich das?</h3><p>{M(understanding["why"])}</p><h3>Die Idee in einfachen Worten</h3><p>{M(understanding["idea"])}</p><details class="think-first"><summary>Verständnischeck: {E(understanding["check"])}</summary><p>{M(understanding["answer"])}</p></details></section>'
    concepts=''.join(f'<article class="concept"><h3>{E(c["title"])}</h3><p>{M(c["explanation"])}</p><div class="math-line">{F(c["example"])}</div></article>' for c in u['concepts'])
    examples=''.join(f'<article class="example"><span class="tag">{E(ex["level"])}</span><h3>{E(ex["title"])}</h3><p>{M(ex["question"])}</p>{steps(ex)}</article>' for ex in u['examples'])
    explanation=f'<section class="chapter-section" id="erklaerung"><div class="section-title"><span class="eyebrow">01 · VERSTEHEN</span><h2>Die Ideen hinter der Rechnung</h2></div>{why}{graph(u["id"])}<div class="concept-grid">{concepts}</div></section>'
    example_section=f'<section class="chapter-section" id="beispiele"><div class="section-title"><span class="eyebrow">02 · NACHVOLLZIEHEN</span><h2>Beispiele, Schritt für Schritt</h2><p>Lies jeden Schritt und frage dich, welche Regel ihn erlaubt.</p></div><div class="example-list">{examples}</div></section>'
    tasks=''
    for level in counts:
        entries=''.join(exercise(t,i) for i,t in enumerate(u['tasks'],1) if t['level'].split(' · ')[0]==level)
        tasks+=f'<section class="level-group" data-level-group="{level}" aria-label="Aufgaben: {level}"><div class="level-heading"><h3>{level}</h3><p>{descriptions[level]} · {counts[level]} Aufgaben</p></div><div class="task-grid">{entries}</div></section>'
    task_section=f'''<section class="chapter-section" id="aufgaben"><div class="section-title"><span class="eyebrow">03 · SELBST RECHNEN</span><h2>Jetzt bist du dran</h2><p>Einfach: Grundlagen festigen. Mittel: mehrere Schritte verbinden. Schwierig: Wissen übertragen und begründen. Probiere zuerst selbst; ein Denkimpuls hilft dir weiter. LK kennzeichnet zusätzliche Kursinhalte.</p></div><div class="task-tools js-only"><label for="task-level">Schwierigkeit</label><select id="task-level"><option value="alle">Alle Aufgaben</option><option value="Einfach">Einfach</option><option value="Mittel">Mittel</option><option value="Schwierig">Schwierig</option></select><button type="button" data-random-task>Zufallsaufgabe</button><button type="button" data-solutions aria-pressed="false">Lösungen aufklappen</button><button type="button" data-print>Kapitel drucken</button></div><p id="random-task-status" class="random-task-status" role="status"></p><output id="task-count" class="task-count" aria-live="polite">{len(u['tasks'])} Aufgaben</output><p class="print-note">Zum Drucken: Geöffnete Lösungen werden mitgedruckt. Über die Aufgabenkennung kannst du eine einzelne Aufgabe verlinken.</p><div class="exercise-levels">{tasks}</div></section>'''
    i=UNITS.index(u);next_unit=UNITS[(i+1)%len(UNITS)]
    next_html=f'<nav class="continue" aria-label="Weiterlernen"><span>Weiterlernen</span><a href="{link(next_unit,root)}">{E(next_unit["name"])} →</a><a href="../{STAGE_MAP[stage][1]}/index.html">Zur Übersicht {stage}</a></nav>'
    return f'<div class="chapter-layout"><div class="chapter-content">{intro}{picker}{explanation}{example_section}{task_section}{next_html}</div></div>'

def main():
    count=validate();total_examples=sum(len(u['examples']) for u in UNITS)
    BASE.mkdir(exist_ok=True)
    shutil.copytree(ROOT/'assets',BASE/'assets',dirs_exist_ok=True)
    search_entries=[dict(title=u['name'],stage=u['stage'],course=u['course'],path=u['slug']+'/index.html',keywords=' '.join([u['id'],u['lead']]+[c['title'] for c in u['concepts']])) for u in UNITS]
    search_entries += [dict(title=f'{stage} Zusammenfassung & Formelsammlung',stage=stage,type='Recap',path=f'formelsammlung/index.html?stufe={stage}',keywords=f'{stage} Formeln Zusammenfassung Recap Wiederholung '+title) for stage,_,title,_ in STAGES if stage in ('Q1','Q2','Q3','Q4')]
    (BASE/'assets/search-index.js').write_text('window.MATHEPFAD_SEARCH='+json.dumps(search_entries,ensure_ascii=False)+';\n',encoding='utf-8')
    home=f'''<header class="intro"><span class="eyebrow">DEIN LERNWEG · MATHEMATIK IN HESSEN</span><h1>Ein Thema verstehen.<br>Dann selbst lösen.</h1><p>Von Klasse 10 bis Q4: verständliche Erklärungen, vorgerechnete Beispiele und Aufgaben mit aufklappbaren Lösungen. Wähle deine Lernstufe.</p><div class="welcome-meta"><span>{len(UNITS)} Kapitel</span><span>{total_examples} Rechenbeispiele</span><span>{count} Aufgaben mit Lösung</span><span>Gymnasium & Realschule</span></div></header><nav class="learning-path" aria-label="Lernstufe auswählen">'''
    home+=''.join(f'<a class="{"path-abi" if stage=="Abiturtraining" else ""}" href="{slug}/index.html">{stage}<span>→</span></a>' for stage,slug,_,_ in STAGES)
    home+='</nav><a class="exam-entry" href="probeklausur/index.html"><span><strong>Deine Themen. Deine Probeklausur.</strong><br>Kapitel auswählen · Aufgaben mischen · mit Lösungsblatt drucken</span><b aria-hidden="true">→</b></a>'+recap_entry()+search_box()
    for i,(stage,*_) in enumerate(STAGES,1):home+=stage_section(stage,'',i)
    home+='<section class="sources"><h2>Mit dem hessischen Lehrplan lernen</h2><p>Die Oberstufe orientiert sich am KCGO Mathematik, Ausgabe 2024, für das Abitur ab 2027. Grundkurs, Leistungskurs und Wahlthemen sind gekennzeichnet. Unterrichtsfolge und jahrgangsbezogene Prüfungsschwerpunkte bitte mit deiner Schule abgleichen.</p><a href="lehrplan/index.html">Einordnung und offizielle Quellen →</a></section>'
    write('','Übersicht',f'Mathematik in Hessen: Klasse 10, E-Phase, Q1 bis Q4 und Realschule. Erklärungen, Beispiele und {count} Aufgaben.',home)
    for i,(stage,slug,title,desc) in enumerate(STAGES,1):
        units=[u for u in UNITS if u['stage']==stage]
        note='Der Realschulbereich reicht bis zum mittleren Abschluss. Die E- und Q-Phasen gehören zur gymnasialen Oberstufe.' if stage=='Realschule' else 'GK + LK: gemeinsame Grundlagen. LK: zusätzliche Anforderungen. Wahlthema: im Curriculum aufgeführte Ergänzung; nicht automatisch verbindlicher Prüfungsstoff.'
        body=f'<header class="intro"><span class="eyebrow">{stage.upper()} · HESSEN</span><h1>{title}</h1><p>{desc}</p><div class="welcome-meta"><span>{len(units)} Kapitel</span><span>{sum(len(u["tasks"]) for u in units)} Aufgaben</span></div></header><div class="stage-callout"><p>{note}</p></div>'+search_box()+stage_section(stage,'../',i,False)
        if stage in ('Q1','Q2','Q3','Q4'):body=body.replace('<div class="stage-callout">',recap_entry(stage)+'<div class="stage-callout">',1)
        write(slug,stage+' · '+title,desc,body,stage)
    write('formelsammlung','Formelsammlung & Zusammenfassungen','Eigene Zusammenfassung für Q1 bis Q4: Kapitel auswählen, Formeln verstehen und Lernzettel drucken.',recap_page(UNITS),'Formelsammlung')
    write('probeklausur','Probeklausur zusammenstellen','Eigene Probeklausur aus ausgewählten Kapiteln mit separaten Lösungen.',(ROOT/'templates/probeklausur.html').read_text(), 'Probeklausur')
    bank=[dict(id=u['id'],name=u['name'],stage=u['stage'],course=u['course'],tasks=[dict(id=t['id'],title=t['title'],level=t['level'],question=M(t['question']),answer=steps(t)) for t in u['tasks']]) for u in UNITS]
    (BASE/'assets/exam-bank.js').write_text('window.JR_EXAM_BANK='+json.dumps(bank,ensure_ascii=False)+';',encoding='utf-8')
    for u in UNITS:write(u['slug'],u['name'],u['lead'],chapter(u),u['stage'])
    for slug,title in [('lehrplan','Lehrplan & Quellen'),('weiterentwickeln','Code, VS Code & Hosting')]:
        body=(ROOT/'templates'/f'{slug}.html').read_text(encoding='utf-8')
        write(slug,title,title+' für JR Maths',f'<article class="article-page">{body}</article>','info')
    (BASE/'.nojekyll').write_text('')
    (BASE/'404.html').write_text('<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Seite nicht gefunden</title><body style="font:18px/1.6 system-ui;padding:30px"><h1>Dieses Kapitel wurde nicht gefunden.</h1><p>Nutze die Zurück-Schaltfläche deines Browsers und wähle das Kapitel erneut aus der Übersicht.</p></body></html>',encoding='utf-8')
    print(f'{len(UNITS)} Kapitel, {total_examples} Beispiele, {count} Aufgaben erzeugt.')

if __name__=='__main__':main()
