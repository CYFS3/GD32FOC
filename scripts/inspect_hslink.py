from migrate_p2 import *
S=W.parent/'HPM'
for f in [S/'4_DAP.kicad_sch',S/'2_USB.kicad_sch',S/'3_POWER.kicad_sch',S/'ProDoc_IPB-TINY_2026-10-26.kicad_sch', W/'GD32F5_FOC.kicad_sch',W/'MCU.kicad_sch']:
 s,r=load(f);print('\nFILE',f.name,'UUID',r.val('uuid'))
 for n in r.kids('symbol'):
  print('SYM',prop(n,'Reference'),prop(n,'Value'),n.val('lib_id'),n.one('at').items[1:])
 for k in ['label','global_label','hierarchical_label','text','sheet']:
  for n in r.kids(k):print(k,n.items[1] if k not in ['sheet'] else [(x.items[1:3]) for x in n.kids('property')],n.one('at').items[1:] if n.one('at') else '')
