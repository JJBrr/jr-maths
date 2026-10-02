"""Buchähnliche Formeln aus den bestehenden Textfeldern: native MathML, offline.
Brüche und Potenzen werden strukturell gesetzt; Texte bleiben HTML-Text.
"""
from dataclasses import dataclass
from html import escape
import xml.etree.ElementTree as ET
import re
SUP='⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱᵐᵗˣᵏᵃᵇᶜʳ'
SUB='₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ'
SUPMAP=str.maketrans(SUP,'0123456789+−=()nimtxkabcr')
SUBMAP=str.maketrans(SUB,'0123456789+−=()aehijklmnoprstuvx')
@dataclass
class Node:
    raw:str
    xml:str
    changed:bool=False
    atom:bool=False
    inner:object=None
    def plain(self):
        return self.inner if self.inner is not None else self.xml

def parse(s):
    out=[];i=0
    while i<len(s):
        c=s[i]
        if c=='∫':
            j=i+1;lower='';upper=''
            while j<len(s) and s[j] in SUB:lower+=s[j];j+=1
            while j<len(s) and s[j] in SUP+'ᵉ∞':upper+=s[j];j+=1
            lo=''.join(n.xml for n in parse(lower.translate(SUBMAP)))
            hi=''.join(n.xml for n in parse(upper.translate(SUPMAP).replace('ᵉ','e')))
            op='<mo largeop="true" stretchy="false">∫</mo>'
            if lower and upper:op='<msubsup>'+op+'<mrow>'+lo+'</mrow><mrow>'+hi+'</mrow></msubsup>'
            elif lower:op='<msub>'+op+'<mrow>'+lo+'</mrow></msub>'
            elif upper:op='<msup>'+op+'<mrow>'+hi+'</mrow></msup>'
            out.append(Node(s[i:j],op,True,False));i=j;continue
        if c in '([':
            closing=')' if c=='(' else ']';depth=1;j=i+1
            while j<len(s) and depth:
                if s[j]==c:depth+=1
                elif s[j]==closing:depth-=1
                j+=1
            if not depth:
                children=parse(s[i+1:j-1]);inner=''.join(n.xml for n in children)
                out.append(Node(s[i:j],'<mrow><mo>'+c+'</mo>'+inner+'<mo>'+closing+'</mo></mrow>',any(n.changed for n in children),True,inner));i=j;continue
        if c=='|' and '|' in s[i+1:]:
            j=s.index('|',i+1);inside=s[i+1:j]
            if inside and not any(k in inside for k in '=;:'):
                children=parse(inside);out.append(Node(s[i:j+1],'<mrow><mo>|</mo>'+''.join(n.xml for n in children)+'<mo>|</mo></mrow>',any(n.changed for n in children),True));i=j+1;continue
        if c in SUP+SUB:
            chars=SUP if c in SUP else SUB;j=i+1
            while j<len(s) and s[j] in chars:j+=1
            txt=s[i:j].translate(SUPMAP if c in SUP else SUBMAP)
            if out and out[-1].atom:
                b=out.pop();tag='msup' if c in SUP else 'msub'
                out.append(Node(b.raw+s[i:j],f'<{tag}><mrow>{b.xml}</mrow><mrow>'+''.join(n.xml for n in parse(txt))+f'</mrow></{tag}>',True,True));i=j;continue
        if c.isspace():
            j=i+1
            while j<len(s) and s[j].isspace():j+=1
            out.append(Node(s[i:j],'<mspace width="0.3em"/>'));i=j;continue
        if c.isdigit() and c not in SUP+SUB:
            j=i+1
            while j<len(s) and s[j].isdigit() and s[j] not in SUP+SUB:j+=1
            if j+1<len(s) and s[j] in ',.' and s[j+1].isdigit():
                j+=1
                while j<len(s) and s[j].isdigit() and s[j] not in SUP+SUB:j+=1
            raw=s[i:j];out.append(Node(raw,'<mn>'+escape(raw)+'</mn>',False,True));i=j;continue
        if c.isalpha() and c not in SUP+SUB:
            j=i+1
            while j<len(s) and ((s[j].isalpha() and s[j] not in SUP+SUB) or s[j] in '′″̂̄'):j+=1
            raw=s[i:j]
            if len(raw)<=3 and raw not in ('ln','sin','cos','tan','log','lim','Var') and not any(k in raw for k in '′″̂̄'):
                out.extend(Node(v,'<mi>'+escape(v)+'</mi>',False,True) for v in raw)
            else:
                tag='mi' if len(raw)<=3 or raw in ('arcsin','arccos','arctan') else 'mtext'
                out.append(Node(raw,f'<{tag}>{escape(raw)}</{tag}>',False,True))
            i=j;continue
        out.append(Node(c,'<mo>'+escape(c)+'</mo>'));i+=1
    # An immediately attached argument belongs to a function; an exponent binds to its base.
    j=0
    while j<len(out)-1:
        a,b=out[j:j+2]
        if a.atom and b.atom and b.raw.startswith('(') and (re.fullmatch(r'[A-Za-zΦ][′″]*',a.raw) or a.raw in ('sin','cos','tan','ln','log','lim','arcsin','arccos','arctan','C','Var')):
            out[j:j+2]=[Node(a.raw+b.raw,'<mrow>'+a.xml+b.xml+'</mrow>',a.changed or b.changed,True)];continue
        if a.raw=='^' and j>0 and out[j-1].atom and b.atom:
            base=out[j-1];out[j-1:j+2]=[Node(base.raw+'^'+b.raw,'<msup><mrow>'+base.xml+'</mrow><mrow>'+b.plain()+'</mrow></msup>',True,True)];j=max(0,j-1);continue
        j+=1
    # Roots bind before division, so √3/2 means (√3)/2.
    j=len(out)-2
    while j>=0:
        if out[j].raw in ('√','∛') and out[j+1].atom:
            a,b=out[j:j+2];xml='<msqrt>'+b.plain()+'</msqrt>' if a.raw=='√' else '<mroot><mrow>'+b.plain()+'</mrow><mn>3</mn></mroot>'
            if a.raw=='√' and j>0 and out[j-1].raw in SUP:
                degree=out[j-1];xml='<mroot><mrow>'+b.plain()+'</mrow><mi>'+degree.raw.translate(SUPMAP)+'</mi></mroot>'
                out[j-1:j+2]=[Node(degree.raw+a.raw+b.raw,xml,True,True)];j-=1
            else:out[j:j+2]=[Node(a.raw+b.raw,xml,True,True)]
        j-=1
    # Factorials and angle units belong to the preceding operand.
    j=1
    while j<len(out):
        if out[j].raw in ('!','°') and out[j-1].atom:
            a,b=out[j-1:j+1];out[j-1:j+1]=[Node(a.raw+b.raw,'<mrow>'+a.xml+b.xml+'</mrow>',a.changed,True)];continue
        j+=1
    # Join adjacent factors only when no operator/space separates them (e.g. 4πr³).
    j=0
    while j<len(out)-1:
        a,b=out[j:j+2]
        if a.atom and b.atom:
            out[j:j+2]=[Node(a.raw+b.raw,'<mrow>'+a.xml+b.xml+'</mrow>',a.changed or b.changed,True)];continue
        j+=1
    j=0
    while j<len(out):
        if out[j].raw=='/':
            l=j-1;r=j+1
            while l>=0 and out[l].raw.isspace():l-=1
            while r<len(out) and out[r].raw.isspace():r+=1
            if l>=0 and r<len(out) and out[l].atom and out[r].atom:
                a,b=out[l],out[r]
                out[l:r+1]=[Node(a.raw+'/'+b.raw,'<mfrac><mrow>'+a.plain()+'</mrow><mrow>'+b.plain()+'</mrow></mfrac>',True,True)];j=l;continue
        j+=1
    return out

def M(text):
    return ''.join(('<span class="math-wrap"><math xmlns="http://www.w3.org/1998/Math/MathML" class="book-math"><mrow>'+n.xml+'</mrow></math></span>') if n.changed else escape(n.raw) for n in parse(text))


def F(text):
    """Display a complete formula on one shared mathematical baseline."""
    # Prose belongs to HTML: native MathML collapses text whitespace and
    # cannot wrap explanatory sentences like ordinary paragraphs.
    words=re.findall(r'[A-Za-zÄÖÜäöüß]{3,}',text)
    functions={'sin','cos','tan','cot','log','lim','Var','arcsin','arccos','arctan','exp','Re','Im'}
    if any(word not in functions for word in words):
        return '<div class="formula-prose">'+M(text)+'</div>'
    lines=re.split(r'; | ··· ',text)
    return ''.join('<div class="formula-row"><math xmlns="http://www.w3.org/1998/Math/MathML" class="display-math" display="block"><mrow>'+''.join(n.xml for n in parse(line))+'</mrow></math></div>' for line in lines if line.strip())
