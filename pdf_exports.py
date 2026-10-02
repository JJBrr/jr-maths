"""Build actual PDF assets, using vector formulas and locally bundled fonts.
Regenerate after changing recap_data.json: python pdf_exports.py
Requires reportlab and pypdf. The website itself needs no server or Python.
"""
from pathlib import Path
from dataclasses import dataclass
from html import escape
import json, re, xml.etree.ElementTree as ET
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from pypdf import PdfReader,PdfWriter
from mathtext import parse
ROOT=Path(__file__).parent
OUT=ROOT/'assets/pdfs';OUT.mkdir(parents=True,exist_ok=True)
for name,file in [('Body','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Math','DejaVuSerif.ttf')]:pdfmetrics.registerFont(TTFont(name,str(ROOT/'assets/fonts'/file)))
INK=HexColor('#182b53');BLUE=HexColor('#335bcc');MUTED=HexColor('#52627b');LINE=HexColor('#dbe3f1');BG=HexColor('#eff4fc')
W,H=595.276,841.89;LEFT=46;WIDTH=W-2*LEFT
STYLE=ParagraphStyle('body',fontName='Body',fontSize=10,leading=15,textColor=INK,spaceAfter=0)
SMALL=ParagraphStyle('small',parent=STYLE,fontSize=9,leading=13,textColor=MUTED)
HEAD=ParagraphStyle('heading',parent=STYLE,fontName='Bold',fontSize=18,leading=23)
SUBHEAD=ParagraphStyle('subheading',parent=STYLE,fontName='Bold',fontSize=12,leading=17)
@dataclass
class Box:
    w:float
    up:float
    down:float
    draw:object

def glyph(text,s=13,font='Math'):
    if not text:return Box(0,0,0,lambda c,x,y:None)
    text=text.replace('\u2011','-')
    w=pdfmetrics.stringWidth(text,font,s)
    def draw(c,x,y):c.setFont(font,s);c.drawString(x,y,text)
    return Box(w,.82*s,.23*s,draw)
def row(boxes,gap=0):
    if not boxes:return glyph('')
    def draw(c,x,y):
        for b in boxes:b.draw(c,x,y);x+=b.w+gap
    return Box(sum(b.w for b in boxes)+gap*max(0,len(boxes)-1),max(b.up for b in boxes),max(b.down for b in boxes),draw)
def box(node,s=13):
    tag=node.tag
    if tag=='mspace':return Box(float(node.get('width','0.3em').removesuffix('em'))*s,0,0,lambda c,x,y:None)
    if tag in ('root','mrow'):return row([box(n,s) for n in node])
    if tag in ('mn','mi','mo','mtext'):
        txt=''.join(node.itertext())
        return glyph(txt,s*1.65 if txt=='∫' else s,'Body' if tag=='mtext' else 'Math')
    if tag=='mfrac':
        a,b=[box(n,s*.88) for n in node];w=max(a.w,b.w)+s*.45;axis=s*.23;gap=s*.19
        ay=axis+gap+a.down;by=axis-gap-b.up
        def draw(c,x,y):
            a.draw(c,x+(w-a.w)/2,y+ay);b.draw(c,x+(w-b.w)/2,y+by)
            c.setLineWidth(.65);c.line(x+s*.08,y+axis,x+w-s*.08,y+axis)
        return Box(w,ay+a.up,-by+b.down,draw)
    if tag in ('msup','msub','msubsup'):
        base=box(node[0],s);sub=box(node[1],s*.67) if tag!='msup' else None;sup=box(node[2] if tag=='msubsup' else node[1],s*.67) if tag!='msub' else None
        sy=max(base.up-s*.15,s*.65)+(sup.down if sup else 0);dy=max(s*.25,base.down+s*.04)+(sub.up*.15 if sub else 0)
        w=base.w+max(sub.w if sub else 0,sup.w if sup else 0)+s*.07
        def draw(c,x,y):
            base.draw(c,x,y)
            if sup:sup.draw(c,x+base.w+s*.04,y+sy)
            if sub:sub.draw(c,x+base.w+s*.04,y-dy)
        return Box(w,max(base.up,sy+sup.up if sup else 0),max(base.down,dy+sub.down if sub else 0),draw)
    if tag in ('msqrt','mroot'):
        child=row([box(n,s) for n in node]) if tag=='msqrt' else box(node[0],s)
        root=glyph('√',max(s,child.up+child.down)*1.08);prefix=s*.22 if tag=='mroot' else 0
        degree=box(node[1],s*.5) if tag=='mroot' else None;w=prefix+root.w+child.w+s*.13
        def draw(c,x,y):
            root.draw(c,x+prefix,y);child.draw(c,x+prefix+root.w,y)
            c.setLineWidth(.65);c.line(x+prefix+root.w*.8,y+child.up+s*.06,x+w,y+child.up+s*.06)
            if degree:degree.draw(c,x,y+s*.66)
        return Box(w,max(root.up,child.up+s*.12),max(root.down,child.down),draw)
    return row([box(n,s) for n in node])
def formula(text,size=13):
    node=ET.fromstring('<root>'+''.join(n.xml for n in parse(text))+'</root>')
    return box(node,size)
def para(text,style=STYLE,width=WIDTH):
    p=Paragraph(escape(text).replace('\n','<br/>'),style);_,h=p.wrap(width,1000);return p,h

def export_chapter(u,items,compact):
    suffix='compact' if compact else 'full';path=OUT/f'{u["id"]}-{suffix}.pdf';c=Canvas(str(path),pagesize=(W,H),pageCompression=1)
    c.setTitle(f'JR Maths - {u["id"]} {u["name"]}');c.setAuthor('JR Maths');page=0;y=0
    def start():
        nonlocal page,y
        page+=1;c.setFillColor(INK);c.rect(0,H-66,W,66,fill=1,stroke=0)
        c.setFillColor(HexColor('#ffd887'));c.setFont('Bold',19);c.drawString(LEFT,H-42,'JR MATHS')
        c.setFillColor(HexColor('#e3ecff'));c.setFont('Body',9);c.drawRightString(W-LEFT,H-40,f'{u["stage"]} · Formelsammlung')
        c.setFillColor(MUTED);c.setFont('Body',8);c.drawString(LEFT,29,u['id']+' · '+('Kompakt' if compact else 'Mit Erklärungen'));c.drawRightString(W-LEFT,29,f'Seite {page}')
        y=H-95;c.setFillColor(INK)
    def put(text,style=STYLE,gap=9):
        nonlocal y
        p,h=para(text,style);p.drawOn(c,LEFT,y-h);y-=h+gap
    start();put(u['name'],HEAD,9);put(u['id']+' · '+u['course'],SMALL,15)
    if not compact:put(u['understanding']['idea'],STYLE,18)
    for item in items:
        lines=re.split(r'; | ··· ',item['formula']);forms=[formula(t) for t in lines]
        scales=[min(1,(WIDTH-30)/b.w) if b.w else 1 for b in forms]
        heights=[(b.up+b.down)*s+12 for b,s in zip(forms,scales)]
        formulaH=sum(heights)+10
        title=item['name']+(' · LK' if item['course']=='LK' else '')
        hp,hh=para(title,SUBHEAD,WIDTH-28)
        mp,mh=para(item['meaning'],STYLE,WIDTH-28)
        cp,ch=para('Voraussetzung: '+item['condition'],SMALL,WIDTH-28)
        height=14+hh+10+formulaH+10+(mh+9 if not compact else 0)+ch+14
        if y-height<58:c.showPage();start();put(u['name']+' · Fortsetzung',SUBHEAD,15)
        c.setStrokeColor(LINE);c.setFillColor(HexColor('#ffffff'));c.roundRect(LEFT,y-height,WIDTH,height,8,fill=1,stroke=1)
        yy=y-14;hp.drawOn(c,LEFT+14,yy-hh);yy-=hh+10
        c.setFillColor(BG);c.roundRect(LEFT+10,yy-formulaH,WIDTH-20,formulaH,5,fill=1,stroke=0)
        fy=yy-7
        for b,scale,h in zip(forms,scales,heights):
            c.saveState();c.setFillColor(INK);c.setStrokeColor(INK);c.translate(LEFT+17,fy-b.up*scale);c.scale(scale,scale);b.draw(c,0,0);c.restoreState();fy-=h
        yy-=formulaH+10
        if not compact:mp.drawOn(c,LEFT+14,yy-mh);yy-=mh+9
        cp.drawOn(c,LEFT+14,yy-ch);y-=height+13
    c.save();return path

def main():
    data=json.loads((ROOT/'recap_data.json').read_text());units={u['id']:u for u in (json.loads(p.read_text()) for p in (ROOT/'content').glob('*.json'))}
    for uid,items in data.items():
        for compact in (False,True):export_chapter(units[uid],items,compact)
    for stage in ('Q1','Q2','Q3','Q4'):
        for compact in (False,True):
            suffix='compact' if compact else 'full';w=PdfWriter()
            for uid in data:
                if units[uid]['stage']==stage:
                    for page in PdfReader(OUT/f'{uid}-{suffix}.pdf').pages:w.add_page(page)
            w.add_metadata({'/Title':f'JR Maths - {stage} Formelsammlung','/Author':'JR Maths'})
            with (OUT/f'JR-Maths-{stage}-{suffix}.pdf').open('wb') as out:w.write(out)
            # Keep previously shared PDF addresses working with current branding.
            (OUT/f'JJ-Mathe-{stage}-{suffix}.pdf').write_bytes((OUT/f'JR-Maths-{stage}-{suffix}.pdf').read_bytes())
    print(f'{len(list(OUT.glob("*.pdf")))} PDF-Dateien erstellt.')
if __name__=='__main__':main()
