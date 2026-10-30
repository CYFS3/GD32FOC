from migrate_p2 import *
import xml.etree.ElementTree as ET
O=W/'interface_review'
a=ET.parse(O/'baseline/audit_netlist.xml');b=ET.parse(O/'final.xml')
def nets(t):return {n.attrib['name']:{(x.attrib['ref'],x.attrib['pin']) for x in n.findall('node')} for n in t.findall('.//nets/net')}
aN,bN=nets(a),nets(b);newrefs={c.attrib['ref'] for c in b.findall('.//components/comp')}-{c.attrib['ref'] for c in a.findall('.//components/comp')};addedpins={('U1',p) for p in ['3','4','32','83','84','85','89','92','93']}
oldgroups={frozenset(g-addedpins) for g in aN.values() if g-addedpins};newgroups={frozenset({p for p in g if p[0] not in newrefs}-addedpins) for g in bN.values() if {p for p in g if p[0] not in newrefs}-addedpins};print('Full old net partition preserved:',oldgroups==newgroups,'(concurrent FOC changes may differ)')
expect={'LCD_SCK':{('U1','89'),('J300','3')},'LCD_MOSI':{('U1','32'),('J300','4')},'LCD_CS_N':{('U1','92'),('J300','5'),('R310','2')},'LCD_DC':{('U1','93'),('J300','6')},'LCD_RST_N':{('U1','3'),('J300','7'),('R311','2')},'LCD_BL_GPIO':{('U1','4'),('R312','1')},'LCD_BL_CTRL':{('J300','8'),('R312','2'),('R313','1')}}
for i in range(3):
 expect[f'BTN_{i+1}_N']={('U1',str(83+i)),(f'R{314+i*2}','2'),(f'R{315+i*2}','2'),(f'C{302+i}','1')}
 expect[f'BTN_{i+1}_SW']={(f'SW{300+i}','4'),(f'R{314+i*2}','1')}
for name,g in expect.items():assert bN[name]==g,(name,bN.get(name),g)
assert {('J300','1'),('C300','1'),('C301','1'),('R310','1'),('R311','1'),('R315','1'),('R317','1'),('R319','1')}<=bN['VCC']
assert {('J300','2'),('C300','2'),('C301','2'),('R313','2'),('C302','2'),('C303','2'),('C304','2'),('SW300','1'),('SW301','1'),('SW302','1')}<=bN['GND']
r3=next(c for c in b.findall('.//components/comp') if c.attrib['ref']=='R3');assert r3.findtext('value')=='0R';assert r3.find("property[@name='Manufacturer Part']").attrib['value']=='0402WGF0000TCE'
report={'scope':'Final LCD/button nets and R3 identity only; encoder changes verified by parent final_delta.json','interface_components':sorted(newrefs & ({'J300'}|{f'R{i}' for i in range(310,320)}|{f'C{i}' for i in range(300,305)}|{f'SW{i}' for i in range(300,303)})),'expected_new_signal_nets_verified':len(expect),'R3_metadata_verified':True};(O/'interface_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))

