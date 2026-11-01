from pathlib import Path
import json
from kipy import KiCad
k=KiCad();assert k.check_version();b=k.get_board();ps=b.get_pads();d={p.id.value:dict(type=p.pad_type,layers=list(p.padstack.layers)) for p in ps};Path('.layout-review/module-pad-layers.json').write_text(json.dumps(d));print(len(d))
