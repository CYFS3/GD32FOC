import sys,json
sys.path.insert(0,'scripts')
from migrate_p2 import load,W
out={}
for f in ['MCU','power','FOC_M1','FOC_M2','HSLink']:
 s,r=load(W/(f+'.kicad_sch'));hits=[]
 for n in r.kids('global_label'):
  x,y,a=map(float,n.one('at').items[1:]);d=1 if a==0 else -1 if a==180 else 0
  if not d:continue
  for w in r.kids('wire'):
   p,q=[tuple(map(float,z.items[1:3])) for z in w.one('pts').kids('xy')]
   if abs(p[1]-y)<1e-5 and abs(q[1]-y)<1e-5 and min(p[0],q[0])-1e-5<=x<=max(p[0],q[0])+1e-5 and ((d==1 and max(p[0],q[0])>x+.001) or(d==-1 and min(p[0],q[0])<x-.001)):hits.append(n.items[1]);break
 out[f]=hits
print(json.dumps({'remaining':out,'pass':not any(out.values())},indent=2))
