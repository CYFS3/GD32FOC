from pathlib import Path
from decimal import Decimal
import sys,shutil,uuid,re,subprocess
sys.path.insert(0,str(Path.cwd()/'scripts'))
from migrate_p2 import load,patches
W=Path.cwd(); out=W/'c130_recheck'; base=out/'baseline';base.mkdir(exist_ok=True)
cli=r'C:\Users\RTT\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe'
for p in W.glob('*.kicad_sch'):
 assert not (base/p.name).exists();shutil.copy2(p,base/p.name)
subprocess.run([cli,'sch','export','netlist','--format','kicadxml','-o',str(out/'before.xml'),str(W/'GD32F5_FOC.kicad_sch')],check=True)
for k in [1,2]:
 p=W/f'FOC_M{k}.kicad_sch';s,r=load(p);ops=[];extra=[]
 for n in r.kids('global_label'):
  at=n.one('at');x,y,a=at.items[1:]
  if n.items[1] not in [f'M{k}_VB{i}' for i in [1,2,3]] or x!='341.63' or y not in ['199.39','210.82','222.25']:continue
  ny=f'{Decimal(y)-Decimal("3.81"):.6f}'
  t=s[n.start:n.end];t=t.replace(s[at.start:at.end],f'(at 341.630000 {ny} 0)',1).replace('(justify right)','(justify left)')
  ops.append((n.start,n.end,t))
  extra.append(f'(wire (pts (xy 341.630000 {y}) (xy 341.630000 {ny})) (stroke (width 0) (type default)) (uuid "{uuid.uuid4()}"))')
  extra.append(f'(junction (at 341.630000 {y}) (diameter 0) (color 0 0 0 0) (uuid "{uuid.uuid4()}"))')
 assert len(ops)==3
 ops.append((r.end-1,r.end-1,'\n'+'\n'.join(extra)+'\n'))
 with p.open('w',encoding='utf-8',newline='') as f:f.write(patches(s,ops))
subprocess.run([cli,'sch','export','netlist','--format','kicadxml','-o',str(out/'after.xml'),str(W/'GD32F5_FOC.kicad_sch')],check=True)
subprocess.run([cli,'sch','export','pdf','--exclude-pdf-property-popups','-o',str(out/'updated.pdf'),str(W/'GD32F5_FOC.kicad_sch')],check=True)
import xml.etree.ElementTree as ET,json
def graph(p):
 r=ET.parse(p).getroot()
 return {n.attrib['name']:sorted((x.attrib['ref'],x.attrib['pin']) for x in n.findall('node')) for n in r.findall('./nets/net')}
a,b=graph(out/'before.xml'),graph(out/'after.xml');assert a==b
print('COMPLETE NATIVE CONNECTIVITY IDENTICAL',len(a),'nets',sum(map(len,a.values())),'nodes')
