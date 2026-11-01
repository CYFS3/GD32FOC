import xml.etree.ElementTree as E,json
from pathlib import Path
def netset(fn):
 r=E.parse(fn);return {frozenset((p.get('ref'),p.get('pin')) for p in n.findall('node') if not p.get('ref').startswith('#')):n.get('name') for n in r.findall('./nets/net') if any(not p.get('ref').startswith('#') for p in n.findall('node'))}
a=netset('.review-fixes/before-power-model.xml');b=netset('.review-fixes/after-power-model.xml');assert a.keys()==b.keys(),(a.keys()-b.keys(),b.keys()-a.keys())
for refs,old in a.items():
 if old!=b[refs]:print('Net renamed only:',old,'=>',b[refs])
for ref in ['U7','U1007']:
 for pn,phase in [('18','A'),('15','B'),('12','C')]:
  n=next((name for members,name in b.items() if (ref,pn) in members));assert n==('M1_' if ref=='U7' else 'M2_')+'M'+phase,(ref,pn,n)
print('PASS: all effective ref/pin net partitions unchanged; VS1/2/3 tied to phase A/B/C for both drivers.')
e=json.loads(Path('.review-fixes/erc-power-model.json').read_text(encoding='utf8'));vs=[v for s in e['sheets'] for v in s['violations']]
print('ERC',len(vs),'errors',sum(v['severity']=='error' for v in vs))
