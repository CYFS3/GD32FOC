from pin_types import *
import math,uuid
exec(Path('.review-gd32/crystal_work.py').read_text(encoding='utf8').split("s=P('MCU.kicad_sch')")[0])
# Enumerate all placed physical pin ends for endpoint and unused-pin checking.
def pin_positions(s):
 libs={x[1]:x for x in children(one(s,'lib_symbols'),'symbol')};out=[]
 for sym in children(s,'symbol'):
  lib=libs[one(sym,'lib_id')[1]];unit=int(one(sym,'unit')[1]);at=one(sym,'at');x,y,a=map(float,at[1:]);r=math.radians(a)
  mirror=one(sym,'mirror');mx=-1 if mirror and mirror[1]=='y' else 1;my=-1 if mirror and mirror[1]=='x' else 1
  ref=next(p[2] for p in children(sym,'property') if p[1]=='Reference')
  for sub in children(lib,'symbol'):
   u=int(sub[1].rsplit('_',2)[1])
   if u not in [0,unit]:continue
   for p in children(sub,'pin'):
    pa=one(p,'at');px=float(pa[1])*mx;py=-float(pa[2])*my
    xx=x+px*math.cos(r)+py*math.sin(r);yy=y-px*math.sin(r)+py*math.cos(r)
    out.append((ref,one(p,'number')[1],one(p,'name')[1],round(xx,6),round(yy,6)))
 return out
if __name__=='__main__':
 e=json.loads(Path('.review-gd32/erc-after.json').read_text(encoding='utf8'));ids={i['uuid'] for sh in e['sheets'] for v in sh['violations'] if v['type']=='unconnected_wire_endpoint' for i in v['items']}
 for fn in ['FOC_M1.kicad_sch','FOC_M2.kicad_sch','power.kicad_sch','HSLink.kicad_sch']:
  p=Path(fn);text=p.read_text(encoding='utf8');s=parse(text);pins=pin_positions(s);edits=[];adds=[]
  targets={('U7',str(n)) for n in [5,7,8,21]}|{('U1007',str(n)) for n in [5,7,8,21]}|{('U6','6'),('USB8002','3'),('USB8002','9')}
  for ref,num,name,x,y in pins:
   if (ref,num) in targets:
    if any(abs(float(one(n,'at')[1])-x)<1e-6 and abs(float(one(n,'at')[2])-y)<1e-6 for n in children(s,'no_connect')):continue
    adds.append(f'(no_connect (at {x:g} {y:g}) (uuid "{uuid.uuid4()}"))');print('NC',fn,ref,num,name,x,y)
  for n in nodes(text)[0]['children']:
   if kind(n)!='wire' or val(n,'uuid') not in ids:continue
   w=parse(text[n['start']:n['end']]);pts=[tuple(map(float,p[1:])) for p in children(one(w,'pts'),'xy')]
   print('STUB',fn,val(n,'uuid'),pts,'pins near',[(ref,num,name,x,y) for ref,num,name,x,y in pins if any(abs(x-xx)<10 and abs(y-yy)<3 for xx,yy in pts)])
  if adds:
   text=text.rstrip()[:-1]+'\n'+'\n'.join(adds)+'\n)\n';p.write_text(text,encoding='utf8')
