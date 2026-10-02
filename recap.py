"""Kuratierte Zusammenfassungen und auswählbare Formelsammlung für Q1–Q4."""
import json
from pathlib import Path
from html import escape as E
from mathtext import M, F
DATA=json.loads((Path(__file__).parent/'recap_data.json').read_text())
STAGE_IDEAS={
 'Q1':('Von Raten zu Beständen','Höhe im Rate-Zeit-Graphen → momentane Rate. Vorzeichenbehaftete Fläche → gesamte Änderung. Anfangsbestand plus Änderung → Endbestand.','Geht es um eine Bilanz, eine geometrische Fläche oder einen vorhandenen Bestand? Prüfe Grenzen, Vorzeichen und Einheiten.'),
 'Q2':('Funktionen umkehren und den Raum beschreiben','Eingabe und Ausgabe unterscheiden. Punkte beschreiben Orte, Vektoren Verschiebungen. Gleichungen übersetzen räumliche Bedingungen in überprüfbare Rechnungen.','Eine Skizze und den Definitionsbereich beziehungsweise Parameterbereich festlegen. Prüfe alle Koordinaten, nicht nur die Projektion.'),
 'Q3':('Zufall modellieren und Entscheidungen einordnen','Vergleichsgruppe und Zufallsgröße bestimmen, dann ein passendes Modell wählen. Wahrscheinlichkeiten berechnen und die Aussage wieder in Alltagssprache übersetzen.','Unabhängigkeit, konstante Trefferchance und Stichprobenerhebung prüfen. Eine statistische Entscheidung ist kein logischer Beweis einer Hypothese.'),
 'Q4':('Wissen vernetzen und begründen','Parameter wählen eine Funktion; x wählt einen Punkt. Aussagen brauchen passende Voraussetzungen, Sonderfälle und nachvollziehbare Argumente.','Vor dem Teilen durch einen Parameter mögliche Nullfälle prüfen. Ein Gegenbeispiel widerlegt eine allgemeine Aussage; ein passendes Beispiel beweist sie nicht.')
}
def recap_entry(stage=None):
    target='formelsammlung/index.html'+(f'?stufe={stage}' if stage else '')
    root='../' if stage else ''
    return f'<section class="recap-entry"><div><h2>{E(stage)+" kompakt" if stage else "Deine Formelsammlung"}</h2><p>Die wichtigsten Ideen und Formeln. Wähle deine Kapitel und stelle deinen eigenen Lernzettel zusammen.</p></div><a href="{root}{target}">{"Zum "+E(stage)+"-Recap" if stage else "Q1–Q4 zusammenfassen"} →</a></section>'

def page(units):
    selected=[u for u in units if u['id'] in DATA]
    header='<header class="intro recap-intro"><span class="eyebrow">Q1–Q4 · WIEDERHOLEN & VERKNÜPFEN</span><h1>Dein Stoff. Dein Lernzettel.</h1><p>Wähle eine Lernstufe oder stelle Kapitel frei zusammen. Die Sammlung zeigt die wichtigsten Formeln, ihre Bedeutung und die Bedingungen, unter denen sie gelten.</p></header>'
    presets='<div class="recap-presets js-only" role="group" aria-label="Lernstufe als Vorauswahl">'+''.join(f'<button type="button" data-recap-preset="{s}" aria-pressed="{str(s=="Q1").lower()}">{s} kompakt</button>' for s in STAGE_IDEAS)+'<button type="button" id="recap-practice" aria-pressed="false">Formeln üben</button></div>'
    groups=''
    for stage in STAGE_IDEAS:
        choices=''.join(f'<label class="recap-choice"><input type="checkbox" data-recap-choice value="{E(u["id"])}" data-stage="{stage}" {"checked" if stage=="Q1" else ""}><span><strong>{E(u["id"])} · {E(u["name"])}</strong><small>{E(u["course"])}</small></span></label>' for u in selected if u['stage']==stage)
        groups+=f'<fieldset><legend>{stage}</legend>{choices}</fieldset>'
    chooser=f'<aside class="recap-chooser js-only"><h2>Kapitel auswählen</h2><p>Wähle eine ganze Stufe oder kombiniere einzelne Kapitel.</p><div class="selection-actions"><button type="button" data-recap-all>Alle</button><button type="button" data-recap-none>Keine</button></div><div class="recap-checkboxes">{groups}</div><label class="context-switch"><input type="checkbox" id="recap-explanations" checked> Kurz-Erklärungen & Beispiele</label><p class="selection-note">Die Bedingungen bleiben immer sichtbar, damit die Formeln richtig eingesetzt werden.</p></aside>'
    overview=''
    for stage,(title,idea,check) in STAGE_IDEAS.items():
        overview+=f'<section class="recap-overview" data-recap-stage="{stage}"><span class="eyebrow">{stage} · DER ROTE FADEN</span><h3>{title}</h3><p>{E(idea)}</p><p class="recap-note"><strong>Vor dem Rechnen:</strong> {E(check)}</p></section>'
    cards=''
    for u in selected:
        formulas=''.join(f'<article class="formula-card"><div class="formula-name"><h4>{E(f["name"])}</h4>{"<span class=tag>LK</span>" if f["course"]=="LK" else ""}</div><div class="math-line">{F(f["formula"])}</div><p class="recap-note">{M(f["meaning"])}</p><p class="formula-condition"><strong>Gilt unter diesen Bedingungen:</strong> {M(f["condition"])}</p></article>' for f in DATA[u['id']])
        cards+=f'<section class="recap-chapter" data-recap-id="{E(u["id"])}" data-stage="{E(u["stage"])}"><div class="recap-chapter-title"><div><span class="tag">{E(u["course"])}</span><h3>{E(u["id"])} · {E(u["name"])}</h3></div><a href="../{u["slug"]}/index.html">Kapitel nachlesen →</a></div>{formulas}</section>'
    sheet=f'<section class="recap-sheet" aria-label="Deine zusammengestellte Formelsammlung"><div class="recap-sheet-heading"><div><span class="eyebrow">DEINE AUSWAHL</span><h2 id="recap-title">Formelsammlung Q1–Q4</h2><output id="recap-count" aria-live="polite">{len(selected)} Kapitel · {sum(len(DATA[u["id"]]) for u in selected)} Formel- und Merkkarten</output></div><button type="button" class="js-only" id="recap-print">PDF erstellen</button></div><div id="pdf-result" class="pdf-result" hidden><a id="pdf-open" target="_blank" rel="noopener" download>PDF öffnen / speichern</a><button type="button" id="pdf-share" hidden>Teilen / In Dateien sichern</button></div><p id="pdf-status" class="pdf-status" role="status" aria-live="polite"></p><p class="recap-empty" id="recap-empty" hidden>Wähle mindestens ein Kapitel. Deine Zusammenfassung erscheint hier.</p><p class="recap-scope" id="recap-scope">Kompakter Lernüberblick zu den Kapiteln dieser Plattform. LK und Wahlthemen sind gekennzeichnet; die Auswahl ersetzt keine jahrgangsbezogenen Prüfungsanforderungen.</p>{overview}{cards}</section>'
    return header+presets+'<noscript><p>Ohne JavaScript werden alle Kapitel angezeigt. Die interaktive Auswahl benötigt JavaScript.</p></noscript><div class="recap-layout">'+chooser+sheet+'</div>'
