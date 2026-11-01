from pathlib import Path as P
exec(P('.review-gd32/apply_crystal.py').read_text(encoding='utf8').split("f=P('MCU.kicad_sch')")[0])
s=P('MCU.kicad_sch').read_text(encoding='utf8');t=parse(s)
import sys,shutil,json
sys.path.insert(0,str(P('.review-fixes').resolve()))
from pin_types import patch
s,changes=patch(s)
P('MCU.kicad_sch').write_text(s,encoding='utf8')
name='LP5907QMFX-3.3Q1';start=s.index('(symbol "ProDoc_Boa-easyedapro:'+name+'"');b=block(s,start).replace('"ProDoc_Boa-easyedapro:'+name+'"','"'+name+'"',1)
source=P('ProDoc_Boa-easyedapro.kicad_sym');old=source.read_text(encoding='utf8');backup=P('.review-fixes/U2-source.before-cache-sync.kicad_sym');assert not backup.exists();shutil.copy2(source,backup)
st=old.index('(symbol "'+name+'"');ob=block(old,st);source.write_text(old[:st]+b+old[st+len(ob):],encoding='utf8')
P('.review-fixes/mcu-type-changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf8')
print('Patched MCU pin type count',len(changes),'and synchronized only U2 source symbol geometry')
