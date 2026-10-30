from audit import *
reports=json.loads((W/'label_wire_audit/candidates.json').read_text())
changes=[]
for report in reports:
 f=W/report['file'];raw=f.read_bytes();assert raw==(W/'label_wire_audit/baseline'/f.name).read_bytes();s=raw.decode();r=parse(s);ops=[];done=set()
 for c in report['candidates']:
  if c['uuid'] in done:continue
  done.add(c['uuid']);w=next(n for n in r.kids('wire') if n.val('uuid')==c['uuid']);ls=[n for n in r.kids('global_label') if xy(n)[1]==c['anchor'][1] and min(p[0] for p in c['wire'])<=xy(n)[0]<=max(p[0] for p in c['wire'])]
  same=[n for n in ls if n.items[1]==c['label'] and any(z['uuid']==c['uuid'] and z['anchor'][:2]==list(xy(n)) for z in report['candidates'])];l=min(same,key=lambda n:xy(n)[0]);x,y=xy(l)
  related=next(z for z in report['candidates'] if z['uuid']==c['uuid'] and z['anchor'][:2]==[x,y]);blocking=[b for b in related['blockers'] if not(b[0]=='global_label' and b[1]==c['label'])]
  for dup in same:
   if dup is not l:ops.append((dup.start,dup.end,''));changes.append(dict(file=f.name,action='remove redundant same-conductor label',label=dup.items[1],at=xy(dup)))
  if not blocking:
   end=max(p[0] for p in c['wire']);p=next(p for p in w.one('pts').kids('xy') if float(p.items[1])==end);ops.append((p.start,p.end,f'(xy {x:.6f} {y:.6f})'));changes.append(dict(file=f.name,action='trim verified dangling tail',label=l.items[1],old_end=[end,y],new_end=[x,y],uuid=w.val('uuid')))
  else:
   if f.name=='HSLink.kicad_sch' and l.items[1]=='HSL_LINK_DP':newx=x;angle=90;justify='left'
   else:newx=min(p[0] for p in c['wire']);angle=180;justify='right'
   text=s[l.start:l.end];local=[]
   for at in [l.one('at')]+[p.one('at') for p in l.kids('property')]:
    if at:local.append((at.start-l.start,at.end-l.start,f'(at {newx:.6f} {y:.6f} {angle})'))
   j=l.one('effects').one('justify');local.append((j.start-l.start,j.end-l.start,f'(justify {justify})'))
   ops.append((l.start,l.end,patches(text,local)));changes.append(dict(file=f.name,action='orient label away from functional wire',label=l.items[1],old_at=c['anchor'],new_at=[newx,y,angle],preserved_wire=c['wire'],blockers=blocking))
 if ops:f.write_bytes(patches(s,ops).encode())
(W/'label_wire_audit/changes.json').write_text(json.dumps(changes,indent=2),encoding='utf-8')
from collections import Counter
print(Counter(c['action'] for c in changes));print(Counter(c['file'] for c in changes))
