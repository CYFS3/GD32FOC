from pathlib import Path as P
exec(P('.review-gd32/crystal_work.py').read_text(encoding='utf-8').split("s=P('MCU.kicad_sch')")[0])
def nets(file):
 t=parse(P(file).read_text(encoding='utf-8'));return {one(n,'name')[1]:{(one(x,'ref')[1],one(x,'pin')[1]) for x in children(n,'node')} for n in children(one(t,'nets'),'net')}
b=nets('.review-gd32/MCU.before.net');a=nets('.review-gd32/MCU.after.net')
expected=[{('U1','12'),('Y200','1'),('C210','1')},{('U1','13'),('Y200','3'),('C211','1')}]
for e in expected:assert e in a.values(),e
assert a['GND']==b['GND']|{('Y200','2'),('Y200','4'),('C210','2'),('C211','2')}
for name,nodes in b.items():
 if name in ['unconnected-(U1-OSCIN-PD0-Pad12)','unconnected-(U1-OSCOUT-PD1-Pad13)','GND']:continue
 assert a[name]==nodes,(name,nodes,a.get(name))
assert len(a)==len(b)
# All original AST objects preserved except two NC markers; libraries only extended.
before=parse(P('.review-gd32/MCU.before-crystal.kicad_sch').read_text(encoding='utf-8'));after=parse(P('.review-gd32/MCU.crystal-candidate.kicad_sch').read_text(encoding='utf-8'))
for n in before[1:]:
 if isinstance(n,list) and n[0]=='lib_symbols':
  assert all(x in one(after,'lib_symbols') for x in n[1:]);continue
 if isinstance(n,list) and n[0]=='no_connect' and one(n,'uuid')[1] in ['3ded7979-ccfb-4861-ae10-101262280fc0','e7087977-5886-4cce-8be4-5a5fcf4dec47']:continue
 assert n in after, n
print('PASS: exact HXTAL_IN = U1.12/Y200.1/C210.1')
print('PASS: exact HXTAL_OUT = U1.13/Y200.3/C211.1')
print('PASS: GND adds only Y200.2/Y200.4/C210.2/C211.2')
print('PASS: all other pre-existing nets and AST objects unchanged, except two removed OSC no-connect markers')
