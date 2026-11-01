from pathlib import Path as P
import hashlib,shutil
expected=P('.review-gd32/crystal-original.sha256').read_text()
assert hashlib.sha256(P('MCU.kicad_sch').read_bytes()).hexdigest()==expected,'Disk changed: do not overwrite'
P('HXTAL.pretty').mkdir(exist_ok=True)
f=P('HXTAL.pretty/ABM3B_5x3.2mm.kicad_mod');assert not f.exists()
s=P('.review-gd32/ABM3B.kicad_mod').read_text();s=s.replace('"1b3087ab6cf54ca48676ad50b01280c8"','"ABM3B_5x3.2mm"',1);f.write_text(s,encoding='utf-8')
shutil.copy2('.review-gd32/MCU.crystal-candidate.kicad_sch','MCU.kicad_sch')
print('Committed verified candidate; imported HQ part footprint without geometry changes.')
