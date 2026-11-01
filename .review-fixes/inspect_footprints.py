from pathlib import Path as P
import json
exec(P('.review-gd32/crystal_work.py').read_text(encoding='utf8').split("s=P('MCU.kicad_sch')")[0])
libs={}
for f in P('.').glob('*.kicad_sym'):
 try:
  libs[f.stem]={x[1]:x for x in children(parse(f.read_text(encoding='utf8')),'symbol')}
 except Exception as e:print(f,e)
rows=[]
for f in P('.').glob('*.kicad_sch'):
 t=parse(f.read_text(encoding='utf8'))
 for s in children(t,'symbol'):
  p={x[1]:x[2] for x in children(s,'property')}; fp=p.get('Footprint','')
  if fp=='ProDoc_Boa-easyedapro:':
   lid=one(s,'lib_id')[1];ln,sn=lid.split(':',1);src=libs.get(ln,{}).get(sn,[]);sp={x[1]:x[2] for x in children(src,'property')}
   rows.append({'sheet':str(f),'ref':p.get('Reference'),'value':p.get('Value'),'lib_id':lid,'source_footprint':sp.get('Footprint'),'other_props':p})
P('.review-fixes/empty-footprint-source-map.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
for r in rows: print(r['ref'],r['value'],r['source_footprint'])
