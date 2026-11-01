from pin_types import *
exec(Path('.review-gd32/crystal_work.py').read_text(encoding='utf8').split("s=P('MCU.kicad_sch')")[0])
s=parse(Path('FOC_M1.kicad_sch').read_text(encoding='utf8'))
for lib in children(one(s,'lib_symbols'),'symbol'):
 if lib[1].endswith('B5819WS_C305446'):
  for sub in children(lib,'symbol'):print(sub)
