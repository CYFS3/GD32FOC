from kipy import KiCad
import inspect,json
k=KiCad();assert k.check_version();b=k.get_board();fs=b.get_footprints();f=fs[0]
print('BOARD',b.name if hasattr(b,'name') else str(b))
for o in [b,f,b.get_pads()[0]]:print(type(o),[a for a in dir(o) if not a.startswith('_')])
print(inspect.signature(b.get_item_bounding_box));bb=b.get_item_bounding_box(fs[:1]);print(bb, type(bb[0]),[a for a in dir(bb[0]) if not a.startswith('_')])
print('pad',b.get_pads()[0].position,b.get_pads()[0].net)
print('group keys',json.load(open('.layout-review/placement-groups.json')).keys())
