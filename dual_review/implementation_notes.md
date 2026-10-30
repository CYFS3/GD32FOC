# Dual motor schematic implementation

The existing schematic is now a five-sheet project: root, MCU, POWER_SHARED, FOC_M1, and FOC_M2. The existing project settings and PCB were not modified; their SHA256 hashes match the backup in `dual_backup/20261026_143556`.

## Circuit changes

- `power.kicad_sch` contains the original common input connector/protection, bulk capacitance, 12V/5V conversion, and VREF buffer. These regulators were not duplicated.
- `FOC_M1.kicad_sch` retains original physical component references for the functional motor circuit. `FOC_M2.kicad_sch` duplicates the same actual embedded symbols, coordinates, device properties and wiring, using reference numbers offset by 1000 and fresh object/pin UUIDs and sheet instance paths.
- Both motor sheets include their own FD6288Q, six power MOSFETs, three phase shunts, one bus shunt, analog sensing, temperature sensing, Hall connector and SPI connector. M1_/M2_ distinguish motor-specific nets. SPI2_SCK/MISO/MOSI are intentionally common upstream of each connector's series resistors, with independent chip selects.
- The phase-shunt lower ends join the respective M1_SHUNT_RETURN or M2_SHUNT_RETURN. Each joins common PGND only through its own R109 or R1109 bus shunt. These return nets are distinct in the exported netlist.
- Removed the isolated illustrative LM358/Rf/R block, unrelated 24V example, decorative frame, and unreadable source annotations from the functional power pages.
- MCU pin assignments are in `pin_mapping.json`; the netlist is authoritative for connectivity. Six phase-current inputs use PA0..PA5. Both bus current inputs, both temperatures and six Hall signals are connected. M1_VBUS supplies the shared bus measurement. Phase voltages, COM and the redundant M2 bus voltage divider remain available in the reference circuit but are not assigned to MCU pins.
- MCU VDDA/VREFP and C206..C208 now use MCU_VDDA, derived from VCC through R203=0R. AVCC remains the separate analog amplifier supply.
- R300..R305 and R1300..R1305 provide 10k pulldowns on all twelve gate driver HIN/LIN logic inputs. The source FD6288Q symbol has no dedicated enable pin.
- J201 provides VCC, GND, M1_BRKIN and M2_BRKIN on pins 1..4. R204/R205 pull the fault inputs HIGH. Firmware must configure active-HIGH timer break; an external open-drain HEALTH circuit must hold each input LOW only while its motor is healthy. Unplugging defaults to asserted break once firmware has configured the timer. This is an external protection interface, not a completed autonomous overcurrent comparator. Thresholds remain unspecified.

## Native validation

KiCad 10.0.6 successfully exported `dual_motor.xml` and the five-sheet `dual_motor.pdf`. Export contains 430 physical components and 236 nets. The parent agent's independent connectivity validator reports PASS and writes `verification.json`.

Final native ERC result: **430 findings, 152 errors and 278 warnings**. This is not an ERC-clean or manufacturing-ready design.

| Category | Count |
| --- | ---: |
| footprint_link_issues | 154 |
| pin_not_driven | 117 |
| unconnected_wire_endpoint | 72 |
| pin_to_pin | 37 |
| power_pin_not_driven | 24 |
| endpoint_off_grid | 14 |
| pin_not_connected | 11 |
| lib_symbol_mismatch | 1 |

The imported reference includes incomplete footprint identifiers, passive symbols incorrectly typed as inputs, open reference wire stubs, NC pin inconsistencies and power-source ERC issues. Both reference-derived motor stages retain those issues. Newly added components were placed on the existing grid. Net alias conflicts were normalized (Hall, phase return and shunt return); the final ERC has no multiple_net_names findings.

## Engineering limitations

No bus/current rating change was requested; all reference component values and ratings were retained without validating dual-motor load capability. Supply thermal/current margin, MOSFET/gate-driver ratings, current amplifier range and polarity, ADC acquisition timing, fault thresholds and sensor voltage compatibility remain engineering work. Source R109 (and duplicated R1109) displays 1mΩ while its manufacturer part metadata is LR2512D-3W-5mR-1%; this inconsistency is retained and must be resolved before current calibration or procurement. Source input connector pin-name/polarity conflict also requires review. PCB synchronization/layout/routing has not been performed.

## Audit artifacts

`split_manifest.json` records sheet identifiers, reference mapping and removed references. `backup_path.txt` records the full backup location. `pin_mapping.json` uses final canonical labels. The scripts are one-time migration steps, not safe to rerun against an already-converted design: restore the backup first if a replay is needed, then run build_dual_motor.py, finish_dual_mcu.py, map_dual_pins.py, normalize_dual_aliases.py, snap_dual_additions.py in order. The final alias normalization is reflected in pin_mapping.json.
