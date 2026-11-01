import json,math
from pathlib import Path
j=json.loads(Path('.layout-review/reference-coordinates.json').read_text(encoding='utf8'))
for key in j:
 fs=j[key]['footprints'];by={x['reference']:x for x in fs};print('\n',key,'counts',j[key]['counts']);print('edges',j[key]['outline'])
 for ref in (['Q1','Q3','U7','U10','R81','R82','R83','R109'] if key=='FOC' else ['U6','USB2','X2','D5']):
  f=by.get(ref)
  if not f:continue
  print('DETAIL',ref, f['at'], f.get('schematic',{}).get('properties',{}), '\nPADS',f['pads'])
 for ref in (['U7','U10','Q5','Q8'] if key=='FOC' else ['U6','USB2','X2']):
  c=by[ref]['at'];near=sorted([(math.hypot(f['at'][0]-c[0],f['at'][1]-c[1]),f) for f in fs if f['reference']!=ref],key=lambda x:x[0])[:18]
  print('NEAR',ref,[(f['reference'],f['value'],f['at'],round(d,3),[(p['number'],p['net']) for p in f['pads']]) for d,f in near])
 if key=='FOC':
  for f in fs:
   if 'XT30' in f['footprint']:print('XT30',f)
