from pathlib import Path
import sys,json,math
W=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(W/'scripts'))
from migrate_p2 import parse,prop,patches
reports=[]
for filename,ref in [('FOC_M1.kicad_sch','U7'),('FOC_M2.kicad_sch','U1007')]:
 path=W/filename; raw=path.read_bytes(); s=raw.decode('utf-8'); r=parse(s);ops=[];changes=[]
 assert raw==(W/'u7_label_fix/baseline'/filename).read_bytes(), 'File changed since snapshot'
 sym=next(n for n in r.kids('symbol') if prop(n,'Reference')==ref)
 lib=next(n for n in r.one('lib_symbols').kids('symbol') if n.items[1]==sym.val('lib_id'))
 ys={round(204.47-float(p.one('at').items[2]),6):p.val('number') for sub in lib.kids('symbol') for p in sub.kids('pin') if float(p.one('at').items[3])==180}
 for wire in r.kids('wire'):
  pts=wire.one('pts').kids('xy');xy=[tuple(map(float,p.items[1:])) for p in pts]
  if {p[0] for p in xy}!={303.53,311.15} or xy[0][1]!=xy[1][1] or xy[0][1] not in ys:continue
  y=xy[0][1];label=[n for n in r.kids('global_label') if tuple(map(float,n.one('at').items[1:3]))==(306.07,y)]
  assert len(label)==1
  # Confirm no other wire intersects the removed open tail, including diagonal intersections.
  for other in r.kids('wire'):
   if other is wire:continue
   a,b=[tuple(map(float,p.items[1:])) for p in other.one('pts').kids('xy')]
   if a[1]==b[1]:
    assert not(a[1]==y and max(min(a[0],b[0]),306.070001)<=min(max(a[0],b[0]),311.15))
   elif min(a[1],b[1])<=y<=max(a[1],b[1]):
    x=a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1]);assert not 306.07<x<=311.15
  for kind in ['label','global_label','hierarchical_label','junction','no_connect']:
   for n in r.kids(kind):
    x,yy=map(float,n.one('at').items[1:3]);assert not (yy==y and 306.07<x<=311.15)
  # All placed symbol pin locations, honoring rotations and mirrors.
  for n in r.kids('symbol'):
   sx,sy,ang=map(float,n.one('at').items[1:]);libn=next(z for z in r.one('lib_symbols').kids('symbol') if z.items[1]==n.val('lib_id'))
   for sub in libn.kids('symbol'):
    for p in sub.kids('pin'):
     px,py=map(float,p.one('at').items[1:3]);mir=n.val('mirror')
     if mir=='x':py=-py
     if mir=='y':px=-px
     a=math.radians(ang);x=round(sx+px*math.cos(a)-py*math.sin(a),6);yy=round(sy-px*math.sin(a)-py*math.cos(a),6)
     assert not (yy==y and 306.07<x<=311.15),(ref,prop(n,'Reference'),p.val('number'))
  p=next(p for p in pts if p.items[1]=='311.15');old=s[p.start:p.end];new=old.replace('311.15','306.07');ops.append((p.start,p.end,new))
  changes.append({'pin':ys[y],'label':label[0].items[1],'wire_uuid':wire.val('uuid'),'y':y,'old_end_x':311.15,'new_end_x':306.07})
 assert len(changes)==10,(filename,len(changes))
 out=patches(s,ops);assert len(s)-len(out)==0
 path.write_bytes(out.encode('utf-8'));reports.append({'file':filename,'reference':ref,'changed_wires':changes})
(W/'u7_label_fix/changes.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
print(json.dumps(reports,indent=2))
