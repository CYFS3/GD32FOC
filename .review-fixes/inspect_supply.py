from pathlib import Path as P
exec(P('.review-gd32/crystal_work.py').read_text().split("s=P('MCU.kicad_sch')")[0])
t=parse(P('.review-fixes/mcu-supply-project.net').read_text(encoding='utf8'))
for n in children(one(t,'nets'),'net'):
 refs=[(one(x,'ref')[1],one(x,'pin')[1]) for x in children(n,'node')]
 if one(n,'name')[1] in ['5V','GND','AGND','MCU_VDDA'] or any(x[0] in ['U19','L7'] for x in refs):
  print(one(n,'name')[1], [x for x in refs if x[0] in ['U19','L7','R3','R203','U1','U20','U2'] or x[0].startswith(('J','CN','L'))])
