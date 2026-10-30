# LCD and button implementation

Implemented in MCU.kicad_sch, Interface.kicad_sch and root sheet 7. No PCB modification. Baseline is interface_review/baseline.

| J300 pin | Net | MCU |
|---|---|---|
|1|VCC (3.3V)|board supply|
|2|GND|ground|
|3|LCD_SCK|PB3 pin 89, SPI0 AF2|
|4|LCD_MOSI|PA7 pin 32, SPI0 AF0|
|5|LCD_CS_N|PB6 pin 92 GPIO|
|6|LCD_DC|PB7 pin 93 GPIO|
|7|LCD_RST_N|PE4 pin 3 GPIO|
|8|LCD_BL_CTRL|PE5 pin 4 through R312 100R|

J300 uses verified installed KiCad PinHeader_1x08_P2.54mm_Vertical copied into Interface.pretty. This board-defined pin order is not automatic compatibility with any LCD module. Use a verified adapter for a 3.3V logic module. No MISO, SD, touch or readback. Release PB3 JTDO/TRACESWO for SPI0; preserve SWD on PA13/PA14. Existing motor SPI2 and debug signals unchanged by this implementation.

R310/R311 are 10k pull-ups on CS/RST. R312 is 100R in series between LCD_BL_GPIO and LCD_BL_CTRL; R313 100k pulls the connector side low. BL is only a logic enable/PWM control, never LED power. Module must supply its backlight driver and support active-high enable. PE5 may use GPIO or TIMER15_CH0 AF3. C300=100nF and C301=10uF/10V bypass VCC at the header. Module load is unknown: verify board regulator current/thermal budget and effective bulk capacitance before choosing the module.

SW300/SW301/SW302 use the exact reference SW5/SW6 PTS815SJK250SMTRLFS symbol/footprint. Pin1=GND, pin4=switch-side signal; pins2/3 NC as reference. Each switch drives PD2/PD3/PD4 through a 1k resistor, with a 10k 3.3V pull-up and 100nF to ground at the GPIO node. Active-low button behavior is intentional (the reference buttons were active-high). Pressed voltage is approximately 0.30V. Firmware debounce remains required.

R3 metadata corrected from stale 10k MPN to Royal Electronic Factory 0402WGF0000TCE, 0R 0402 1/16W, HQ catalog HQG0063276 as verified by parent catalog research. Removed stale LCSC supplier/part and old datasheet. Exact symbol pin geometry, UUID, placement, footprint and connectivity preserved; corrected local definition is Interface.kicad_sym.

Native kicad-cli netlist verifies all 13 new signal-node sets and new supply/ground nodes. The first stage before concurrent FOC changes preserved every original net partition except nine formerly NC MCU pins. The corrected final interface-stage export includes parallel encoder modifications, so whole-project net preservation comparison is explicitly false until scoped to those authorized FOC edits. All new interface nets pass exact assertions in scripts/verify_interface.py. Initial rotated-series resistor mapping was corrected and reverified before delivery.

PDF: interface_stage.pdf (7 sheets). PNG pages 2 and 7 generated for parent visual review; this agent's model has no image input and could not inspect them. Final whole-project ERC, exports and visual approval belong to the parent after parallel FOC changes settle.
