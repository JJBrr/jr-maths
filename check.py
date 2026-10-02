"""Prüft echte Ausgabedateien, relative Links und Aufgabenanker."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json

ROOT=Path(__file__).resolve().parent
BASE=ROOT/'dist'
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.ids=set();self.links=[];self.headings=0;self.tasks=0;self.duplicate=[]
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):
            if a['id'] in self.ids:self.duplicate.append(a['id'])
            self.ids.add(a['id'])
        if tag=='h1':self.headings+=1
        if 'data-exercise-id' in a:self.tasks+=1
        for key in ('href','src'):
            if a.get(key):self.links.append(a[key])

pages={p.resolve():Page(p.read_text(encoding='utf-8')) for p in BASE.rglob('*.html')}
errors=[];links=0
for path,page in pages.items():
    if page.headings!=1:errors.append(f'{path}: {page.headings} H1 statt 1')
    if page.duplicate:errors.append(f'{path}: doppelte IDs {page.duplicate}')
    for href in page.links:
        url=urlsplit(href)
        if url.scheme or url.netloc:continue
        links+=1
        if url.path.startswith('/'):
            errors.append(f'{path}: nicht portable absolute URL {href}');continue
        target=(path.parent/unquote(url.path)).resolve() if url.path else path
        if target.is_dir():target=target/'index.html'
        if not target.exists():errors.append(f'{path}: fehlt {href}');continue
        if url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
            errors.append(f'{path}: fehlender Anker {href}')

units=[json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'content').glob('*.json')]
expected=sum(len(u['tasks']) for u in units)
actual=sum(p.tasks for p in pages.values())
if expected!=actual:errors.append(f'Aufgabenzahl JSON {expected} != HTML {actual}')
for u in units:
    page=pages[(BASE/u['slug']/'index.html').resolve()]
    for t in u['tasks']:
        if t['id'] not in page.ids:errors.append('Fehlende Aufgabe '+t['id'])
if errors:raise SystemExit('\n'.join(errors))
print(f'OK: {len(pages)} HTML-Seiten, {links} interne Verweise, {actual} Aufgabenanker.')
