from pathlib import Path as P
import uuid,json,re
exec(P('.review-gd32/crystal_work.py').read_text(encoding='utf8').split("s=P('MCU.kicad_sch')")[0])
exec(P('.review-gd32/apply_crystal.py').read_text(encoding='utf8').split("f=P('MCU.kicad_sch')")[0].split('def uid():')[1].join(['def uid():','']) if False else P('.review-gd32/apply_crystal.py').read_text(encoding='utf8').split("f=P('MCU.kicad_sch')")[0])
s=P('MCU.kicad_sch').read_text(encoding='utf8'); before=parse(s)
refs=set()
for f in P('.').glob('*.kicad_sch'):
 for n in children(parse(f.read_text(encoding='utf8')),'symbol'):
  refs.update(p[2] for p in children(n,'property') if p[1]=='Reference')
assert not refs & {'Y201','C214','C215','#PWR9800','#PWR9801'}
for ident in ['84fad719-3d67-4037-b605-f98eb77778a4','a59cf5da-c912-466b-a931-4b7d41c3b983']:
 pos=s.index(ident);start=s.rfind('(no_connect',0,pos);b=block(s,start);s=s.replace(b,'',1)
lib=P('LXTAL.kicad_sym').read_text(encoding='utf8');b=block(lib,lib.index('(symbol "ABS07"')).replace('(symbol "ABS07"','(symbol "LXTAL:ABS07"',1)
pos=s.index('(lib_symbols')+len('(lib_symbols');s=s[:pos]+'\n'+b+s[pos:]
exec(P('.review-gd32/apply_crystal.py').read_text(encoding='utf8').split("inst='/df")[1].split('refs=')[0].join(["inst='/df",'']))
# Area x330..385,y120..175 is empty according to placed-symbol/wire coordinate inspection.
wire(116.84,68.58,124.46,68.58);label('LXTAL_IN',124.46,68.58)
wire(116.84,71.12,124.46,71.12);label('LXTAL_OUT',124.46,71.12)
sym('LXTAL:ABS07','Y201','32.768kHz',350.52,121.92,['1','2'],'VerifiedParts:ABS07_32.768kHz_3215',refxy=(350.52,114.3),valxy=(350.52,116.84),extra=prop('MPN','ABS07-32.768KHZ-9-T',350.52,121.92,True)+prop('Manufacturer','Abracon',350.52,121.92,True)+prop('Datasheet','https://file.elecfans.com/web2/M00/29/C4/poYBAGHGUeWAAXgaAEdA-9wBNxg447.pdf',350.52,121.92,True))
for ref,x,pr in [('C214',335.28,'#PWR9800'),('C215',365.76,'#PWR9801')]:
 sym('Device:C',ref,'12pF C0G',x,132.08,['1','2'],'Capacitor_SMD:C_0603_1608Metric',refxy=(x+6.35,129.54),valxy=(x+6.35,133.35))
 wire(x,121.92,x,128.27);wire(x,135.89,x,140.97);gnd(pr,x,140.97)
wire(335.28,121.92,346.71,121.92);wire(354.33,121.92,365.76,121.92)
label('LXTAL_IN',335.28,121.92);label('LXTAL_OUT',365.76,121.92)
for i,t in enumerate(['LXTAL Y201: ABS07-32.768KHZ-9-T','CL=9pF; ESR<=70k; C214/C215=12pF C0G','C=2*(CL-Cs), Cs=3pF assumed; tune on PCB.','Enable backup writes (BKPWEN), crystal mode BPS=0.','Select LXTALDRI by startup/drive validation.','Enable LXTAL; wait LXTALSTB before selecting RTC.','Typical startup 2s is NOT a guaranteed timeout.','VBAT tied to VCC: no battery-backed timekeeping.']):text(t,322.58,152.4+i*3.81)
s=s[:s.rfind(')')]+'\n'+'\n'.join(add)+'\n'+s[s.rfind(')'):]
P('MCU.kicad_sch').write_text(s,encoding='utf8')
print('Added Y201 C214 C215 and ground; removed only two LXTAL NC markers')
