from migrate_p2 import *
s,r=load(W/'HSLink.kicad_sch')
for n in r.items:
 if isinstance(n,Node) and n.key in ['symbol','global_label','text']:
  print(n.key,prop(n,'Reference') if n.key=='symbol' else n.items[1],prop(n,'Value') if n.key=='symbol' else '',n.one('at').items[1:])
