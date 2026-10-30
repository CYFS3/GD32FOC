import xml.etree.ElementTree as E,json,sys
r=E.parse(sys.argv[1]); nets=r.findall('./nets/net'); index={(p.get('ref'),p.get('pin')):n for n in nets for p in n.findall('node')}
mapping={'67':'M1_HIN1','68':'M1_HIN2','69':'M1_HIN3','52':'M1_LIN1','53':'M1_LIN2','54':'M1_LIN3','63':'M2_HIN1','64':'M2_HIN2','65':'M2_HIN3','15':'M2_LIN1','16':'M2_LIN2','17':'M2_LIN3','23':'M1_IA','24':'M1_IB','25':'M1_IC','26':'M2_IA','29':'M2_IB','30':'M2_IC','18':'M1_IBUS','34':'M2_IBUS','38':'M1_NTC','39':'M2_NTC','90':'M1_QEI1_A','91':'M1_QEI1_B','35':'M1_QEI1_Z','59':'M2_QEI1_A','60':'M2_QEI1_B','61':'M2_QEI1_Z'}
mapping.update({'33':'M1_VBUS','78':'SPI2_SCK','79':'SPI2_MISO','80':'SPI2_MOSI','1':'M1_SPI1_CS0','2':'M2_SPI1_CS0','51':'M1_BRKIN','31':'M2_BRKIN','21':'MCU_VDDA','22':'MCU_VDDA'})
for pin,name in list(mapping.items()):
 mapping[pin]=name.replace('QEI1_A','HALL_A').replace('QEI1_B','HALL_B').replace('QEI1_Z','HALL_C')
checks=[]
for pin,name in mapping.items():
 n=index.get(('U1',pin)); actual=n.get('name') if n is not None else None
 checks.append({'pin':pin,'expected':name,'actual':actual,'pass':actual==name and len(n.findall('node'))>1 if n is not None else False})
# Verify supply resistor, SPI fanout and fail-safe brake pullups against exact native netlist.
for name,pins in [('MCU supply filter input',[('U1','11'),('R203','1')]),('MCU supply filter output',[('U1','21'),('U1','22'),('R203','2')]),('SPI SCK fanout',[('U1','78'),('R120','2'),('R1120','2')]),('SPI MISO fanout',[('U1','79'),('R118','2'),('R1118','2')]),('SPI MOSI fanout',[('U1','80'),('R117','2'),('R1117','2')]),('M1 brake interface',[('U1','51'),('J201','3'),('R204','2')]),('M2 brake interface',[('U1','31'),('J201','4'),('R205','2')]),('Brake pullup supply',[('U1','11'),('R204','1'),('R205','1')])]:
 ns=[index.get(p) for p in pins];checks.append({'check':name,'pass':ns[0] is not None and all(n is ns[0] for n in ns)})
refs=[c.get('ref') for c in r.findall('./components/comp')]
for ref in ['R109','R1109']:
 a=index.get((ref,'1'));b=index.get((ref,'2'));checks.append({'check':ref+' shunt not bypassed','pass':a is not None and b is not None and a is not b})
a=index.get(('R109','1'));b=index.get(('R1109','1'));checks.append({'check':'Independent bus shunt positive nodes','pass':a is not None and b is not None and a is not b})
for pin in ['18','15','12']:
 a=index.get(('U7',pin));b=index.get(('U1007',pin));checks.append({'check':'Separate driver phase return '+pin,'pass':a is not None and b is not None and a is not b})
print(json.dumps({'components':len(refs),'nets':len(nets),'duplicate_refs':sorted({x for x in refs if refs.count(x)>1}),'unannotated':[x for x in refs if '?' in x],'checks':checks,'pass':all(x['pass'] for x in checks)},ensure_ascii=False,indent=2))
