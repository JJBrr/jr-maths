# JR Maths

Modulare, statische Lernplattform für die Nachhilfe: Gymnasium G9 Klasse 10, E1/E2, Q1–Q4, Abiturtraining und Realschule Klasse 10 / mittlerer Abschluss.

**Stand: 26.09.2026 · 40 Kapitel · 120 Rechenbeispiele · 434 Aufgaben mit Lösungen.**

Die Oberstufe orientiert sich am hessischen KCGO Mathematik, Ausgabe 2024 (Grundlage ab Abitur 2027). GK, LK und Wahlthemen sind gekennzeichnet. Die konkreten Abiturschwerpunkte des jeweiligen Jahrgangs müssen zusätzlich mit dem Erlass und dem Unterricht abgeglichen werden. Alle Themenfelder der KCGO-Übersicht sind vertreten; das Angebot ist ein ausbaufähiger Lern- und Übungsbestand, kein Ersatz für jede schulische Vertiefung. Aufgaben sind eigens erstellt, keine Originalprüfungen.

## Schnellstart in Visual Studio Code

1. Das ZIP vollständig entpacken.
2. In **Visual Studio Code → Datei → Ordner öffnen** den Ordner `mathepfad` öffnen. Die große Visual-Studio-IDE wird nicht benötigt.
3. `dist/index.html` kann direkt im Browser geöffnet werden. Alle Lerntexte, Navigation und Lösungen funktionieren auch ohne Server.
4. Für Inhaltsänderungen Python 3 installieren. Es werden **keine zusätzlichen Python-Pakete**, kein npm und keine Datenbank benötigt.
5. Im integrierten Terminal ausführen:

```powershell
# Windows
py build.py
py export.py
py check.py
py -m http.server 8000 --directory dist
```

```bash
# macOS / Linux
python3 build.py
python3 export.py
python3 check.py
python3 -m http.server 8000 --directory dist
```

Dann `http://localhost:8000` öffnen. Server mit Strg+C beenden. Nach Änderungen erneut bauen und Browser aktualisieren. Vorgefertigte VS-Code-Aufgaben stehen unter **Terminal → Aufgabe ausführen** bereit. Die Windows-Bauaufgabe verwendet PowerShell.

## Ordner und Verantwortlichkeiten

| Pfad | Inhalt / Bearbeitung |
|---|---|
| `content/10.1.json` … `10.5.json` | Klasse 10, bestehende Kapitel und stabile Aufgabenkennungen |
| `content/E.*.json` | Einführungsphase |
| `content/Q1.*.json` … `Q4.*.json` | Qualifikationsphase, inklusive Wahlthemen |
| `content/Q2.3.1.json` | zusätzliche Vertiefung zu Gauß, Ebenenformen und Abständen |
| `content/ABI.*.json` | mehrteilige Aufgaben auf Abiturniveau |
| `content/R.*.json` | Realschule / mittlerer Abschluss |
| `assets/style.css` | gemeinsame Gestaltung, Breakpoints und Druckansicht |
| `assets/app.js` | Aufgabenfilter und Sammelsteuerung der Lösungen |
| `assets/navigation.js` | Globale Suche mit anklickbaren Vorschlägen und mobile Navigation |
| `recap.py` / `recap_data.json` / `assets/recap.js` | Kuratierte Zusammenfassungen und eigene Kapitelauswahl für Q1–Q4 |
| `assets/favicon.svg` | kleines Markenzeichen |
| `templates/base.html` | HTML-Rahmen aller Seiten |
| `templates/lehrplan.html` | Einordnung und offizielle Quellen |
| `templates/weiterentwickeln.html` | Hosting- und Bearbeitungshilfe direkt auf der Site |
| `mathtext.py` | Setzt Brüche, Wurzeln und Exponenten als natives MathML ohne externe Dienste |
| `graph_lab.py` / `assets/graph-lab.js` | 11 Graphenmodelle in 22 Kapiteln mit Ablesepunkt und Deutung |
| `build.py` | Kapitel lesen, validieren und HTML-Seiten erzeugen |
| `export.py` | sauberes Downloadpaket ohne Sites-Projektkennung erstellen |
| `check.py` | HTML-Seiten, interne Links, Anker und Aufgabenanzahl prüfen |
| `docs/kapitel-vorlage.json` | Kopiervorlage für ein neues Kapitel, noch mit Beispielplatzhaltern |
| `.vscode/tasks.json` | lokale Bau- und Vorschauaufgaben |
| `.github/workflows/pages.yml` | Veröffentlichung über GitHub Actions / Pages |
| `dist/` | vollständige fertige Website; diesen Ordner hosten |

**Quellen zuerst ändern, danach bauen.** Änderungen an erzeugten Dateien in `dist/` werden beim nächsten Bauen überschrieben. Die zentrale Gestaltung liegt in `assets/style.css`, nicht in `dist/assets/style.css`.

## Inhalte erweitern

Jede Kapiteldatei ist ein unabhängiges JSON-Objekt. `build.py` erkennt alle Dateien direkt unter `content/` automatisch. Keine manuelle Registrierung neuer Kapitel innerhalb einer bestehenden Lernstufe nötig.

Beispiel für eine zusätzliche Aufgabe in `content/Q1.1.json`:

```json
{
  "id": "Q1.1-09",
  "level": "Mittel",
  "title": "Integral berechnen",
  "question": "Berechne das Integral von 0 bis 2 über 3x².",
  "steps": [
    "Eine Stammfunktion ist F(x)=x³.",
    "F(2)−F(0)=8−0=8."
  ]
}
```

Die Aufgabe gehört in das Array `tasks`. Zwischen JSON-Objekten steht ein Komma; nach dem letzten Objekt keines. Vorhandene Kennungen nicht wiederverwenden. Der Builder prüft doppelte Kennungen. Ältere Aufgaben dürfen das Feld `solution` mit einer zusammenhängenden Lösung behalten; neue Aufgaben verwenden vorzugsweise `steps`.

Ein neues Kapitel entsteht durch Kopieren von `docs/kapitel-vorlage.json` nach `content/`, dann:

1. Neue eindeutige `id` und `slug` setzen. Ein Slug enthält kleine ASCII-Buchstaben, Ziffern und Bindestriche.
2. `stage` wählen: `Klasse 10`, `E-Phase`, `Q1`, `Q2`, `Q3`, `Q4`, `Abiturtraining` oder `Realschule`.
3. Name, Einführung (`lead`), Voraussetzungen und Lehrplanbezug eintragen.
4. Mindestens drei Erklärbausteine, drei vollständig gerechnete Beispiele und sechs echte Aufgaben ausarbeiten. Die Vorlage enthält dafür Platzhalter, die vollständig ersetzt werden müssen.
5. Jede Aufgaben-ID eindeutig setzen. Schwierigkeitsstufen: `Einfach`, `Mittel`, `Schwierig`; bei Bedarf z. B. `Schwierig · LK`.
6. Bauen, prüfen und das neue Kapitel lesen. Ein neuer Stufenname erfordert eine Ergänzung der Liste `STAGES` in `build.py`.

Die Textfelder werden als Text ausgegeben und HTML-escaped. HTML-Tags oder Markdown gehören nicht in die JSON-Texte. Mathematische Schreibweise: `x²`, `f′(x)`, `e^(2x)`, `∫₀²`. Das hält die Website ohne externe Formeldienste und Schrift-CDNs nutzbar. Bei späterer Einführung von KaTeX sollte ein eigenes Formel-Feld ergänzt werden.

**Links stabil halten:** Bestehende Slugs und Aufgaben-IDs beibehalten. Ein Link kann z. B. auf `integrale-verstehen/index.html#Q1.1-03` zeigen. Werden Aufgaben nur umsortiert, bleibt diese Kennung erhalten.

## GitHub Pages: dauerhaft für Schüler veröffentlichen

Der enthaltene Workflow baut und prüft die Site bei einem Push auf `main`. Danach veröffentlicht er ausschließlich `dist/`. Die relativen Links funktionieren auch auf einer Projektadresse unter einem Unterpfad.

1. In deinem GitHub-Konto ein neues Repository anlegen, z. B. `mathepfad`. Für GitHub Free eignet sich ein öffentliches Repository.
2. Den **Inhalt des entpackten Projektordners** hineinladen, sodass `build.py` direkt an der Repository-Wurzel liegt. Nicht eine zusätzliche äußere ZIP-Ordnerstufe hochladen.
3. In **Settings → Pages → Build and deployment → Source** `GitHub Actions` auswählen.
4. Auf `main` pushen. Im Tab **Actions** den Lauf „Mathepfad auf GitHub Pages“ verfolgen. Alternativ den Workflow über **Run workflow** starten.
5. Die erfolgreiche Veröffentlichung zeigt die tatsächliche URL, üblicherweise `https://DEIN-NAME.github.io/mathepfad/`. Erst diese erfolgreiche URL an die Schüler weitergeben.

```bash
git init -b main
git add .
git commit -m "Mathepfad starten"
git remote add origin DEINE_GITHUB_REPOSITORY_URL
git push -u origin main
```

Den Platzhalter ersetzen. Anmeldung über Git/VS Code erledigen. Dieser Befehlssatz gilt für einen neu entpackten Ordner ohne vorhandenes Git-Repository. Es wurde hier noch kein Repository in deinem GitHub-Konto angelegt und keine GitHub-URL veröffentlicht.

Bei späteren Änderungen:

```bash
git add .
git commit -m "Neue Aufgaben ergänzen"
git push
```

Die GitHub-Action baut mit Python erneut, erzeugt das Downloadpaket und prüft alle relativen Verweise. Unter **Settings → Environments → github-pages** können vorhandene Repository-Regeln den Deploymentlauf beeinflussen.

Offizielle Anleitung: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

## Andere Hosting-Anbieter / eigener Webserver

Den Inhalt von `dist/` auf einen statischen Webhost hochladen. `index.html`, `assets/`, `downloads/` und die Kapitelordner müssen ihre relative Struktur behalten. Der Webserver braucht kein Python, Node.js oder Datenbank-Backend. HTTPS und eigene Domain werden beim Anbieter eingestellt.

Für einen lokalen WLAN-Test kann ein eingeschalteter PC `python -m http.server` bereitstellen. Am Handy öffnest du die lokale IP des PCs und Port 8000. Beide Geräte müssen im selben Netz sein; die Firewall muss den Zugriff erlauben. Das ist eine Vorschau, kein dauerhaftes Internet-Hosting. Keine Router-Portfreigabe nötig für den WLAN-Test.

## Bedienung und Geräte

- Responsive Ansichten für schmale Handys, Tablets und Desktop.
- Lerntexte und HTML-`details`-Lösungen funktionieren ohne JavaScript.
- JavaScript verbessert Suche, Filter und Sammelsteuerung; keine Anmeldung, Cookies oder Fortschrittsspeicherung im Anwendungscode.
- Direkte Aufgabenlinks verwenden die dauerhaften IDs.
- Druckansicht übernimmt geöffnete Lösungen. Für ein Arbeitsblatt Lösungen zuklappen; für ein Lösungsblatt öffnen.
- Die Suche durchsucht Kapitelüberschriften, Einführungen, Lehrplanbezüge und Begriffsüberschriften. Es ist keine Volltextsuche in allen Lösungswegen.

## Qualität und Ausbau

`check.py` prüft alle erzeugten Seiten, lokalen Links und Anker. `node --check assets/app.js` kann bei installiertem Node die JS-Syntax prüfen. Mathematik muss beim Ergänzen inhaltlich kontrolliert werden; der Strukturcheck ersetzt keinen fachlichen Review.

Die neue Fassung wurde mit Struktur- und Linkchecks sowie einer Auswahl unabhängiger mathematischer Kontrollrechnungen geprüft. Eine visuelle Geräteprüfung in einem Browser war in dieser Arbeitsumgebung für das bestehende statische Projekt nicht verfügbar. Vor der Nutzung im Unterricht empfiehlt sich daher ein kurzer Test auf den eigenen Geräten, besonders Druckansicht und lange Formeln.

Spätere Fortschrittsspeicherung kann auf `user_id`, `exercise_id`, `status`, `updated_at` aufbauen. Kapitel und Aufgaben müssen dafür nicht aus den Inhaltsdateien entfernt werden. Bis dahin ist die Plattform als schneller Nachschlage- und Übungsort ohne Konten nutzbar.

## Quellen

- KCGO Mathematik 2024: https://kultus.hessen.de/sites/kultus.hessen.de/files/2024-11/kerncurriculum_gymnasiale_oberstufe-mathematik.pdf
- Einführung / Geltung ab 2027: https://kultus.hessen.de/unterricht/kerncurricula-und-lehrplaene/kerncurricula/kerncurricula-fuer-die-gymnasiale-oberstufe-kcgo
- Gymnasium Sek I: https://kultus.hessen.de/sites/kultus.hessen.de/files/2021-07/kerncurriculum_mathematik_gymnasium.pdf
- G9-Lehrplan: https://kultus.hessen.de/sites/kultus.hessen.de/files/2021-06/g9-mathematik.pdf
- Realschule: https://kultus.hessen.de/sites/kultus.hessen.de/files/2021-07/kerncurriculum_mathematik_realschule.pdf
- Ergänzender Realschul-Lehrplan: https://kultus.hessen.de/sites/kultus.hessen.de/files/2021-06/lprealmathe.pdf

Das Export-ZIP enthält keine Sites-Projektkennung und keine Git-Zugangsdaten. Die bestehende Sites-Veröffentlichung hat weiterhin ihre bisherigen Zugriffsrechte; eine eigene GitHub-Pages-Veröffentlichung ist ein separater öffentlicher Zugang.

## Verstehen und Darstellen

Jedes Kapitel enthält `understanding` mit `why`, `idea`, `check` und `answer`. Neue Aufgaben können einen optionalen `hint` als getrennt aufklappbaren Denkimpuls enthalten. Die drei Niveaus sind `Einfach`, `Mittel`, `Schwierig`; ` · LK` bleibt als Zusatz möglich.

Formeln bleiben in JSON lesbare Textfelder. Der Build setzt beispielsweise `27^(2/3)`, `1/(x−2)` und `(f(b)−f(a))/(b−a)` als strukturierte Brüche und Potenzen. Mehrgliedrige Zähler und Nenner immer eindeutig einklammern. Dezimalzahlen verwenden ein Komma; bei Aufzählungen nach dem Komma ein Leerzeichen schreiben. Neue Schreibweisen vor Veröffentlichung kontrollieren; der Renderer ist kein allgemeines Computeralgebrasystem. MathML wird direkt mitgeliefert und benötigt keine externen Schriften oder CDN-Verbindung.

Die Niveauauswahl verwendet `?niveau=Einfach` (oder `Mittel`, `Schwierig`) und lässt sich direkt verlinken. Sie speichert keine personenbezogenen Daten. Ohne JavaScript bleiben alle Aufgaben und aufklappbaren Lösungen zugänglich. Die Graphen liefern zusätzlich eine statische Ausgangsdarstellung.

## Suche und Formelsammlung

Die Seitennavigation enthält Lernstufen und die Kapitel der gerade geöffneten Stufe. Auf kleinen Geräten wird sie über „Menü“ geöffnet. Die Suche ist auf jeder Seite verfügbar. `build.py` erstellt `dist/assets/search-index.js` automatisch aus den Kapitelüberschriften, Einleitungen und Themenüberschriften. Teilwörter, Groß-/Kleinschreibung, Umlaute und mehrere Suchwörter werden unterstützt. Pfeiltasten und Enter wählen einen Treffer aus, Escape schließt die Vorschläge. Es gibt keine externen Suchanfragen.

`formelsammlung/index.html?stufe=Q1` öffnet den Q1-Recap. Für Q2–Q4 den Parameter entsprechend ändern. Über Checkboxen lassen sich die 19 Q-Kapitel frei kombinieren. Die Auswahl wird in der URL abgebildet, z. B. `?kapitel=Q1.1,Q1.2`; `&kurz=1` blendet Kurz-Erklärungen aus. Bedingungen bleiben sichtbar. Die Druckansicht berücksichtigt nur die gewählten Kapitel. „PDF erstellen“ bereitet eine echte PDF-Datei vor. Danach „PDF öffnen / speichern“ antippen. Eigene Kombinationen werden mit dem lokal mitgelieferten pdf-lib im Browser zusammengeführt.

Die 57 Formel- und Merkkarten werden in `recap_data.json` gepflegt, mit den Feldern `name`, `formula`, `meaning`, `condition` und optionalem LK-Hinweis `course`. Schlüssel sind bestehende Kapitel-IDs. Dieses kuratierte Kurzformat ergänzt die ausführlichen Kapitel; neue Kapitel erscheinen automatisch in der Suche, aber erst nach einer fachlichen Zusammenfassung in der Formelsammlung.

## Echte PDF-Dateien und Formelsatz

Die Website liefert unter `assets/pdfs/` vollständige PDF-Dateien für jedes Q-Kapitel und jede Q-Stufe aus, jeweils mit Erklärungen und kompakt. Keine Abhängigkeit vom Druckdialog einer eingebetteten Browseransicht. Nach Änderungen an der Formelsammlung die PDFs mit `python pdf_exports.py` neu erstellen; dafür werden `reportlab` und `pypdf` benötigt (`python -m pip install reportlab pypdf`). Anschließend wie gewohnt `build.py`, `export.py`, `check.py` ausführen. Die vorbereiteten PDFs und lokalen Schriftdateien sind im Quellcodepaket enthalten, sodass normales Bauen keine zusätzlichen Pakete benötigt.

`mathtext.F` setzt ganze Formelzeilen auf einer gemeinsamen mathematischen Grundlinie. Integralgrenzen werden strukturiert als Unter- und Obergrenze gerendert. Der PDF-Generator verwendet denselben Ausdrucksbaum und zeichnet die Formeln als Vektoren.

Die Zufallsaufgabe berücksichtigt das gewählte Niveau und deckt die Lösung nicht auf. „Formeln üben“ in der Formelsammlung verdeckt zunächst die Formeln; jede Karte lässt sich einzeln aufdecken. Der PDF-Export enthält stets die Formeln, unabhängig vom Abfragemodus.
