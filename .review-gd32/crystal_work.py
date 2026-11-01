import re,json,pathlib,collections
P=pathlib.Path
root=P.cwd()
def parse(s):
 ts=re.findall(r'"(?:\\.|[^"\\])*"|[^\s()]+|[()]',s); stack=[]; out=[]
 for t in ts:
  if t=='(':
   n=[]
   if stack: stack[-1].append(n)
   else: out.append(n)
   stack.append(n)
  elif t==')':stack.pop()
  else:stack[-1].append(json.loads(t) if t.startswith('"') else t)
 return out[0]
def children(n,k):return [x for x in n if isinstance(x,list) and x and x[0]==k]
def one(n,k):return next(iter(children(n,k)),None)
s=P('MCU.kicad_sch').read_text(encoding='utf-8'); sch=parse(s)
net=parse(P('.review-gd32/MCU.before.net').read_text(encoding='utf-8'))
host=json.loads(P(r'C:\Users\CYFSybW\AppData\Local\Temp\dsh-spill-elKFml\session-42b74e2adfa6\3acb90394be9-get_project_netlist.txt').read_text(encoding='utf-8'))['netlist']
disk={}
for n in children(one(net,'nets'),'net'):
 nodes={(one(x,'ref')[1],one(x,'pin')[1]) for x in children(n,'node')}
 for ref,pin in nodes:
  if ref=='U1':disk[pin]=(one(n,'name')[1],nodes)
h={}
for n in host['nets']:
 nodes={(x['referenceDesignator'],str(x['pinNumber'])) for x in n['pinReferences']}
 for ref,pin in nodes:
  if ref=='U1':h[pin]=(n['name'],nodes)
print('U1 disk/host pin net counts:',len(disk),len(h))
for pin in sorted(set(disk)|set(h),key=int):
 d=disk.get(pin); a=h.get(pin)
 if d and a and (d[0]!=a[0] or d[1]!={x for x in a[1] if x[0] in {one(c,'ref')[1] for c in children(one(net,'components'),'comp')}}):print('REAL DIFFERENCE',pin,'disk',d,'host',a)
print('OSC pins:',{p:(disk.get(p),h.get(p)) for p in ['12','13']})
print('Placed symbols:')
for n in children(sch,'symbol'):
 print(next(x[2] for x in children(n,'property') if x[1]=='Reference'),one(n,'lib_id')[1],one(n,'at')[1:])
print('Geometry near U1 left OSC:')
for n in sch:
 if not isinstance(n,list) or n[0] not in ['wire','label','global_label','junction','no_connect','text']:continue
 ats=children(n,'at')
 if one(n,'pts'):ats+=children(one(n,'pts'),'xy')
 if any(0<float(a[1])<60 and 100<float(a[2])<160 for a in ats):print(n)
