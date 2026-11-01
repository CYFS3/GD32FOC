from pathlib import Path as P
import json,re,xml.etree.ElementTree as E,collections,hashlib
exec(P('.review-gd32/crystal_work.py').read_text(encoding='utf8').split("s=P('MCU.kicad_sch')")[0])
source='.layout-review/annotation-final.xml'; root=E.parse(source)
parts={}
for c in root.findall('./components/comp'):
 ref=c.get('ref');parts[ref]={'ref':ref,'value':c.findtext('value'),'footprint':c.findtext('footprint'),'sheet':c.find('sheetpath').get('names'),'nets':[]}
for n in root.findall('./nets/net'):
 for p in n.findall('node'):
  if p.get('ref') in parts:parts[p.get('ref')]['nets'].append({'pin':p.get('pin'),'net':n.get('name')})
for f in ['MCU','power','FOC_M1','FOC_M2','HSLink','Interface']:
 s=parse(P(f+'.kicad_sch').read_text(encoding='utf8'))
 for x in children(s,'symbol'):
  props={p[1]:p[2] for p in children(x,'property')};ref=props.get('Reference')
  if ref in parts:
   parts[ref].update(value=props.get('Value'),footprint=props.get('Footprint'),mpn=props.get('MPN',props.get('Manufacturer Part')),dnp=one(x,'dnp')[1]=='yes' if one(x,'dnp') else False,source_schematic=f+'.kicad_sch')
groups={}
def group(id,rect,note):groups[id]={'id':id,'rect_mm':dict(zip(['x_min','y_min','x_max','y_max'],rect)),'notes':note,'refs':[]}
group('shared_input',[3,3,35,31],'DC input, protection, input bypass. CN1 left edge; orientation from actual mating mouth.')
group('shared_bulk',[3,33,35,48],'Bulk DC capacitors and shared ceramics; feed independent M1/M2 trunks, do not daisy-chain motor return through control.')
group('shared_buck12',[3,50,35,63],'U6/L6 compact switching loop; FB parts shielded from SW node.')
group('shared_buck5',[3,65,35,76],'U19/L9 compact local input/output capacitors.')
group('analog_reference',[39,63,62,74],'U12 low-noise reference distribution; keep away from buck and switching-node polygons.')
group('logic_ldo',[39,77,61,88],'U2 AVCC and U20 VCC; output capacitors at pins; R3 ground connection not a reason to cut a ground plane.')
group('mcu',[65,77,111,112],'LQFP100 including dedicated analog and digital decoupling; two crystals get local pin-based refinement.')
group('mcu_debug',[65,114,111,120],'Accessible J200/J201/TP200; rectangle may expand downward after actual connector bbox.')
group('hslink',[3,80,35,117],'USB west edge, ESD between connector and HPM. U8007 is an inductor, not IC.')
group('display_buttons',[114,79,136,117],'FPC bottom facing outward; three accessible buttons below/along bottom side.')
for ch,x in [(1,39),(2,105)]:
 group(f'm{ch}_power',[x,3,x+60,36],'Three high/low MOS phase cells, shunts, local DC capacitors, gate networks at MOS gates. Motor connector at north edge.')
 group(f'm{ch}_driver',[x,38,x+60,49],'FD6288, bootstraps, local 12V bypass, input pulldowns. Align driver output pads toward MOS gate cells.')
 group(f'm{ch}_sense',[x,51,x+60,61],'Current amplifier input/feedback clusters and voltage dividers; Kelvin paths from shunts; avoid SW copper.')
 group(f'm{ch}_encoder',[39 if ch==1 else 139,90 if ch==1 else 77,61 if ch==1 else 167,118],'Hall/encoder/SPI connectors, buffer, filtering, voltage-selection DNPs; outside noisy bridge.')
def assign(ref,g,why):
 assert ref in parts,ref
 assert 'group' not in parts[ref],ref
 parts[ref]['group']=g;parts[ref]['classification_basis']=why;groups[g]['refs'].append(ref)
def rr(prefix,nums):return [prefix+str(n) for n in nums]
# MCU sheet roles
for ref,p in parts.items():
 if p['sheet']=='/MCU/':
  if ref in ['U2','U20','C2','C3','C5','C6','CN2','CN3','CN6','R3']:g='logic_ldo'
  elif ref in ['J200','J201','TP200','R204','R205']:g='mcu_debug'
  else:g='mcu'
  assign(ref,g,'Current MCU page function and actual net names; not reference-board ref matching')
# Shared supply roles
sets={
 'analog_reference':set(['U12','C79','R48','R57','CN13','CN16']),
 'shared_buck12':set(['U6','L6','CN4','L5']+rr('C',[66,67,68,69,70,71,72,73,74,137,138,139])+rr('R',[40,41,42,43,44,45,46,47])),
 'shared_buck5':set(['U19','L9','CN7','L8']+rr('C',[19,166,167,168,169,170,171,172])+rr('R',[152,153,154,155])),
 'shared_bulk':set(rr('C',list(range(151,162))+[164,165])+['CN9','R134','R136','L7','R133'])}
for ref,p in parts.items():
 if p['sheet']=='/POWER_SHARED/':
  g=next((g for g,rs in sets.items() if ref in rs),'shared_input');assign(ref,g,'Power stage topology: input protection vs buck12/buck5 vs bulk/ref')
# Explicit symmetric functional clusters; remaining low-level signal nets classified via topology.
for ch,off in [(1,0),(2,1000)]:
 prefix=f'm{ch}_';sheet=f'/FOC_M{ch}/'
 driver=set([f'U{7+off}',f'C{143+off}']+rr('C',[130+off,131+off,132+off])+rr('D',[8+off,9+off,10+off])+rr('R',range(300+off,306+off)))
 enc=set([f'CN{5+off}',f'CN{47+off}',f'U{9100+ch}',f'C{9099+2*ch}',f'C{9100+2*ch}',f'R{9099+2*ch}',f'R{9100+2*ch}']+rr('C',[82+off,83+off,84+off,85+off])+rr('D',[14+off,19+off,20+off])+rr('R',[49+off,54+off,88+off,89+off,90+off,95+off,97+off,98+off,103+off,105+off,106+off,107+off,108+off,117+off,118+off,120+off,121+off]))
 power=set(rr('Q',range(5+off,11+off))+rr('R',[81+off,82+off,83+off,109+off,59+off,60+off,61+off,62+off,63+off,64+off,75+off,76+off,77+off,78+off,79+off,80+off])+rr('D',[5+off,6+off,7+off,11+off,12+off,13+off])+rr('C',list(range(96+off,105+off))+list(range(145+off,151+off)))+rr('CN',list(range(17+off,20+off))+list(range(22+off,31+off))+[35+off,36+off,41+off]))
 for ref,p in parts.items():
  if p['sheet']!=sheet:continue
  g=prefix+('driver' if ref in driver else 'encoder' if ref in enc else 'power' if ref in power else 'sense')
  assign(ref,g,'Explicit phase/gate/bootstrap/shunt/encoder membership checked against current nets; remaining ADC/divider/NTC chain to sense')
for ref,p in parts.items():
 if p['sheet']=='/HSL_DEBUGGER/':assign(ref,'hslink','HPM5301 debugger page; U8007 actual 4.7uH')
 elif p['sheet']=='/INTERFACE/':assign(ref,'display_buttons','OLED FPC and key interface current page')
assert all('group' in p for p in parts.values())
anchors={}
def anchor(ref,x,y,note,edge=None):
 assert ref in parts,ref
 anchors[ref]={'x_mm':x,'y_mm':y,'rotation_deg':None,'locked':False,'priority':'seed','note':note}
 if edge:anchors[ref]['edge_preference']=edge
anchor('CN1',7,16,'Use actual connector body/mating end, not center, to align west boundary. Verify polarity independently.','west')
for ref,x,y,n in [('Q1',21,12,'Input protection'),('Q3',21,23,'Return protection'),('C164',12,40,'Bulk can clearance includes courtyard'),('C165',25,40,'Bulk can clearance includes courtyard'),('U6',16,56,'12V buck'),('L6',26,56,'Keep SW loop short'),('U19',17,70,'5V buck'),('L9',25,70,'Keep SW loop short'),('U12',50,68,'Reference buffer'),('U2',46,82,'Analog LDO'),('U20',55,82,'Digital LDO'),('U1',88,94,'LQFP100 actual pin-based rotation; may rotate whole MCU cluster'),('Y200',77,88,'PROVISIONAL only: must move adjacent actual U1 pins12/13 after rotation'),('Y201',77,96,'PROVISIONAL only: must move adjacent actual U1 pins8/9 after rotation'),('J200',75,117,'Probe/header access'),('J201',98,117,'External fault inputs'),('TP200',85,115,'Reset probe access'),('U8006',22,96,'HPM local loop'),('D8005',13,96,'ESD directly behind USB data pins'),('X8002',26,104,'To actual HPM35/36'),('U8007',24,88,'Inductor near DCDC_LP15'),('H8001',25,113,'Debug header access'),('SW8005',9,111,'Accessible ISP button'),('FPC300',124,113,'Verify flex exit direction'),('SW300',117,99,'Button access'),('SW301',125,99,'Button access'),('SW302',133,99,'Button access')]:anchor(ref,x,y,n)
anchor('USB8002',7,96,'USB mouth west; ESD between mouth and HPM; verify actual pad/body rotation','west')
for ch,off,x in [(1,0,39),(2,1000,105)]:
 anchor(f'CN{41+off}',x+49,8,'Motor output north edge; check phase order and mating direction','north')
 for phase,dx in enumerate([10,27,44]):
  anchor(f'Q{5+off+phase}',x+dx,18,'High-side MOS; align power pad pair with corresponding low-side')
  anchor(f'Q{8+off+phase}',x+dx,29,'Low-side MOS; source toward shunt/Kelvin pickup')
  anchor(f'R{81+off+phase}',x+dx+7,31,'Phase shunt, refine to source pad; do not share sense with high current trunk')
 anchor(f'R{109+off}',x+54,33,'Common motor return shunt; no bypass through plane')
 anchor(f'U{7+off}',x+29,43,'Driver outputs face phase gates; bootstraps next to corresponding VB/VS')
 anchor(f'U{10+off}',x+30,56,'Four-channel current amplifier; cluster feedback, Kelvin pairs')
 anchor(f'NTC{1+off}',x+7,35,'Move to thermally relevant MOS region; not automatically beside analog group')
 ex=50 if ch==1 else 153; ey=102 if ch==1 else 90
 anchor(f'U{9100+ch}',ex,ey,'Encoder Schmitt buffer between connector and MCU')
 anchor(f'CN{5+off}',ex,116 if ch==1 else 115,'Encoder connector outward at south boundary','south')
 anchor(f'CN{47+off}',ex,94 if ch==1 else 80,'SPI encoder connector; actual mating exit needs checking')
# Attach constraints and parent-relative clusters instead of arbitrary small part coordinates.
clusters=[]
def cluster(id,refs,owner,note):clusters.append({'id':id,'refs':[r for r in refs if r in parts],'anchor_ref':owner,'placement_rule':note})
cluster('mcu_hxtal',['Y200','C210','C211'],'U1','Pin12/13 local island, shortest symmetric tracks; no switched copper beneath oscillator island')
cluster('mcu_lxtal',['Y201','C214','C215'],'U1','Pin8/9 local island, low leakage and short loop, no digital through-routing')
cluster('mcu_vdda',['C206','C207','R203'],'U1','At pin22 with quiet AGND return')
cluster('mcu_vref',['C208','C213'],'U1','At pin21/20 with quiet return')
cluster('mcu_vbat',['C212'],'U1','At pin6, independent short decoupling loop')
for cap,pin in zip(rr('C',range(200,205)),['11','28','50','75','100']):cluster('decouple_'+cap,[cap],'U1','At actual VDD pin'+pin+'; verify pad positions and permit nearest-equivalent cap permutation')
for ch,off in [(1,0),(2,1000)]:
 for i in range(3):
  cluster(f'm{ch}_bootstrap_{i+1}',[f'D{8+off+i}',f'C{130+off+i}'],f'U{7+off}','Place cap directly VB/VS pins, diode immediately at VB; avoid crossing phase currents')
  cluster(f'm{ch}_gate_hi_{i+1}',[f'R{59+off+i}',f'R{62+off+i}',f'D{5+off+i}',f'C{145+off+2*i}'],f'Q{5+off+i}','Gate resistor at MOS gate, gate-source return local; refine after pad geometry')
  cluster(f'm{ch}_gate_lo_{i+1}',[f'R{75+off+i}',f'R{78+off+i}',f'D{11+off+i}',f'C{146+off+2*i}'],f'Q{8+off+i}','Gate resistor at MOS gate, local source return')
 cluster(f'm{ch}_dc_ceramics',rr('C',range(96+off,105+off)),f'Q{5+off}','Distribute three caps per phase commutation cell rather than single remote row')
cluster('hslink_clock',['X8002','C8080','C8081','R8054'],'U8006','Use actual pins35/36, keep local and away from USB/DC-DC')
cluster('hslink_usb',['USB8002','D8005','R8056','R8057','R8060','C8087'],'USB8002','ESD before long DP/DN path; CC near connector; shield RC at shell return')
cluster('hslink_decoupling',rr('C',range(8064,8080))+rr('C',range(8082,8086)),'U8006','Assign by net AND individual supply pin, never blanket grid pack before local pins')
# Anchor overrides into group rectangles are intentional only for NTC thermal sensing.
plan={'schema_version':1,'kind':'placement_plan_only','source_netlist':source,'source_sha256':hashlib.sha256(P(source).read_bytes()).hexdigest(),'reference_report':'.layout-review/reference-layouts.md','coordinate_frame':{'units':'mm','origin':'arbitrary layout-envelope upper-left; translate as a whole to editor coordinates','x':'right','y':'down'},'soft_envelope_mm':{'width':170,'height':120,'is_board_outline':False,'rationale':'532 physical refs incl 52 through-hole 5012 testpoints, two discrete TO252 bridges and 2512 shunts, LQFP100 and HPM island; starting room for review, not thermal/current sizing'},'no_board_mutation':True,'board_stackup':None,'mounting_holes_added':False,'groups':groups,'ref_to_group':{r:p['group'] for r,p in parts.items()},'components':parts,'key_targets':anchors,'local_clusters':clusters,'packing_rules':['Use authoritative imported PCB footprint bbox/courtyard, not symbol position or model body dimensions.','Place key targets first; transform functional clusters together after selecting rotation from pad/net direction.','Targets are approximate seeds. No locked refs or mandatory rotation. Expand rectangles/envelope on bbox collision; do not shrink courtyard clearance to fit.','Group rects are available regions, not full-area keepouts. Cluster children may cross adjacent group borders when electrically justified.','Preserve DNP footprints, testpoint access and original nets. All 532 refs get an explicit group; no changes to population.','Top side first for review; no forced bottom-side assignment or fixed layer stack.','Keep switched-node copper/gate loops in y<50; analog current chain at y51..61, MCU at y77..112. Separation is functional, not certified creepage.','Allow approximately 1mm placement margin outside actual courtyard as an initial collision margin only; apply project electrical/edge clearance rules separately.','No PCB edges, holes, tracks, zones or routing are requested by this JSON.'],'validation':{'component_count':len(parts),'assigned_count':sum(len(g['refs']) for g in groups.values()),'unique_refs':len(set(parts)),'all_assigned':all('group' in p for p in parts.values()),'unassigned_refs':[],'pad_orientation_verified':False,'actual_pcb_bbox_used':False},'warnings':['Q1 may have newer source footprint than netlist; current schematic metadata overrides netlist footprint only, nets from netlist remain source.','CN1 polarity/mating and MR30/USB/FPC exit orientation require actual pad/body check before edge placement.','Reference FOC is single-channel LQFP64, not same MCU or dimensions.','HPM U8007 is 4.7uH; U10/U1010 each four units but only one physical package.','Testpoints are large physical 5012 parts, not zero-size symbols. Do not put all power testpoints in a distant common row.']}
P('.layout-review/placement-groups.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({g:len(d['refs']) for g,d in groups.items()},ensure_ascii=False));print('total',len(parts),'Q1',parts['Q1']['footprint'])
