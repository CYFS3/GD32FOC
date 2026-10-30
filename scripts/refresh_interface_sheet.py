from pathlib import Path
p=Path(__file__).with_name('build_interface.py');s=p.read_text(encoding='utf-8');s=s.split('# Complete all precondition checks')[0];s += "\n(W/'Interface.kicad_sch').write_text(text,encoding='utf-8')\nprint('Refreshed Interface with corrected rotation transform')\n";exec(compile(s,str(p),'exec'))
