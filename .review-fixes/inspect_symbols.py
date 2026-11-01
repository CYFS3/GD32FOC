from pathlib import Path as P
import json,collections
exec(P('.review-gd32/crystal_work.py').read_text(encoding='utf8').split("s=P('MCU.kicad_sch')")[0])
for f in P('.').glob('*.kicad_sch'):
 if f.name in ['MCU.kicad_sch','GD32F5_FOC.kicad_sch']:continue
 s=parse(f.read_text(encoding='utf8')); print('\nFILE',f)
 for lib in children(one(s,'lib_symbols'),'symbol'):
  pins=[p for sub in children(lib,'symbol') for p in children(sub,'pin')]
  print(lib[1],[(one(p,'number')[1],one(p,'name')[1],p[1]) for p in pins])
e=json.loads(P('.review-gd32/erc-after.json').read_text(encoding='utf8'))
for sh in e['sheets']:
 for v in sh['violations']:
  if v['type'] in ['unconnected_wire_endpoint','pin_not_connected']:print(sh['path'],v)
