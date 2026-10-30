# Current six-sheet GD32 dual FOC + HSLink engineering audit

Read-only schematic audit, native KiCad 10 CLI export of `GD32F5_FOC.kicad_sch`. No schematic was modified. Evidence: `audit_netlist.xml` (authoritative exported connectivity), `audit_nets.txt` (one line per net), `audit_values.txt` (component fields), `audit_erc.json`. Snapshot precedes the parent agent's planned interface integration; re-export after that integration.

## Ranked confirmed issues / corrections

1. **P1 — All eight shunts have conflicting resistance identities, not merely the two bus shunts.** R81/R82/R83/R109 and R1081/R1082/R1083/R1109 display **1 mΩ**, while each Manufacturer Part is `LR2512D-3W-5mR-1%` and part description says **5 mΩ**. Phase shunts connect low-side MOSFET source to Mx_SHUNT_RETURN; bus shunt connects Mx_SHUNT_RETURN to PGND. Both phase and bus amplifiers have nominal differential gain 20, so sensitivity is 20 mV/A at 1 mΩ or 100 mV/A at 5 mΩ. At nominal 1.65 V center and ideal 0–3.3 V output the mathematical half-range is 82.5 A versus 16.5 A; these are NOT permissible current ratings or guaranteed linear ranges. Dissipation at equal current differs fivefold. **Correction:** choose actual shunt resistance from required current/thermal range, then make Value, MPN, assembly BOM, firmware scaling and protection thresholds agree for all eight. Do not silently assume either field wins.

2. **P1 — Sole analog-ground link R3 also has a critical BOM conflict.** R3.1 is AGND; R3.2 is GND. Value says `0Ω`, but Manufacturer Part `0402WGF1002TCE`, supplier C25744 and description identify **10 kΩ**. AGND contains U1.19 VSSA, U1.20 VREFN, U10/U1010.11 V−, U12.2 V− and analog filter returns. There is no other direct AGND↔GND link in the exported netlist. A 10 kΩ assembly would lift the analog ground under analog supply current. **Correction:** give R3 a verified zero-ohm MPN/assembly identity and retain the intended ground link. This is a confirmed inconsistency, not proof that a physical board already contains 10 kΩ.

3. **P1 — U19 5 V converter identity is unresolved.** Value `RY8411` conflicts with Manufacturer Part `JW5026`, manufacturer JoulWatt and supplier C185109. Actual wiring: pin5 VIN=12V, pin2 GND, pin6 SW→L9→5V, pin1 BST→C172→SW, pin4 EN via R153=10k to12V; pin3 FB has R155=62k from5V and R154=12k toGND. Divider multiplier is **6.1667**, so output is 6.1667×the actual IC feedback reference (0.8 V would give 4.933 V; 0.6 V would give 3.700 V). These reference values are conditional examples, not claims about either IC. **Correction:** select one real ordering code; verify its six-pin map, FB reference, EN and bootstrap requirements against its datasheet before relying on the 5V label. Affects both 3.3V LDOs and Hall supplies.

4. **P1 assembly blocker — incomplete footprint identifiers include the power/sensing path.** 83 exported components have missing IDs or an empty item after `:`. Examples Q1/Q3, Q5–Q10/Q1005–Q1010, U10/U1010, all eight shunts, bootstrap diodes D8–D10/D1008–D1010. **Correction:** assign verified packages with correct physical pad mapping. A correct schematic netlist alone cannot establish that these parts will route/assemble correctly.

5. **P2 — CN1 polarity annotation contradicts electrical use.** CN1.1 named `-_1` connects DCBUS_IN (Q1.3 source); CN1.2 named `+_2` connects PGND_IN (Q3.2 drain). **Correction:** compare the actual XT30PW-M30.G.Y drawing and physical keyed connector, then correct symbol polarity names and/or electrical mapping consistently. Do not swap live nets solely to make labels look right.

6. **P2 — HSLink shares target supply and ground even when all five signal links are DNP.** R8052=0R joins VCC to HSL_LINK_3V3, feeding U8006.6/.16/.29/.31/.32/.34. USB8002.1/.12 are GND, shared with MCU and gate-driver COM; USB shield uses R8060/C8087. HSL_USB_VBUS contains only USB8002.2/.11 and D8005.4: there is no VBUS-to-board regulator feed in this snapshot. Thus USB-only power does not intentionally power HSLink, while target-powered HSLink can operate from VCC. Five DNP signal resistors R8901–R8905 do not disconnect its power demand or USB ground. **Correction:** explicitly specify target-powered debugger operation and include HPM5301 consumption in U20/5V budgets. If independent USB-powered operation or galvanic isolation is required, a power/interface redesign is necessary; simply closing the signal links does not provide it.

## Current sampling: actual pin/gain evidence

For motor 2, add 1000 to each resistor, capacitor and op-amp reference below; MCU pins differ as listed.

| Function | Differential input wiring at U10 | Feedback and bias | Output / MCU |
|---|---|---|---|
| Phase A | + pin10 via R69=1k from M1_IA+; − pin9 via R67=1k from M1_SHUNT_RETURN | R65=20k output8→−; R71=20k VREF→+ | output8→R70=22Ω→M1_IA→U1.23 PA0; M2→U1.26 PA3 |
| Phase B | + pin12 via R72=1k from M1_IB+; − pin13 via R68=1k from return | R66=20k output14→−; R74=20k VREF→+ | output14→R73=22Ω→M1_IB→U1.24 PA1; M2→U1.29 PA4 |
| Phase C | + pin3 via R52=1k from M1_IC+; − pin2 via R145=1k from return | R146=20k output1→−; R55=20k VREF→+ | output1→R53=22Ω→M1_IC→U1.25 PA2; M2→U1.30 PA5 |
| Branch bus | + pin5 via R148=1k from M1_SHUNT_RETURN; − pin6 via R147=1k from PGND | R149=20k output7→−; R51=20k VREF→+ | output7→R50=22Ω→M1_IBUS→U1.18 PC3; M2→U1.34 PC5 |

Ideal transfer for each is **Vout=VREF+20(Vsense+−Vsense−)**. No swapped amplifier feedback/input polarity is visible relative to the cached symbol pin functions. C133–C136 (and +1000) are 1nF to AGND after the 22Ω output resistors; their standalone RC time constant is 22ns, so they do not by themselves prove PWM-frequency filtering or ADC settling performance. Actual amplifier datasheet and ADC sample timing remain necessary.

VREF is a bias rail, not the MCU ADC reference: R48=10k AVCC→U12.1 IN+, R57=10k IN+→AGND; U12.4 OUT is tied to U12.3 IN− and drives eight 20k bias resistors. Nominal VREF=AVCC/2. U12 is LM321MF/NOPB on AVCC=3.3V; verify guaranteed input common-mode and output swing at 3.3V and the eight-channel load, particularly temperature extremes. Metadata for RS624XQ is internally inconsistent (1.1MHz GBP field versus 7MHz description), so no settling/bandwidth rating is accepted here.

Each bus shunt senses only that motor bridge's summed low-side return, not total connector supply current: U6 VIN and other shared supply paths draw directly from DCBUS/GND and bypass R109/R1109. Firmware must not equate either IBUS (or necessarily their sum during transients) to all input current. Low-side phase shunts require PWM-synchronized valid sampling windows; their topology is not continuous in-line phase sensing.

## Power paths and ground connectivity verified

- Positive input: CN1.1 DCBUS_IN→Q1.3 S / Q1.2 D→DCBUS→both inverter high-side drains and U6.2 VIN. Negative input: CN1.2 PGND_IN→Q3.2 D / Q3.3 S→PGND. Q1 is specified as P-channel, Q3 N-channel in component identity; actual package pad mapping remains unverified because footprints are incomplete.
- Motor return: low-side Q8/Q9/Q10 sources→R81/R82/R83→M1_SHUNT_RETURN→R109→PGND; analogous motor2. No direct GND short bypassing either branch bus shunt appears in the netlist.
- PGND↔GND is joined by **two parallel zero-ohm links R134 and R136**, each pin1 PGND / pin2 GND. This is connected, not floating; two physical links can create unwanted current sharing loops, which requires layout review. R41 and R42 have **both pins on GND**, so they provide no electrical partition. Correct drawing/net-tie placement if these were intended as separate return links.
- U6 generates nominal12V through SW pin8/L6; FB pin5 uses R44=453k to12V, R43=49.9k toGND. U19 then generates the intended5V; U2 produces AVCC and U20 produces VCC. U2/U20 inputs and enable pins are tied to5V. These are actual connections, not a validated voltage/current budget.
- Gate driver COM pin6 and EP pin25 of both U7/U1007 are GND, with the power return behind the shunts. Assess switching ground bounce and negative phase transients in PCB layout and driver datasheet; do not infer them from net names alone.

## Bootstrap and MCU checks that pass connectivity review

All six bootstrap capacitors are between their own VB and VS nets, **not ground**:

| Driver | Capacitor | VB pin/net | VS pin/net |
|---|---|---|---|
| U7 | C130 | 20 / M1_VB1 | 18 / M1_MA |
| U7 | C131 | 17 / M1_VB2 | 15 / M1_MB |
| U7 | C132 | 14 / M1_VB3 | 12 / M1_MC |
| U1007 | C1130 | 20 / M2_VB1 | 18 / M2_MA |
| U1007 | C1131 | 17 / M2_VB2 | 15 / M2_MB |
| U1007 | C1132 | 14 / M2_VB3 | 12 / M2_MC |

D8/D9/D10 and +1000 connect pin2 to12V, pin1 to respective VB. Their symbol functions are numeric, so verify cathode pad1 against physical diode data. FD6288 cached mapping is HIN1/2/3=22/23/24, LIN1/2/3=1/2/3, HO1/2/3=19/16/13, LO1/2/3=11/10/9; do not declare silicon pin-map verification without the QFN datasheet. C130 label relocation has not created a connectivity fault in this snapshot.

MCU: U1.94 BOOT0→R20110k→GND; U1.37 BOOT1→R20210k→GND. U1.14 NRST→R20010k→VCC and C209→GND, with optional R8903 debugger link. U1.21 VREFP and .22 VDDA share MCU_VDDA via R2030R from VCC, with C206/C207/C208 to AGND. U1.19 VSSA/.20 VREFN=AGND. U1 VDD pins11/28/50/75/100 and VBAT6 are VCC. This follows local `review/datasheet.txt` guidance (lines3451–3452,4189–4190), subject to fixing R3 BOM and physical supply integrity.

Local official pin table confirms PE7 pin38 ADC2_IN4 and PE8 pin39 ADC2_IN5 (`review/datasheet.txt`1518–1523), matching M1_NTC/M2_NTC. No claim that these pins lack ADC support is warranted. Firmware must use ADC2 for them. M2_VBUS divider is present but not connected to MCU; M1_VBUS connects U1.33 PC4 and observes the same shared DCBUS, so a second ADC connection is not inherently necessary. M1/M2_PWM, phase VA/VB/VC and virtual COM networks are not MCU-connected in this snapshot; do not advertise those as available firmware measurements without additional routing.

## Datasheet/design-input closure needed before release

- FD6288Q: official QFN pinout/EP requirements, input VIH at3.3V, UVLO, allowable VS transients, maximum VB/VS, bootstrap charge/leakage and minimum refresh duty. Cached B16WS attributes disagree on40V versus60V; use actual diode datasheet and maximum bus/transients.
- RS624XQ and LM321: physical pin map,3.3V operation/common mode/output swing, amplifier settling at gain20, ADC acquisition drive and reference-buffer load. No unsupported bandwidth or accuracy guarantee.
- Resolve U19 identity; then verify both DC/DC stages and U20 thermal/current budget including HPM5301, sensor loads and two driver banks. Define maximum input voltage, phase/bus current, PWM frequency, ambient and regeneration behavior. Part catalog maximum currents are not board ratings.
- Input protection: CN1 polarity, Q1/Q3 physical pad map, Q1 gate clamp D24 and Q3 gate clamp D23, D22 TVS standoff/clamp at required surge, and absence of an independently demonstrated regenerative overvoltage energy path. No blanket reverse-polarity/surge/regeneration protection claim from schematic alone.
- BRKIN: M1 U1.51/PB12 and M2 U1.31/PA6 each have10k pullups R204/R205 toVCC and external J201 pins3/4. There is no current comparator wired to these nets in this snapshot. For the intended active-high trip convention, external healthy must pull low; configure timer break polarity/enables and fault latching accordingly. No firmware exists to verify this or dead time/ADC trigger sequencing.

ERC total769 is dominated by273 off-grid endpoints,205 footprint-link issues,145 input-not-driven,94 pin-type conflicts and28 undriven power pins.13 unconnected-pin entries are NC pins/PG/USB SBU, not proof of missing motor connectivity. Imported pin electrical types are often inappropriate. Two isolated labels are HSL_ISP_TX/RX, each only connected to one HPM MCU pin. Prioritize issues above over reducing ERC count by markers.

Limitation: online search unavailable (search backend API key missing), and no local FD6288/RS624 regulator datasheets were found. Official local GD32 datasheet/manual/errata text exists under `review/`. Silicon-level checks not established by those local sources remain explicitly open; component metadata is not treated as a verified rating.
