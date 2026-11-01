# 参考小测试焊盘原理图与库同步

用户明确选择按参考做小测试焊盘后，已修改52个实例，范围严格来自reference-testpoint-audit.json的current_keystone。没有操作PCB或IPC。

- 新封装ID：`VerifiedParts:TestPoint_D1.27_Reference`。
- 单个1号圆形pad，1.27×1.27mm，SMD，层F.Cu/F.Mask；无钻孔、无F.Paste、无3D、无User.1假孔。
- 保留参考空间尺度：courtyard为±1.0375mm方框、Fab圆半径0.762mm；隐藏参考和值文字避免增加丝印拥挤。
- attr包含smd、exclude_from_pos_files、exclude_from_bom。
- VerifiedParts已存在于fp-lib-table，无需修改表。

修改MCU.kicad_sch、power.kicad_sch、FOC_M1.kicad_sch、FOC_M2.kicad_sch共52个目标实例：Value=TestPoint，Footprint为新ID；Manufacturer Part、Manufacturer、Supplier Part、Supplier、Datasheet均清空；in_bom=no、in_pos_files=no、on_board=yes。TP200未修改。符号lib_id仍引用原单引脚图形定义，未改符号引脚或库图形；其中名字含5012不代表实例仍有5012采购身份，实际采购字段已清除且不进BOM。

所有4页修改前备份在`.layout-review/testpoint-barepad-backup/`；新封装此前不存在，无旧版本可备份。没有覆盖原参考库或旧中文测试点库。

验证：原生KiCad CLI导出testpoint-before.xml/testpoint-after.xml，逐网名称与(ref,pin)节点完全一致；全部4页AST白名单比较只允许目标元数据变化，通过；52实例唯一齐全，on_board保持，所有符号坐标/UUID/引脚/电气类型及连线不变。验证JSON为`reference-testpoint-fix-validation.json`。

PCB尚须由父代理指定的IPC执行者同步新的焊盘几何、值、封装ID和BOM属性；本任务未宣称PCB已经同步。
