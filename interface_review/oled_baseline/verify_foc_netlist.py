import xml.etree.ElementTree as ET
import json,sys
from pathlib import Path
root=ET.parse(sys.argv[1]).getroot()
nets=root.findall('./nets/net')
pin_net={}
for n in nets:
 for p in n.findall('node'): pin_net[(p.get('ref'),p.get('pin'))]=n
expected={'67':'HIN1','68':'HIN2','69':'HIN3','52':'LIN1','53':'LIN2','54':'LIN3','15':'IA','16':'IB','17':'IC','18':'IBUS','33':'VBUS','34':'COM','23':'VA','24':'VB','25':'VC','26':'NTC','63':'QEI1_A','64':'QEI1_B','65':'QEI1_Z','29':'SPI1_CS0','30':'SPI1_SCK','31':'SPI1_MISO','32':'SPI1_MOSI'}
results=[]
for pin,name in expected.items():
 n=pin_net.get(('U1',pin)); actual=n.get('name') if n is not None else None
 nodes=[dict(p.attrib) for p in n.findall('node')] if n is not None else []
 results.append({'pin':pin,'expected':name,'actual':actual,'connected_nodes':len(nodes),'pass':actual==name and len(nodes)>1})
comps=root.findall('./components/comp'); refs=[c.get('ref') for c in comps]
report={'components':len(comps),'nets':len(nets),'duplicate_refs':sorted({x for x in refs if refs.count(x)>1}),'unannotated_refs':[x for x in refs if '?' in x],'interfaces':results,'all_interfaces_connected':all(x['pass'] for x in results)}
print(json.dumps(report,ensure_ascii=False,indent=2))
