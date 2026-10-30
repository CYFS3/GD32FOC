import xml.etree.ElementTree as E,json,sys
mapping={'FPC1':'FPC300','C56':'C320','C57':'C321','C58':'C322','C59':'C323','C63':'C324','C65':'C325','R27':'R320','R30':'R321','R29':'R322','R31':'R323','R34':'R324','D3':'D300'}
def load(p):
 r=E.parse(p);return {c.get('ref'):c for c in r.findall('./components/comp')},{n.get('name'):{(p.get('ref'),p.get('pin'))for p in n.findall('node')}for n in r.findall('./nets/net')}
ref,rn=load('interface_review/reference_full.xml');old,on=load('oled_review/parent_before.xml');new,nn=load(sys.argv[1]);newrefs=set(mapping.values())
expected={frozenset((mapping[r],p)for r,p in ps if r in mapping)for ps in rn.values()if any(r in mapping for r,p in ps)}
actual={frozenset((r,p)for r,p in ps if r in newrefs)for ps in nn.values()if any(r in newrefs for r,p in ps)}
removed={'J300','C300','C301','R310','R311','R312','R313'};changedpins={'3','4','32','89','92','93'}
def groups(nets):
 return {frozenset((r,p)for r,p in ps if r in old and r not in removed and not(r=='U1'and p in changedpins))for ps in nets.values()if any(r in old and r not in removed and not(r=='U1'and p in changedpins)for r,p in ps)}
ix={pin:n for n,ps in nn.items()for pin in ps};checks={'OLED_reference_topology_exact':expected==actual,'OLED_reference_values_exact':all(ref[a].findtext('value')==new[b].findtext('value')for a,b in mapping.items()),'other_circuit_connectivity_unchanged':groups(on)==groups(nn),'OLED_SCL_to_PB6':ix.get(('FPC300','15'))==ix.get(('U1','92')),'OLED_SDA_to_PB7':ix.get(('FPC300','16'))==ix.get(('U1','93')),'released_MCU_pins_unconnected':all(len(nn[ix[('U1',p)]])==1 for p in ['3','4','32','89']),'SPI_display_parts_removed':not(removed&set(new))}
print(json.dumps({'checks':checks,'pass':all(checks.values()),'mapping':mapping,'components':len(new)},indent=2))
