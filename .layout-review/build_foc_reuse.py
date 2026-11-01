import json,re,collections,xml.etree.ElementTree as E
from pathlib import Path
S={x['reference']:x for x in json.loads(Path('.layout-review/reference-coordinates.json').read_text(encoding='utf8'))['FOC']['footprints']}
P=json.loads(Path('.layout-review/placement-groups.json').read_text(encoding='utf8')); C=P['components']; m1={r:v for r,v in C.items() if v['sheet']=='/FOC_M1/'};m2={r:v for r,v in C.items() if v['sheet']=='/FOC_M2/'}
T=E.parse('.layout-review/q1-after.xml'); nets={}
for n in T.findall('./nets/net'):
 for p in n.findall('node'):nets[(p.get('ref'),p.get('pin'))]=n.get('name')
cn={r:{p:n for (rr,p),n in nets.items() if rr==r} for r in C}
sn={r:{p['number']:p['net'] for p in f['pads'] if p['net']} for r,f in S.items()}
def norm(n):
 n=re.sub(r'^M[12]_','',n)
 return {'SHUNT_RETURN':'IA-','NTC':'NTC1','ENC_A_IN':'HALL_A','ENC_B_IN':'HALL_B','ENC_C_IN':'HALL_C','SPI1_CS0':'SPI1_CSN'}.get(n,n.replace('SPI2_','SPI1_'))
def named(n):return not(n.startswith('$') or n.startswith('Net-') or n.startswith('unconnected') or n.startswith('/'))
def compat(r,s):return {p for p,n in cn[r].items() if not n.startswith('unconnected')}==set(sn[s]) or (r.startswith('CN') and len(cn[r])==1)
def score(r,s,mp):
 a=cn[r];b=sn[s]; agree=0;clash=0;adj=0;detail=[]
 for pin,n in a.items():
  if pin not in b:continue
  if named(n) and named(b[pin]):
   if norm(n)==norm(b[pin]):agree+=1
   else:clash+=1
  for (rr,pp),nn in nets.items():
   if rr!=r and nn==n and rr in mp and pp in sn[mp[rr]] and sn[mp[rr]][pp]==b[pin]:adj+=1
 return agree*3+adj*2-clash*5,agree,clash,adj
# Same reference seed only where named pins agree and none contradict.
mp={};ev={}
for r in m1:
 if r in S and compat(r,r):
  sc,a,c,d=score(r,r,{})
  if a>=1 and c==0:mp[r]=r;ev[r]=[sc,a,c,d,'same ref plus named-pin agreement']
# Grow graph matches, rewarding but never requiring same ref.
for iteration in range(8):
 proposals=[]
 for r in m1:
  if r in mp:continue
  arr=[]
  for s in S:
   if s in mp.values() or not compat(r,s):continue
   if not re.match('[A-Z]+',s) or re.match('[A-Z]+',r)[0]!=re.match('[A-Z]+',s)[0]:continue
   sc,a,c,d=score(r,s,mp)
   if c:continue
   # Named power alone cannot resolve a passive without adjacency or same-ref provenance.
   if d==0 and s!=r:continue
   if a==0 and d==0:continue
   val=str(m1[r]['value']);sv=S[s]['value'];bonus=1 if val==sv else 0
   arr.append((sc+(2 if r==s else 0)+bonus,s,a,c,d))
  arr.sort(reverse=True)
  if arr and (len(arr)==1 or arr[0][0]>arr[1][0]):proposals.append((arr[0][0],r,arr[0]))
 for _,r,b in sorted(proposals,reverse=True):
  if b[1] in mp.values():continue
  mp[r]=b[1];ev[r]=[*b,'graph-neighbor match']
Path('.layout-review/foc-reuse-working.json').write_text(json.dumps({'map':mp,'evidence':ev,'unmatched':{r:m1[r] for r in m1 if r not in mp}},ensure_ascii=False,indent=2),encoding='utf8')
print('current',len(m1),len(m2),'matched',len(mp));print('unmatched',[(r,m1[r]['value'],cn[r]) for r in m1 if r not in mp]);print('renamed',[(r,s) for r,s in mp.items() if r!=s])
