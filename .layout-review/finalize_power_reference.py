from pathlib import Path
exec(Path('.layout-review/map_power_reference.py').read_text(encoding='utf8').split('for r in mp:print')[0])
w=load('.layout-review/power-map-working.json');mp=w['map'];pm=w['pinmaps'];ev=w['evidence']
manual={**{f'C{151+i}':f'C{5+i}' for i in range(11)},'C162':'C16','C163':'C17','C164':'C3','C165':'C4','R134':'R10','R136':'R11','R41':'R23','R42':'R24','C71':'C27','C72':'C28','C73':'C39','C137':'C58','C138':'C59','C139':'C60','C168':'C38','C170':'C37','C19':'C30','C166':'C44','C167':'C45','C171':'C106','L9':'L7','R155':'R36','CN16':'CN16','R48':'R46','R57':'R57','C2':'C36','C3':'C32','C5':'C41','C6':'C42'}
assert set(manual)==set(w['unmatched'])
# Per-net mapping for regulator 5V before original 0-ohm distribution, now consolidated;
# reference resistor-divider node is separate from opamp input by R54; current removed that jumper.
alias={'5V':{'5V','$1N958663'},'Net-(U12-IN+)':{'$1N858763','$1N752227'}}
for r,s in manual.items():
 mp[r]=s; a=cn[r];b=sn[s];best=None
 for swap in [False,True] if set(a)=={'1','2'} and set(b)=={'1','2'} else [False]:
  pp={p:('2' if p=='1' else '1') if swap else p for p in a};yes=0;bad=[]
  for pin,n in a.items():
   target=b.get(pp[pin]);allowed=alias.get(n,{w['netmap'].get(n,n)})
   if target in allowed:yes+=1
   elif not n.startswith('unconnected'):bad.append((pin,n,target))
  rank=(len(bad),-yes)
  if best is None or rank<best[0]:best=(rank,pp,bad)
 pm[r]=best[1];assert not best[2],(r,s,best)
 ev[r]='Manual functional-region mapping with every connected pin network checked; electrically parallel repeated passives use deterministic source order, not uniquely inferable identity'
assert len(mp)==len(refs)==97 and len(set(mp.values()))==97
rows=[]
for r in refs:
 s=mp[r];f=S[s];diff=[]
 if r=='CN1':diff+=['Current XT30PW-M30.G.Y male vs reference XT30PW-F female; preserve functional anchor and orient by actual pin1 DCBUS_IN/pin2 PGND_IN, extra current pins3/4 no reference mapping; physical polarity remains verification item.']
 if r=='U19':diff+=['Current Value=RY8411 but MPN=JW5026; source RY8411. Mapping uses schematic pin functions/topology, not proof of exact BOM identity.']
 if C[r]['value']!=f['value']:diff+=[f"Value changed: current {C[r]['value']}, source {f['value']}; geometry may differ."]
 if r in ['C166','C167','C171','L9','R155']:diff+=['Reference regulated 5V local net $1N958663 joins 5V through R27; current schematic consolidates to 5V. Retain source buck-local geometry, do not invent R27.']
 if r in ['R48','R57','CN16']:diff+=['Reference divider node $1N752227 reaches opamp input through R54 0ohm; current joins directly. Do not copy removed R54/DAC branch.']
 if r.startswith('CN') and r!='CN1':diff+=['Current 5012 real PTH test post may be larger than source imported test pad; check both copper sides/courtyard before exact reuse.']
 diff+=['Use current real pad centers for rigid origin/rotation alignment; source angle alone is insufficient if current footprint differs.']
 rows.append(dict(source_ref=s,current_ref=r,group=C[r]['group'],source_pos_mm=f['at'][:2],source_angle_deg=f['rotation_deg'],source_layer=f['layer'],source_pads=f['pads'],source_value=f['value'],source_footprint=f['footprint'],current_value=C[r]['value'],current_mpn=C[r]['mpn'],current_footprint=C[r]['footprint'],current_to_source_pin_map={p:q for p,q in pm[r].items() if q in sn[s]},current_pin_nets=cn[r],evidence=ev[r],current_expected_diff=diff))
keyrefs=['CN3','Q1','Q2','Q3','C3','C4','U2','U5','U3','U4','U6','Q5','Q6','Q7','Q8','Q9','Q10','U7']
anchors={s:dict(position_mm=S[s]['at'][:2],angle_deg=S[s]['rotation_deg'],layer=S[s]['layer'],value=S[s]['value']) for s in keyrefs}
xs=[r['source_pos_mm'][0] for r in rows];ys=[r['source_pos_mm'][1] for r in rows]
out=dict(status='read_only_mapping_plan_no_board_change',counts=dict(power_page=sum(C[r]['sheet']=='/POWER_SHARED/' for r in refs),mcu_power=sum(C[r]['sheet']=='/MCU/' for r in refs),total=97,mapped=97),rows=rows,anchors=anchors,source_power_center_bounds_mm=[min(xs),min(ys),max(xs),max(ys)],source_board_bounds_mm=[99.1235,79.8475,199.1235,134.8475],placement_plan=dict(common_transform='For every shared-power item and M1 source-mapped item apply the SAME board-origin translation T=(target_x-99.1235,target_y-79.8475), then model-specific rigid pad-origin/rotation correction. Do not assign power a separate downshift.',M2='Copy only full current FOC module below M1 with dx=0,dy=actual M1 full envelope height+8mm. Current module needs approximately78.5mm pitch because TP/new peripherals; nominal55mm+margin only if true full-module clearance verified.',shared_power='Exactly one input/protection/DCbus/buck/LDO/reference set, never duplicate for M2.',control='GD32/HSLink/display do not inherit STM32 coordinates. Repack these groups into free left/lower regions around M2, preserving internal clusters; eliminate global208 downshift and do not treat283mm workspace as board outline.',envelope='Source power+M1 uses original100x55mm relationships; two-module work envelope roughly100x(55+actual_pitch)mm before new control/HSLink clearance. Not a board size commitment.'),source_no_copy=['STM32 U1 and its clock/decoupling','reference R27 local5V bridge when absent current','reference R54/DAC selection branch when absent current','all copper/tracks/vias/board outline/layer stack'])
Path('.layout-review/power-reference-map.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(out['counts'],out['source_power_center_bounds_mm']);print(json.dumps(anchors,ensure_ascii=False,indent=2))
