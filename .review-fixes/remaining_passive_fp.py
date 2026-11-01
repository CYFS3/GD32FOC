from pin_types import *
base=Path('D:/KiCad/HQ10.0/share/kicad/footprints')
s=(base/'LED_SMD.pretty/LED_0603_1608Metric.kicad_mod').read_text(encoding='utf8');s=s.replace('LED_0603_1608Metric','LED_0603_1608Metric_A1K2');s=re.sub(r'\(pad "([12])"',lambda m:'(pad "'+('2' if m[1]=='1' else '1')+'"',s)
p=Path('Interface.pretty/LED_0603_1608Metric_A1K2.kicad_mod');assert not p.exists();p.write_text(s,encoding='utf8')
logs=[]
for fn in ['FOC_M1.kicad_sch','FOC_M2.kicad_sch','power.kicad_sch']:
 p=Path(fn);text=p.read_text(encoding='utf8');edits=[];backup=Path('.review-fixes')/(fn+'.before-passive-footprint')
 if not backup.exists():shutil.copy2(p,backup)
 for n in nodes(text)[0]['children']:
  if kind(n)!='symbol':continue
  props={c['tokens'][1][0]:c for c in n['children'] if kind(c)=='property'};ref=props['Reference']['tokens'][2][0];sid=val(n,'lib_id');new=None
  if sid=='ProDoc_Boa-easyedapro:R2512_S':new='Resistor_SMD:R_2512_6332Metric'
  if ref in ['D4','D23','D24']:new='Diode_SMD:D_MiniMELF'
  if ref in ['L5','L7','L8']:new='Interface:LED_0603_1608Metric_A1K2'
  if new:
   if not new.startswith('Interface:'):
    lib,name=new.split(':');assert (base/(lib+'.pretty')/(name+'.kicad_mod')).is_file()
   old,a,b=props['Footprint']['tokens'][2];edits.append((a,b,json.dumps(new)));logs.append((fn,ref,new))
 for a,b,new in sorted(edits,reverse=True):text=text[:a]+new+text[b:]
 p.write_text(text,encoding='utf8')
Path('.review-fixes/passive-footprint-changes.json').write_text(json.dumps(logs,indent=2),encoding='utf8');print(logs)
