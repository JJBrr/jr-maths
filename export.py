"""Reproduzierbares, eigenständig nutzbares Quellcodepaket ohne Hosting-Identität."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parent
TARGET=ROOT/'dist/downloads/mathepfad-quellcode.zip'
TARGET.parent.mkdir(parents=True,exist_ok=True)
paths=[]
for name in ('content','assets','templates','docs','.github','.vscode','dist'):
    paths.extend(p for p in (ROOT/name).rglob('*') if p.is_file())
paths.extend(ROOT/name for name in ('README.md','build.py','mathtext.py','graph_lab.py','recap.py','recap_data.json','pdf_exports.py','check.py','export.py','.gitignore'))
with ZipFile(TARGET,'w',compression=ZIP_DEFLATED) as archive:
    for p in sorted(set(paths)):
        rel=p.relative_to(ROOT)
        if 'downloads' in rel.parts or '__pycache__' in rel.parts or p.suffix=='.zip':continue
        entry=ZipInfo('mathepfad/'+str(rel).replace('\\','/'),date_time=(2026,9,24,0,0,0))
        entry.compress_type=ZIP_DEFLATED
        archive.writestr(entry,p.read_bytes())
print(f'Quellcodepaket: {TARGET.name} ({TARGET.stat().st_size:,} Bytes)')
