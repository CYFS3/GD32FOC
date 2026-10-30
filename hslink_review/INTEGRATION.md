# Onboard reference debugger integration

Current project schematics and local symbol/footprint libraries were backed up first in `hslink_backup_20261026_155454`.

`HSLink.kicad_sch` imports the complete HPM `4_DAP.kicad_sch` debugger (HPM5301IEG1), USB-C interface, protection and CH213K power path, plus the TPS563201DDCR 5 V to 3.3 V source supply subcircuit from `3_POWER.kicad_sch`. The HPM main controller, EtherCAT and USB1 circuits are not imported. Reference files and PCB files were not modified. Source components use original designators +8000. `reference_map.json` records exact translation.

All debugger power rails are HSL-prefixed, except common GND and the explicitly passive target VCC reference at H8001 pin1. USB VBUS -> CH213K -> HSL_5V -> reference buck/filter -> HSL_3V3 -> R8052 -> HSL_LINK_3V3. Motor 5V/VCC are not supply sources for the debugger. H8001 pin1 is target VCC reference only; no ADC voltage sensing or automatic firmware voltage detection was established. Header pullups remain debugger powered, on the debugger side of disconnect links.

| Default-DNP link | Connection |
|---|---|
| R8901 | debugger TMS via original22R -> GD32 SWDIO U1.72 |
| R8902 | debugger TCK via original22R -> GD32 SWCLK U1.76 |
| R8903 | debugger SRST via original22R -> GD32 NRST U1.14 |
| R8904 | debugger RX via original22R <- GD32 PD5 USART1_TX AF0 U1.86 |
| R8905 | debugger TX via original22R -> GD32 PD6 USART1_RX AF0 U1.87 |

The five 0-ohm links are explicitly DNP/default open. To enable debug/UART, solder the corresponding links only with the target supply present. Remove them for target-unpowered use or external J200 probe operation. Never use simultaneous probes. These links require manual assembly changes; no automatic backfeed protection is claimed. With links fitted, direct GPIO connections can backfeed an unpowered target. H8001 is debugger-side and is not a replacement target header; its pin10 remains TRST, not NRST.

The source PA27/PB11 clock pairing, PA26/PB10 pairing, and PA29/PA28 22-ohm path are preserved. Source ISP boot button/UART labels remain available. No firmware was flashed, fetched or tested; exact compatible HPM5301 firmware and GPIO mapping must be verified before operation. The page is named HSLink for the requested integration, but verified evidence establishes HPM5301 reference debugger hardware only.

Validation:

- Native KiCad CLI XML netlist: `after.xml`.
- Native six-page PDF: `GD32F5_FOC_HSLink.pdf`.
- Native ERC: `erc.rpt`, 688 findings; not an ERC-clean signoff. Imported library electrical pin types, off-grid geometry and inherited project issues require review.
- Original 430 components unchanged; final503 components. Original pin connectivity preserved exactly, including both motor power nets.
- All 68 imported source components preserve source pin topology, except deliberate separation of H8001 pin1 onto passive target VCC. Five new links connect the intended interfaces.
- Parent independently verifies and records interface, reference and preservation results.
- New target UART labels and 12 safely isolated source signal leads attach directly at pins. Exact-name power symbols are in updated project-local StylePower library.

Manufacturing limitations: copied USB footprint has correct referenced pad numbers, but its source geometry/pad technology (through-hole rectangles despite SMD naming) is not certified. Imported footprints require physical datasheet/land-pattern review before PCB work. No PCB update or routing was attempted.

Rebuild: run `scripts/integrate_hslink.py`, then `scripts/polish_hslink.py`, then native netlist/PDF/ERC exports and the verification scripts. The integration script deliberately rebuilds from the timestamped backup; do not rerun after subsequent user schematic edits without updating its baseline.
