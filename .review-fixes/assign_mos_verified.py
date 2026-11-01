from pin_types import *
exec(Path('.review-gd32/crystal_work.py').read_text(encoding='utf8').split("s=P('MCU.kicad_sch')")[0])
for fn in ['FOC_M1.kicad_sch','FOC_M2.kicad_sch']:
 p=Path(fn);text=p.read_text(encoding='utf8');s=parse(text);lib=next(x for x in children(one(s,'lib_symbols'),'symbol') if x[1]=='ProDoc_Boa-easyedapro:KCD3008A');pins={one(p,'number')[1]:one(p,'name')[1] for sub in children(lib,'symbol') for p in children(sub,'pin')};assert pins=={'1':'G','2':'D','3':'S'}
 backup=Path('.review-fixes')/(fn+'.before-verified-mos');assert not backup.exists();shutil.copy2(p,backup);edits=[]
 for n in nodes(text)[0]['children']:
  if kind(n)!='symbol' or val(n,'lib_id')!='ProDoc_Boa-easyedapro:KCD3008A':continue
  props={c['tokens'][1][0]:c for c in n['children'] if kind(c)=='property'};old,a,b=props['Footprint']['tokens'][2];edits.append((a,b,json.dumps('VerifiedParts:NCE7560K')))
 for a,b,new in sorted(edits,reverse=True):text=text[:a]+new+text[b:]
 p.write_text(text,encoding='utf8');print(fn,len(edits))
