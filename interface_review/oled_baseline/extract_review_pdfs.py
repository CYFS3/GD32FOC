import sys
sys.path.insert(0,'.pdf-review-tools')
from pypdf import PdfReader
from pathlib import Path
base=Path(r'C:\Users\RTT\.hq-edge\1.8.12\dsh-home\kicad\attachments\v1\files')
items=[('26/26e07a1bdb5180a4b99abadb8ae3825949eb25581aa4adbc1a15383aea90f523/GD32F505xx_Datasheet_Rev0.9RC5.pdf','datasheet'),('b1/b1b0d2004baf5a6e123c85f504f3d219262a4080cad060f874634e3ccf31d44a/GD32F50x_用户手册_Rev1.4.pdf','manual'),('03/036734d0ebab88fbfd3a876c6c55729f57f7a51286339acb4229c0b5298c52ec/GD32F50x芯片使用限制_Rev1.1.pdf','errata')]
Path('review').mkdir(exist_ok=True)
for src,name in items:
 r=PdfReader(base/src)
 text='\n'.join(f'\n=== PDF PAGE {i+1} ===\n'+p.extract_text(extraction_mode='layout') for i,p in enumerate(r.pages))
 Path(f'review/{name}.txt').write_text(text,encoding='utf8')
 print(name,len(r.pages),len(text))
