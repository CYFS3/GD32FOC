from pin_types import *
for fn in ['FOC_M1.kicad_sch','FOC_M2.kicad_sch','ProDoc_Boa-easyedapro.kicad_sym']:
 p=Path(fn);s=p.read_text(encoding='utf8');ed=[];root=nodes(s)[0];lib=next((c for c in root['children'] if kind(c)=='lib_symbols'),root)
 for sym in lib['children']:
  if kind(sym)!='symbol' or not sym['tokens'][1][0].endswith('FD6288Q_C328453'):continue
  for pn in walk(sym):
   if kind(pn)=='pin' and val(pn,'number') in ['12','15','18']:
    old,a,b=pn['tokens'][1];ed.append((a,b,'passive'))
 for a,b,n in sorted(ed,reverse=True):s=s[:a]+n+s[b:]
 p.write_text(s,encoding='utf8');print(fn,len(ed))
p=Path('power.kicad_sch');s=p.read_text(encoding='utf8');ed=[]
mp={'Q3':'WSD80120DN56_GDS123','C164':'50TZV220M10X10.5','C165':'50TZV220M10X10.5','L6':'SMNR6045-680MT','L9':'MPIH252010-4R7M-LF'}
for n in nodes(s)[0]['children']:
 if kind(n)!='symbol':continue
 props={c['tokens'][1][0]:c for c in n['children'] if kind(c)=='property'};ref=props['Reference']['tokens'][2][0]
 if ref in mp:
  old,a,b=props['Footprint']['tokens'][2];ed.append((a,b,json.dumps('VerifiedParts:'+mp[ref])))
for a,b,n in sorted(ed,reverse=True):s=s[:a]+n+s[b:]
p.write_text(s,encoding='utf8');print('footprints',len(ed))
