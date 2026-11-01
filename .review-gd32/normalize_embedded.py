from pathlib import Path as P
exec(P('.review-gd32/apply_crystal.py').read_text(encoding='utf-8').split("f=P('MCU.kicad_sch')")[0])
lib=P('HXTAL.kicad_sym').read_text(encoding='utf-8').replace('(property "Value" ""','(property "Value" "ABM3B"',1);P('HXTAL.kicad_sym').write_text(lib,encoding='utf-8')
b=block(lib,lib.index('(symbol "ABM3B"')).replace('(symbol "ABM3B"','(symbol "HXTAL:ABM3B"',1)
s=P('MCU.kicad_sch').read_text(encoding='utf-8');old=block(s,s.index('(symbol "HXTAL:ABM3B"'));s=s.replace(old,b,1);P('MCU.kicad_sch').write_text(s,encoding='utf-8')
P('.review-gd32/MCU.crystal-candidate.kicad_sch').write_text(s,encoding='utf-8')
