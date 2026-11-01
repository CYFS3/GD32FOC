from pathlib import Path as P
import json,uuid,shutil
exec(P('.review-gd32/apply_crystal.py').read_text(encoding='utf8').split("f=P('MCU.kicad_sch')")[0])
f=P('MCU.kicad_sch');s=f.read_text(encoding='utf8');shutil.copy2(f,'.review-fixes/MCU.before-flags.kicad_sch')
lib=P(r'D:\KiCad\HQ10.0\share\kicad\symbols\power.kicad_sym').read_text(encoding='utf8');b=block(lib,lib.index('(symbol "PWR_FLAG"')).replace('(symbol "PWR_FLAG"','(symbol "power:PWR_FLAG"',1)
pos=s.index('(lib_symbols')+len('(lib_symbols');s=s[:pos]+'\n'+b+s[pos:]
inst='/df410b35-b24b-4f8c-aaa2-f94e7558172b/023525dc-8b31-4272-8a5f-3c0381bf9655';add=[]
for i,(net,x) in enumerate([('5V',254),('GND',279.4),('AGND',304.8),('MCU_VDDA',330.2)],200):
 ref=f'#FLG{i}';assert not any(ref in p.read_text(encoding='utf8') for p in P('.').glob('*.kicad_sch'))
 y=30.48
 add.append(f'(symbol (lib_id "power:PWR_FLAG") (at {x} {y} 0) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid "{uid()}") (property "Reference" "{ref}" (at {x} {y} 0) (hide yes) (effects (font (size 1 1)))) (property "Value" "PWR_FLAG" (at {x} {y-5.08} 0) (effects (font (size 1 1)))) (pin "1" (uuid "{uid()}")) (instances (project "GD32F5_FOC" (path "{inst}" (reference "{ref}") (unit 1)))))')
 add.append(f'(global_label "{net}" (shape input) (at {x} {y} 0) (effects (font (size 1 1)) (justify left)) (uuid "{uid()}"))')
text='ERC supply declarations (not extra regulators):\\n5V: U19.SW -> L9; GND: supply return;\\nAGND: R3 to GND; MCU_VDDA: R203 to VCC.'
add.append(f'(text "{text}" (at 245 39.37 0) (effects (font (size 1 1)) (justify left top)) (uuid "{uid()}"))')
s=s[:s.rfind(')')]+'\n'+'\n'.join(add)+'\n'+s[s.rfind(')'):];f.write_text(s,encoding='utf8')
