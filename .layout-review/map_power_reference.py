import json,re,xml.etree.ElementTree as E
from pathlib import Path
load=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
P=load('.layout-review/placement-groups.json');C=P['components']; S={f['reference']:f for f in load('.layout-review/reference-coordinates.json')['FOC']['footprints']}
groups=['shared_input','shared_bulk','shared_buck12','shared_buck5','analog_reference','logic_ldo']; refs=[r for g in groups for r in P['groups'][g]['refs']]
T=E.parse('.layout-review/q1-after.xml'); cn={r:{} for r in C}
for n in T.findall('./nets/net'):
 for p in n.findall('node'):cn.setdefault(p.get('ref'),{})[p.get('pin')]=n.get('name')
sn={r:{p['number']:p['net'] for p in f['pads'] if p['net']} for r,f in S.items()}
# Exact active identities; source connector is intentionally different model.
mp={'CN1':'CN3','Q1':'Q1','Q2':'Q2','Q3':'Q3','U6':'U2','U19':'U5','U12':'U6','U2':'U4','U20':'U3'}
for r in mp:print('ANCHOR',r,C[r]['value'],mp[r],S[mp[r]]['value'],cn[r],sn[mp[r]])
# Build net correspondence using same physical pin numbers of verified active parts.
nmap={};bad=[]
for r,s in mp.items():
 for pin,n in cn[r].items():
  if pin in sn[s] and not n.startswith('unconnected'):
   v=sn[s][pin]
   if n in nmap and nmap[n]!=v:bad.append((r,pin,n,v,nmap[n]))
   else:nmap[n]=v
print('CONFLICT',bad)
def score(r,s):
 a=cn[r];b=sn[s]; best=None
 for swap in [False,True] if set(a)=={'1','2'} and set(b)=={'1','2'} else [False]:
  pinmap={p:('2' if p=='1' else '1') if swap else p for p in a}; yes=no=0
  for pin,n in a.items():
   q=pinmap[pin]
   if q not in b:continue
   if n in nmap:
    if nmap[n]==b[q]:yes+=1
    else:no+=1
  val=(str(C[r]['value'])==str(S[s]['value']));mpn=C[r].get('mpn'); srcmpn=S[s]['schematic']['properties'].get('Manufacturer Part') if S[s].get('schematic') else None
  same=bool(mpn and mpn==srcmpn)
  v=(yes*10-no*100+val*2+same*3,yes,no,pinmap)
  if best is None or v[0]>best[0]:best=v
 return best
pm={r:{p:p for p in cn[r]} for r in mp};evidence={r:'Verified active MPN/function anchor; same pin function' for r in mp}
used=set(load('.layout-review/foc-reuse-map.json')['reference_not_reused']) if False else set(x['source_ref'] for x in load('.layout-review/foc-reuse-map.json')['rows'] if x.get('source_ref'))
for it in range(20):
 proposals=[]
 for r in refs:
  if r in mp:continue
  opts=[]
  for s in S:
   if s in mp.values() or s in used:continue
   if not re.match('[A-Z]+',s) or re.match('[A-Z]+',r)[0]!=re.match('[A-Z]+',s)[0]:continue
   if len(cn[r])!=len(sn[s]):continue
   v=score(r,s)
   if v[1] and not v[2]:opts.append((v[0],s,v))
  opts.sort(key=lambda x:x[0],reverse=True)
  if opts and (len(opts)==1 or opts[0][0]>opts[1][0]):proposals.append((opts[0][0],r,opts[0]))
 if not proposals:break
 for _,r,(_,s,v) in sorted(proposals,reverse=True):
  if s in mp.values():continue
  mp[r]=s;pm[r]=v[3];evidence[r]='Pin-network topology propagated from verified active anchors; value/MPN tie break'
  for pin,n in cn[r].items():
   if pm[r][pin] in sn[s]:nmap.setdefault(n,sn[s][pm[r][pin]])
print('MATCH',len(mp),len(refs));print('UNMATCHED',[(r,C[r]['value'],cn[r]) for r in refs if r not in mp]);print('MAPPING',mp)
Path('.layout-review/power-map-working.json').write_text(json.dumps(dict(map=mp,pinmaps=pm,netmap=nmap,evidence=evidence,unmatched=[r for r in refs if r not in mp],refs=refs),ensure_ascii=False,indent=2),encoding='utf8')
