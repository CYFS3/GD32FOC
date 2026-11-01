import pathlib,re,json,uuid,shutil,hashlib
P=pathlib.Path
# Parser definitions only, no analysis side effects.
exec(P('.review-gd32/crystal_work.py').read_text(encoding='utf-8').split("s=P('MCU.kicad_sch')")[0])
def uid():return str(uuid.uuid4())
def block(text,start):
 depth=0; quoted=False; esc=False
 for i in range(start,len(text)):
  c=text[i]
  if quoted:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':quoted=False
  elif c=='"':quoted=True
  elif c=='(':depth+=1
  elif c==')':
   depth-=1
   if depth==0:return text[start:i+1]
 raise ValueError('unclosed')
f=P('MCU.kicad_sch'); raw=f.read_bytes(); s=raw.decode('utf-8'); before=parse(s)
bak=P('.review-gd32/MCU.before-crystal.kicad_sch')
if not bak.exists():shutil.copy2(f,bak)
else:assert bak.read_bytes()==raw
# Preserve all original text except the two explicit unconnected markers.
for ident in ['3ded7979-ccfb-4861-ae10-101262280fc0','e7087977-5886-4cce-8be4-5a5fcf4dec47']:
 pos=s.index(ident); start=s.rfind('(no_connect',0,pos); b=block(s,start); assert ident in b; s=s[:start]+s[start:].replace(b,'',1)
for path,name,newname in [('.review-gd32/ABM3B.kicad_sym','XTAL-2G4G-4','HXTAL:ABM3B'),(r'D:\KiCad\HQ10.0\share\kicad\symbols\power.kicad_sym','GND','power:GND')]:
 txt=P(path).read_text(encoding='utf-8'); st=txt.index('(symbol "'+name+'"'); b=block(txt,st).replace('(symbol "'+name+'"','(symbol "'+newname+'"',1)
 b=b.replace('"'+name+'_','"'+newname.split(':')[1]+'_')
 b=b.replace('(offset 1.016) hide)', '(offset 1.016) (hide yes))')
 p=s.index('(lib_symbols')+len('(lib_symbols');s=s[:p]+'\n'+b+s[p:]
inst='/df410b35-b24b-4f8c-aaa2-f94e7558172b/023525dc-8b31-4272-8a5f-3c0381bf9655'
add=[]
def prop(k,v,x,y,hide=False):return f'(property {json.dumps(k)} {json.dumps(v)} (at {x} {y} 0)'+(' (hide yes)' if hide else '')+' (effects (font (size 1 1))))'
def sym(lib,ref,val,x,y,pins,fp='',refxy=None,valxy=None,extra=''):
 refxy=refxy or (x+5,y-2);valxy=valxy or (x+7,y+2)
 t=f'(symbol (lib_id "{lib}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid()}")'
 t+=prop('Reference',ref,*refxy,hide=ref.startswith('#'))+prop('Value',val,*valxy)+prop('Footprint',fp,x,y,True)+extra
 t+=''.join(f'(pin "{p}" (uuid "{uid()}"))' for p in pins)
 t+=f'(instances (project "GD32F5_FOC" (path "{inst}" (reference "{ref}") (unit 1)))))';add.append(t)
def wire(x,y,a,b):add.append(f'(wire (pts (xy {x} {y}) (xy {a} {b})) (stroke (width 0) (type default)) (uuid "{uid()}"))')
def label(name,x,y,rot=0):add.append(f'(label "{name}" (at {x} {y} {rot}) (effects (font (size 1 1)) (justify left bottom)) (uuid "{uid()}"))')
def gnd(ref,x,y):sym('power:GND',ref,'GND',x,y,['1'],refxy=(x,y),valxy=(x,y+3.81))
def text(t,x,y):add.append(f'(text {json.dumps(t)} (at {x} {y} 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid()}"))')
refs={p[2] for n in children(before,'symbol') for p in children(n,'property') if p[1]=='Reference'}
newrefs={'Y200','C210','C211','#PWR9037','#PWR9038','#PWR9039','#PWR9040'};assert not refs&newrefs
wire(55.88,121.92,48.26,121.92);label('HXTAL_IN',48.26,121.92)
wire(55.88,124.46,48.26,124.46);label('HXTAL_OUT',48.26,124.46)
sym('HXTAL:ABM3B','Y200','8MHz',190.5,220.98,['1','2','3','4'],'HXTAL:ABM3B_5x3.2mm',refxy=(201.93,212.09),valxy=(201.93,214.63),extra=prop('MPN','ABM3B-8.000MHZ-10-D-1-G-T',190.5,220.98,True)+prop('Manufacturer','Abracon',190.5,220.98,True)+prop('Datasheet','https://file.elecfans.com/web2/M00/29/79/poYBAGHF2VCATwTTABRNCuI7RRw751.pdf',190.5,220.98,True))
for ref,x in [('C210',175.26),('C211',205.74)]:
 sym('Device:C',ref,'12pF C0G',x,231.14,['1','2'],'Capacitor_SMD:C_0603_1608Metric',refxy=(x+7.62,229.87),valxy=(x+7.62,232.41))
 wire(x,220.98,x,227.33);wire(x,234.95,x,237.49)
 gnd('#PWR9037' if ref=='C210' else '#PWR9038',x,237.49)
wire(175.26,220.98,186.69,220.98);wire(194.31,220.98,205.74,220.98)
label('HXTAL_IN',175.26,220.98);label('HXTAL_OUT',205.74,220.98)
# The two case ground pins are distinct from the resonator pins.
wire(190.5,215.9,182.88,215.9);gnd('#PWR9039',182.88,215.9)
wire(190.5,226.06,190.5,237.49);gnd('#PWR9040',190.5,237.49)
text('HXTAL: 8MHz design choice; Y200 = ABM3B-8.000MHZ-10-D-1-G-T',155,251.46)
text('CL=10pF; C210=C211=2*(CL-Cs)=12pF initially, assuming Cs=4pF.',155,255.27)
text('Verify Cs, startup margin and drive level on PCB; tune capacitors. Internal Rf=400k.',155,259.08)
s=s[:s.rfind(')')]+'\n'+'\n'.join(add)+'\n'+s[s.rfind(')'):]
# Stage candidate; main-file replacement occurs only after netlist and concurrency checks.
P('.review-gd32/MCU.crystal-candidate.kicad_sch').write_text(s,encoding='utf-8')
P('.review-gd32/crystal-original.sha256').write_text(hashlib.sha256(raw).hexdigest())
print('Candidate staged; original backup SHA256',hashlib.sha256(raw).hexdigest())
