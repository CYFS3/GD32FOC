from audit import *
import xml.etree.ElementTree as ET
sys.path.insert(0,str(W/'.pdf-review-tools'));import pymupdf
def netstate(p):
 r=ET.parse(p).getroot();return {n.attrib['name']:sorted((p.attrib['ref'],p.attrib['pin']) for p in n.findall('node')) for n in r.findall('nets/net')}
a=netstate(W/'label_wire_audit/before.xml');b=netstate(W/'label_wire_audit/after.xml');assert a==b
for f in W.glob('*.kicad_sch'):
 old=(W/'label_wire_audit/baseline'/f.name).read_text(encoding='utf-8');new=f.read_text(encoding='utf-8');ro,rn=parse(old),parse(new)
 assert sorted(pins(ro))==sorted(pins(rn))
 for kind in ['symbol','junction','no_connect','lib_symbols']:
  assert [old[n.start:n.end] for n in ro.kids(kind)]==[new[n.start:n.end] for n in rn.kids(kind)],(f,kind)
p=pymupdf.open(W/'label_wire_audit/GD32F5_FOC.pdf');print('pages',len(p))
for i,page in enumerate(p):
 if 'C130' in page.get_text():
  target=pymupdf.open();target.insert_pdf(p,from_page=i,to_page=i);target.save(W/'label_wire_audit/FOC_M1.pdf');target.close()
  crop=pymupdf.open();out=crop.new_page(width=1000,height=500);out.show_pdf_page(out.rect,p,i,clip=pymupdf.Rect(290*72/25.4,185*72/25.4,390*72/25.4,230*72/25.4));crop.save(W/'label_wire_audit/C130_bootstrap_focus.pdf');crop.close();break
changes=json.loads((W/'label_wire_audit/changes.json').read_text())
for c in changes:
 if c.get('new_at')==[128.98,106.2,180]:c['new_at']=[132.79,106.2,270]
 if c.get('new_at')==[167.08,126.52,90]:c['new_at']=[160.73,126.52,90]
(W/'label_wire_audit/changes.json').write_text(json.dumps(changes,indent=2),encoding='utf-8')
(W/'label_wire_audit/verification.json').write_text(json.dumps(dict(native_all_net_pinsets_identical=True,nets=len(a),all_physical_pin_coordinates_identical=True,all_symbols_junctions_libraries_identical=True,pdf_pages=len(p)),indent=2),encoding='utf-8')
print('PASS',len(a),'native net pinsets identical, all source physical pins/symbols/junctions/libraries unchanged')
