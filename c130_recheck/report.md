# C130 current-file recheck

The saved schematic had the previous C130/right-MA fix, and no `_autosave-FOC_M1.kicad_sch` existed at inspection. The remaining collision was the left-facing VB label covering the bootstrap diode, not C130's reference field. D8 is centred at (336.55,199.39); its drawn body spans approximately x335.28–338.328 mm. The old VB1 PDF text spans x332.953–340.002 mm at the diode's y coordinate, intersecting that body. The same layout occurs for all three phases of both motors.

Changed only FOC_M1.kicad_sch and FOC_M2.kicad_sch: raised each of six VB labels 3.81 mm, oriented it rightward, and connected it by a vertical 3.81 mm branch at the existing diode/wire endpoint x341.63. Added six branch wires and six junctions. No components, existing wires, capacitor fields, MA/MB/MC labels, UUIDs, or electrical names were deleted or moved. The existing short right-side leads remain 2.54 mm. Existing file formatting is retained outside the exact edited nodes; new coordinates use six decimal places.

After export, all six VB text bounds are x972.300–992.283 PDF points; capacitor references begin x997.156, a 4.873-point / 1.719-mm gap. The longest neighboring diode references (D1008–D1010) end x967.318, a 4.982-point / 1.757-mm gap. VB1 text is y552.350–557.654 points; the existing horizontal connection is y565.2 points, giving 7.546 points / 2.662 mm clearance from text to wire. The VB2/VB3 rows have the same gaps. This is PDF text-bound and source-geometry verification, not a claim of visual image inspection.

Native KiCad XML netlists exported immediately before and after have exactly equal complete mappings of every net name to every (reference,pin): 288 nets, 1234 nodes. In particular M1_VB1 still includes C130.1, D8.1, U7.20. The full before/after XML exports and schematic backups are in this directory.

Outputs: updated.pdf (full project), focus_3.pdf (M1 bootstrap area), focus_4.pdf (M2 bootstrap area). current.pdf is the pre-change export. No GUI save/reload was performed, so any unsaved editor state remains the user's responsibility; the PDF represents the corrected saved files.
