from pathlib import Path
import sys,json,xml.etree.ElementTree as ET,subprocess
W=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(W/'scripts'))
from migrate_p2 import load,Node
rpt=json.loads((W/'power_review/duplicates.json').read_text())
def state(p):
 r=ET.parse(p)
 return {n.get('name'):sorted((p.get('ref'),p.get('pin')) for p in n.findall('node')) for n in r.findall('./nets/net')}
a,b=state(W/'power_review/before.xml'),state(W/'power_review/after.xml');assert a==b
for name,p in rpt['pages'].items():
 old,ro=load(W/'power_review/baseline'/name);new,rn=load(W/name)
 removed={v['remove'] for v in p['duplicates']}
 from migrate_p2 import prop
 old_items=[old[n.start:n.end] for n in ro.items if isinstance(n,Node) and not (n.key=='symbol' and prop(n,'Reference') in removed)]
 new_items=[new[n.start:n.end] for n in rn.items if isinstance(n,Node)]
 assert old_items==new_items,name
result=json.loads(subprocess.check_output([sys.executable,str(W/'style_review/compare_connectivity.py'),str(W/'power_review/before.xml'),str(W/'power_review/after.xml')],text=True));assert result['pass']
result['net_names_and_all_pinsets_identical']=True
result['net_count']=len(a)
result['only_six_duplicate_symbol_objects_removed']=True
result['remaining_duplicates']=json.loads(subprocess.check_output([sys.executable,str(W/'power_review/deduplicate.py')],text=True))['total_removed']
result['capacitor_connections']={ref:{pin:net for net,pins in b.items() for rr,pin in pins if rr==ref} for ref in ['C143','C1143']}
(W/'power_review/verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
