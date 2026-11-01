from pathlib import Path as P
import json
exec(P('.review-gd32/crystal_work.py').read_text(encoding='utf8').split("s=P('MCU.kicad_sch')")[0])
rows=[]
for f in P('.').glob('*.kicad_sch'):
 for s in children(parse(f.read_text(encoding='utf8')),'symbol'):
  p={x[1]:x[2] for x in children(s,'property')};fp=p.get('Footprint','')
  if fp.rsplit(':',1)[-1] in ['C0402','R0402','C0603','R0603','测试点','SO-8_L4.9-W3.9-P1.27-LS6.0-BL-EP']:
   rows.append({'sheet':str(f),**p})
P('.review-fixes/named-footprint-metadata.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
for p in rows: print(p.get('Reference'),p.get('Footprint'),p.get('Supplier Footprint'),p.get('3D Model Title'),p.get('Value'))
