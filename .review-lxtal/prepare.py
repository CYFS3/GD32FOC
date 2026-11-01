from pathlib import Path as P
import re
s=P('.review-lxtal/ABS07.kicad_sym').read_text()
s=s.replace('XTAL-2','ABS07').replace('(property "Value" ""','(property "Value" "ABS07"')
s=s.replace('(pin_numbers hide)','(pin_numbers (hide yes))').replace('(offset 1.016) hide)','(offset 1.016) (hide yes))')
P('LXTAL.kicad_sym').write_text(s,encoding='utf8')
s=P('.review-lxtal/ABS07.kicad_mod').read_text().replace('fbe5e0149b4949b49b76c04487a01796','ABS07_32.768kHz_3215',1)
P('VerifiedParts.pretty/ABS07_32.768kHz_3215.kicad_mod').write_text(s,encoding='utf8')
