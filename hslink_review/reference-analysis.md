# HPM debug reference analysis

Read-only source: `C:\Users\RTT\Desktop\GD32\HPM`. Native KiCad CLI exported the complete root to `reference.xml`; source schematics were not edited. CLI emitted an annotation-error warning but produced XML. IPC was unavailable; no live design state was used. The following connectivity comes from the native XML, with component identities from source symbol properties. Firmware behavior/directions are distinguished from electrical connectivity.

## Identity and extraction boundary

Root `ProDoc_IPB-TINY_2026-10-26.kicad_sch` contains six pinless sheet blocks: IO, USB, POWER, DAP, ETHERCAT, CORE. DAP sheet UUID: `ea68f542-1b9a-44cc-92e5-d96f6b111dd1`.

Debug MCU U6 is **HPM5301IEG1**, QFN48 plus exposed ground pad49, not STM32/GD32. Target U15 in CORE is **HPM5E31IPB1**. LINK naming, JTAG and UART wiring describe an HPM-based debug probe, compatible in concept with an HSLink implementation. The schematic alone cannot establish actual flashed firmware, USB descriptors, CMSIS-DAP protocol support, or an exact HSLink firmware revision. No firmware source/binary was found in the reference file listing. Online search was unavailable due to missing search-service credentials.

Complete functional DAP sheet extraction: **U6–U8, C64–C87, R52–R73, D5, H1, SW5, USB2, X2**: 54 real components. Exclude imported drawing/frame pseudo-component `?` and retain required power symbols, wires, labels and junctions. U7 is an inductor despite its U reference.

External electrical dependencies: +3.3V, +5V, GND; target JTAG.TMS/TCK/TDI/TDO/TRST; target UART labels PA00/UART0.TXD and PA01/UART0.RXD. D_RESETN is intended as an additional target connection but is currently local and disconnected between sheets. DAP includes its own USB connector/protection and does not need USB1's data circuit. DAP does need a supplied 3.3 V rail or the relevant POWER subsection.

## Exact debug and UART nets

Directions below are intended protocol directions relative to probe; the schematic cannot prove GPIO configuration at boot or under installed firmware.

| Signal | Probe pins and series resistor | Target / header | Intended direction |
|---|---|---|---|
| TCK | U6 PB11 pin24 **and PA27 pin41** on LINK_TCK; R65 pin1 -> pin2, 22R | JTAG.TCK; U15 PA06 pin1; H1 pin4; R73 10K to GND | probe -> target |
| TDI | U6 PB13 pin22; R64 22R | JTAG.TDI; U15 PA05 pin2; H1 pin8; R72 10K to +3.3V | probe -> target |
| TDO | U6 PB12 pin23; R63 22R | JTAG.TDO; U15 PA04 pin3; H1 pin6 | target -> probe |
| TMS | U6 PA29 pin39 on LINK_TMS; R66 22R | JTAG.TMS; U15 PA07 pin100; H1 pin2; R71 10K to +3.3V | probe -> target for JTAG; bidirectional if supported as SWDIO |
| TRST | U6 PB14 pin21; R68 22R | JTAG.TRST; U15 PA08 pin8; H1 pin10 | probe -> target, JTAG reset |
| SRST | U6 PB15 pin20; R70 22R | R70 pin2 is /DAP/D_RESETN, no other node | intended probe -> target reset; actually dangling |
| UART RX | U6 PA09 pin3, LINK_UART_RX; R61 10K pullup to LINK_3.3V; R67 22R | PA00/UART0.TXD; U15 pin11 | target TX -> probe RX |
| UART TX | U6 PA08 pin2, LINK_UART_TX; R62 10K pullup; R69 22R | PA01/UART0.RXD; U15 pin9 | probe TX -> target RX |

Preserve three unusual connections: PA27 pin41 tied directly to PB11 pin24; PA26 pin42 tied directly to PB10 pin25 on an otherwise internal net; PA29 pin39 connected through **R59 22R** to PA28 pin40. They must not be deleted as redundant connections or shorted to unrelated signals. Firmware must configure tied pins compatibly.

H1 is an alternative target debug header, not a programming header for U6: pins1 +3.3V; 2 TMS; 3 GND; 4 TCK; 5 GND; 6 TDO; 7 NC; 8 TDI; 9 NC; 10 TRST. Its pin10 is TRST, **not system NRST**. An attached external probe can contend with U6 unless U6 outputs are made high impedance or isolated.

## USB and boot

USB2 TYPE-C 16PIN 2MD(073): pin2 and11 VBUS2; pin1 and12 GND; CC1 pin4 -> R56 5.1K -> GND; CC2 pin10 -> R57 5.1K -> GND. DN pins5,7 -> U6 PA25/USB_DM pin43 and D5 pin3. DP pins6,8 -> U6 PA24/USB_DP pin44 and D5 pin2. These are direct data nets without series resistors or common-mode choke. D5 PRTR5V0U2X pin1 GND, pin4 VBUS2. SBU pins3,9 NC. Shell pins13,14 GND2 -> R60 1M in parallel with C87 1nF -> GND. GND2 is a shell net, not an isolated digital ground.

U6 PA03 pin7 /DAP/ISP_KEY: R55 10K pulldown, SW5 closes to LINK_3.3V. U6 PA02 pin8: R53 10K pulldown. U6 PA00 pin12 is /DAP/ISP_TX and PA01 pin11 /DAP/ISP_RX; these labels have only their MCU node and no programming connector. U6 RESETN pin13 has R58 10K pullup to LINK_3.3V and C86 100nF to GND; SW5 does not directly reset U6. Thus hardware provides a boot strap button and labeled ISP UART but no routed external UART programmer header. Exact ROM boot truth table and programming sequence require the HPM5301 documentation/firmware; they were not established by this schematic.

X2 24MHz: pin1 to U6 XTALI35, pin3 to XTALO36, pins2/4 GND; C80/C81 each15pF to GND; R54 1M across oscillator nodes. No external flash component exists in this DAP block; do not claim a firmware memory map from that absence.

## Supply pins and external power block

R52 **0R** ties +3.3V (pin2) directly to LINK_3.3V (pin1). There is no independent DAP 3.3V regulator. LINK_3.3V feeds U6 VIO_B00 pins6/34, VIO_B01 pin29, VPMC16, VREFH31, VANA32; C73–C77 and C79 are100nF, C78 is10uF to GND. VREFL30 and exposed VSS49 are GND.

U6 DCDC_LP15 -> U7 pin2; U7 4.7uH pin1 -> LINK_VDD_SOC, feeding VDD_SOC pins5,9,28,33,45. This is the MCU's local core rail, not +3.3V. C68–C72 each100nF; C82/C83 each22uF; C84 10uF; C85 100nF. VDD_OTPCAP10 has C64 4.7uF + C65 100nF to GND. VDD_PMCCAP17 has C66 4.7uF + C67 100nF. Do not connect these cap rails to target supplies.

USB2 VBUS2 -> U8 **CH213K** VI+ pin3; U8 VO- pin2 -> global +5V; pin1 GND. The netlist identifies this pass path, but its reverse-blocking/current characteristics were not independently verified from the datasheet.

Existing +3.3V source is POWER: +5V -> U10 TPS563201DDCR VIN3; SW2 -> U9 4.7uH -> +3.3V-T -> L6 -> +3.3V. Supporting exact refs: U9, U10, L6, C88–C96, R75–R77. C88 bootstrap100nF, C89 feedback22pF, C90 output100nF, C91/C92 output22uF, C93 input100nF, C94/C95 input22uF, C96 input10uF; R75 upper33K, R77 lower10K, R76 EN pullup10K. Optional power indication R74 4.7K + LED2 is a load on +3.3V. Other POWER parts generate other system rails and are not required simply to supply DAP3.3V. Replacement by a separately engineered 3.3V source changes the reference power design and must be explicit.

## Cross-sheet import traps and power risks

1. `/DAP/D_RESETN` is only R70.2, while `/CORE/D_RESETN` is only D1.2. Identical local label text does not connect sheets. CORE D1 pin3 is /CORE/RESETN connected to U15 RSTN pin35. Copying the reference blindly yields no probe-driven system reset.
2. `/USB/USB0_N` (L5.2) and `/CORE/USB0_N` (U15.67) are separate; similarly USB0_P L5.3 versus U15.68. USB0_ID/OC/PWR also differ between USB and CORE. Root sheet blocks have no pins. Do not infer connections from intended naming. DAP's own USB2 nets are internal to its sheet and correctly joined.
3. Global JTAG and UART labels genuinely join DAP to CORE. Generic +3.3V/+5V/GND and LINK global labels can inadvertently join the destination project's rails or another probe instance. Rename or establish explicit hierarchical boundaries when extracting.
4. The XML has multiple `?` pseudo-components from imported graphics/custom ports and the CLI warns about annotation. Never use `?` as a unique component key or merge nodes merely because their printed reference matches. The exact real DAP refs above avoid this ambiguity.
5. USB2 can energize the board-wide +5V through U8, then the main3.3V regulator. R52 and H1.1 are direct power ties, not voltage-sense isolation. USB1 AP2151 U5 has IN5 on +5V and OUT1 on +5P/USB1 VBUS. If enabled, it can drive USB1 VBUS from the DAP supply. D2 SS34A also bridges +5P pin2 and +5V pin1; verify diode orientation from the symbol/datasheet before deriving a supply-OR policy. Multiple external5V sources on H2/USB ports require explicit power-path review; netlist alone does not prove safe reverse blocking.
6. If separated power domains are introduced during extraction, debug/UART lines and10K pullups can inject current through an unpowered MCU's protection structures. Existing22R resistors are signal termination, not effective backpower prevention. R52 cannot be retained as an accidental bridge between independently driven3.3V supplies. The reference has no level shifters/target-voltage sensing, so it is a shared3.3V target design.

## Library portability

Symbols come from local `ProDoc_IPB-easyedapro.kicad_sym` and are also embedded in sheets. DAP IDs: 电阻, CapAcitance, CH213K, DZ127S-22-10-55, FTC252010S4R7MBCA, HPM5301IEG1, PRTR5V0U2X_C5158049, TS-1088-AR02016, TYPE-C 16PIN 2MD(073), XL7EL89CKI-111YLC-24M.

Footprint table points to `${KIPRJMOD}/ProDoc_IPB-TINY_2026-10-26-import-fps.pretty`. Crucial mismatch: resistors/capacitors refer to **R0603/C0603**, while the listed local footprint files are **R0603_SMALL/C0603_SMALL**; similarly LED names may differ. Resolve actual footprint IDs before PCB synchronization. USB connector footprint name contains `TYPE-C-6PIN` despite the symbol/part being16PIN: verify pad numbering rather than trusting the name. Actual USB footprint inspection finds16 pad records,14 unique numbers:1–12 once,13 twice and14 twice; every pad is declared thru_hole despite the SMD filename. This imported footprint needs manufacturing review. No PCB preview or PCB mutation was performed.
