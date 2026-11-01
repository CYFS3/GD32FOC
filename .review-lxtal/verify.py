import xml.etree.ElementTree as E,json,collections
from pathlib import Path as P
def nets(f):
 t=E.parse(f);return {n.get('name'):{(x.get('ref'),x.get('pin')) for x in n.findall('node')} for n in t.findall('./nets/net')}
a=nets('.review-lxtal/before.xml');b=nets('.review-lxtal/after.xml')
for target in [{('U1','8'),('Y201','1'),('C214','1')},{('U1','9'),('Y201','2'),('C215','1')}]:assert target in b.values(),target
assert b['GND']==a['GND']|{('C214','2'),('C215','2')}
skip={'GND'}|{k for k,v in a.items() if v in [{('U1','8')},{('U1','9')}]}
for k,v in a.items():
 if k not in skip:assert b[k]==v,(k,v,b.get(k))
assert len(a)==len(b)
refs=[x.get('ref') for x in E.parse('.review-lxtal/after.xml').findall('./components/comp')];assert len(refs)==len(set(refs))
def counts(f):return collections.Counter((v['severity'],v['type']) for s in json.loads(P(f).read_text(encoding='utf8'))['sheets'] for v in s['violations'])
assert counts('.review-lxtal/erc-before.json')==counts('.review-lxtal/erc-after.json')
r={'connectivity':'PASS exact U1.8-Y201.1-C214.1 and U1.9-Y201.2-C215.1; capacitor pin2 GND','other_nets':'UNCHANGED','unique_references':True,'erc_before_after':str(counts('.review-lxtal/erc-after.json'))}
P('.review-lxtal/validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
