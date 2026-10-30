from migrate_p2 import *
for file in ['MCU.kicad_sch','FOC_M1.kicad_sch','FOC_M2.kicad_sch']:
 s,r=load(W/file);ops=[]
 for n in r.kids('global_label'):
  old=n.items[1];new=old
  for i in (1,2):
   for a,b in [('QEI1_A','HALL_A'),('QEI1_B','HALL_B'),('QEI1_Z','HALL_C'),('VS1','MA'),('VS2','MB'),('VS3','MC')]:
    if old==f'M{i}_{a}':new=f'M{i}_{b}'
  if new!=old:ops.append((n.start,n.end,s[n.start:n.end].replace(json.dumps(old),json.dumps(new),1)))
 (W/file).write_text(patches(s,ops),encoding='utf-8')
print('Canonical Hall and phase labels normalized.')
