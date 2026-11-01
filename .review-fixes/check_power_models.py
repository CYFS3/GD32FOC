from pathlib import Path as P
exec(P('.review-gd32/crystal_work.py').read_text(encoding='utf8').split("s=P('MCU.kicad_sch')")[0])
s=parse(P('power.kicad_sch').read_text(encoding='utf8'));lib=one(s,'lib_symbols')
for sym in children(lib,'symbol'):
 if any(x in sym[1] for x in ['WSD80120','WSD90P06','VKME']):
  print(sym[1])
  for unit in children(sym,'symbol'):
   for pin in children(unit,'pin'):print(one(pin,'number')[1],one(pin,'name')[1])
