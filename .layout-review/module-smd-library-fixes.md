# FOC候选误通孔库属性修复

已完成208个候选实例对应5个库封装的修复，共39个库定义焊盘。仅修改候选路径的`.kicad_mod`，未操作IPC、PCB、原理图或库表。

|库封装（均在ProDoc_Board1v1_2026-10-26-import-fps.pretty）|候选实例|修改定义焊盘|表贴依据|
|---|---:|---:|---|
|C0603_S.kicad_mod|44|2|0603、JLC尺寸1.6×0.8、对应表贴电容模型|
|R0603_S.kicad_mod|132|2|0603芯片电阻/NTC及1.6×0.8实体图形|
|SOD-323_L1.8-W1.3-LS2.5-RD_2.kicad_mod|26|2|SOD323表贴二极管及模型尺寸|
|CONN-SMD_6P-P1.25_XUNPU_WAFER-GH1.25-6PWB.kicad_mod|4|8|明确CONN-SMD型号，6个焊接端加2个矩形贴片固定焊盘|
|QFN-24_L4.0-W4.0-P0.50-BL-EP2.6.kicad_mod|2|25|FD6288Q的QFN24及EP25，对应QFN模型和既有F.Paste图形|

仅将这些有型号依据、原为`thru_hole`、`drill 0.001`及`*.Cu/*.Mask`的焊盘变为`smd`、`F.Cu/F.Paste/F.Mask`，删除`drill`与`remove_unused_layers`。每个文件均全部为上述表贴焊盘，因此添加`attr smd`。没有更改真正PTH5012或电源/电机连接器，也没有更改任何混合NPTH孔。

备份在`.layout-review/module-smd-library-backup/`，完整保留原相对路径。脚本`fix_module_smd_libraries.py`按解析AST白名单验证：除pad类型、层、drill、remove_unused_layers以及顶层attr之外，全部AST不变；尤其坐标、尺寸、形状、旋转、编号、UUID、所有原图形包括F.Paste保持。39个定义焊盘验证全部通过。原F.Paste图形和新pad paste可能重合，QFN EP工艺需后续钢网复核，不在本次更改。

`module-smd-library-fixes.json`包含路径、备份、前后SHA256、候选ref、完整同库ref及padcount。注意C0603_S额外有19个当前工程非候选实例、R0603_S额外有18个非候选实例共享这些库；当前PCB未因库修改自动改变，但未来整库更新会覆盖这些同库实例。本次仅5库路径，没有扩大到其它目录封装。主agent应使用JSON中`files[].path`交付/打包，IPC agent独立验证板上候选修复。
