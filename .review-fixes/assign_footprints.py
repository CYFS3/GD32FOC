from pin_types import *
records=json.loads(Path('.review-fixes/empty-footprint-source-map.json').read_text(encoding='utf8'))
base=Path('D:/KiCad/HQ10.0/share/kicad/footprints');maps={};unresolved=[]
for x in records:
 fp=None;package=x['other_props'].get('Supplier Footprint');sid=x['lib_id'].split(':')[-1]
 if sid=='C1206_S_1' and package=='1206':fp='Capacitor_SMD:C_1206_3216Metric'
 elif x['ref'] in ['C67','C66','C172','C68']:fp='Capacitor_SMD:C_0603_1608Metric'
 elif x['ref'] in ['R47','R43','R154','R44','R45','R155','R46']:fp='Resistor_SMD:R_0603_1608Metric'
 elif x['ref'] in ['U10','U1010'] and package=='TSSOP-14':fp='Package_SO:TSSOP-14_4.4x5mm_P0.65mm'
 if fp:
  lib,name=fp.split(':');assert (base/(lib+'.pretty')/(name+'.kicad_mod')).is_file();maps[(x['sheet'],x['ref'])]=fp
 else:unresolved.append(x)
logs=[]
for fn in ['FOC_M1.kicad_sch','FOC_M2.kicad_sch','power.kicad_sch','Interface.kicad_sch']:
 p=Path(fn);text=p.read_text(encoding='utf8');edits=[]
 for n in nodes(text)[0]['children']:
  if kind(n)!='symbol':continue
  props={c['tokens'][1][0]:c for c in n['children'] if kind(c)=='property'}
  if 'Footprint' not in props:continue
  ref=props['Reference']['tokens'][2][0];fpnode=props['Footprint'];old,a,b=fpnode['tokens'][2];new=maps.get((fn,ref));raw=text[a:b]
  if fn=='Interface.kicad_sch' and '\\u' in raw:
   new=old;lib,name=new.split(':',1);assert (Path(lib+'.pretty')/(name+'.kicad_mod')).is_file()
  if new:
   edits.append((a,b,json.dumps(new,ensure_ascii=False)));logs.append({'sheet':fn,'ref':ref,'old':raw,'new':new})
 if edits:
  backup=Path('.review-fixes')/(fn+'.before-footprint');assert not backup.exists();shutil.copy2(p,backup)
  for a,b,new in sorted(edits,reverse=True):text=text[:a]+new+text[b:]
  p.write_text(text,encoding='utf8')
Path('.review-fixes/footprint-assignment-changes.json').write_text(json.dumps(logs,ensure_ascii=False,indent=2),encoding='utf8')
print('Changed instances',len(logs));print('Remaining unique refs',len({(x['sheet'],x['ref']) for x in unresolved}))
