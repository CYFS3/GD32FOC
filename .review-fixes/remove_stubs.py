from clean_endpoints import *
e=json.loads(Path('.review-gd32/erc-after.json').read_text(encoding='utf8'));ids={i['uuid'] for sh in e['sheets'] for v in sh['violations'] if v['type']=='unconnected_wire_endpoint' for i in v['items']}
for fn in ['FOC_M1.kicad_sch','FOC_M2.kicad_sch']:
 p=Path(fn);text=p.read_text(encoding='utf8');s=parse(text);pins=pin_positions(s);edits=[]
 for n in nodes(text)[0]['children']:
  if kind(n)!='wire' or val(n,'uuid') not in ids:continue
  w=parse(text[n['start']:n['end']]);pts=[tuple(map(float,p[1:])) for p in children(one(w,'pts'),'xy')];(x1,y),(x2,y2)=pts;assert y==y2
  interior=[]
  for r,num,nm,x,py in pins:
   if abs(py-y)<1e-6 and min(x1,x2)+1e-6<x<max(x1,x2)-1e-6:interior.append((r,num,x,py))
  for obj in s[1:]:
   if not isinstance(obj,list) or obj[0] not in ['wire','junction','label','global_label','hierarchical_label']:continue
   positions=children(one(obj,'pts'),'xy') if one(obj,'pts') else children(obj,'at')
   for pos in positions:
    x,py=map(float,pos[1:3])
    if abs(py-y)<1e-6 and min(x1,x2)+1e-6<x<max(x1,x2)-1e-6:interior.append(obj)
  assert not interior,(fn,val(n,'uuid'),interior)
  edits.append((n['start'],n['end']));print('Remove empty dangling stub',fn,val(n,'uuid'))
 for a,b in sorted(edits,reverse=True):text=text[:a]+text[b:]
 p.write_text(text,encoding='utf8')
