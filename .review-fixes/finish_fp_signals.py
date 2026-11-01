from pin_types import *
import uuid
# Safe token-only footprint additions and signal-marker replacements.
logs=[]
for fn in ['FOC_M1.kicad_sch','FOC_M2.kicad_sch']:
 p=Path(fn);text=p.read_text(encoding='utf8');edits=[]
 backup=Path('.review-fixes')/(fn+'.before-signal-label');
 if not backup.exists():shutil.copy2(p,backup)
 for n in nodes(text)[0]['children']:
  if kind(n)!='symbol':continue
  props={c['tokens'][1][0]:c for c in n['children'] if kind(c)=='property'}
  ref=props['Reference']['tokens'][2][0];value=props['Value']['tokens'][2][0]
  if ref in ['D8','D9','D10','D1008','D1009','D1010']:
   old,a,b=props['Footprint']['tokens'][2];new='Diode_SMD:D_SOD-323';edits.append((a,b,json.dumps(new)));logs.append((fn,ref,old,new))
  if ref.startswith('#PWR') and re.fullmatch(r'M[12]_(?:V[ABC]|M[ABC])',value):
   at=next(c for c in n['children'] if kind(c)=='at');x,y=at['tokens'][1][0],at['tokens'][2][0];uid=val(n,'uuid')
   replacement=f'(global_label "{value}" (shape bidirectional) (at {x} {y} 0) (effects (font (size 1.0 1.0)) (justify left)) (uuid "{uid}"))'
   edits.append((n['start'],n['end'],replacement));logs.append((fn,ref,value,'global_label'))
 for a,b,new in sorted(edits,reverse=True):text=text[:a]+new+text[b:]
 p.write_text(text,encoding='utf8')
Path('.review-fixes/diode-signal-changes.json').write_text(json.dumps(logs,ensure_ascii=False,indent=2),encoding='utf8');print(logs)
