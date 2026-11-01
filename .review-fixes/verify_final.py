from pathlib import Path
import xml.etree.ElementTree as ET
import json, collections
newrefs={'C212','C213','TP200'}
def load(p):
 t=ET.parse(p)
 d={}
 for net in t.findall('./nets/net'):
  nodes=frozenset((n.get('ref'),n.get('pin')) for n in net.findall('node') if n.get('ref') not in newrefs and not n.get('ref','').startswith('#'))
  if nodes:d[nodes]=net.get('name')
 return d
before=load('.review-fixes/before.xml');after=load('.review-fixes/final.xml')
lost=[{'name':v,'nodes':sorted(k)} for k,v in before.items() if k not in after]
new=[{'name':v,'nodes':sorted(k)} for k,v in after.items() if k not in before]
erc=json.loads(Path('.review-fixes/erc-final.json').read_text(encoding='utf8'))
counts=collections.Counter((v['severity'],v['type']) for s in erc['sheets'] for v in s['violations'])
r={'original_physical_connectivity_unchanged':not lost and not new,'removed_connections':lost,'added_connections_excluding_C212_C213_TP200':new,'erc_categories':{'/'.join(k):v for k,v in counts.items()}}
Path('.review-fixes/final-validation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(r,ensure_ascii=False,indent=2))
