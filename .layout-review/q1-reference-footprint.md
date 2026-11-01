# Q1 WSD90P06DN56参考封装修复

已新增 `VerifiedParts.pretty/WSD90P06DN56_GDS123.kicad_mod`，可用库ID `VerifiedParts:WSD90P06DN56_GDS123`。VerifiedParts已注册，未修改fp-lib-table。经主agent确认annotation写入无冲突并批准后，已仅修改power.kicad_sch的Q1 Footprint属性为上述库ID；备份为`.layout-review/power.before-q1-footprint.kicad_sch`。未修改PCB。

## 证据

参考原理图 `data/FOC/ProDoc_1.axdr_v1.3_2026-10-31.kicad_sch` 73414ff确认Q1，73470ff Manufacturer Part=WSD90P06DN56，Supplier Part=C719104，参考分析reference-layouts.md97ff将其关联至DFN-8_L5.8-W4.9-P1.27-LS6.0-BL-1模型。

原库 `DFN-8_L5.8-W4.9-P1.27-LS6.0-BL-1.kicad_mod` 430ff九焊盘确为thru_hole+drill0.001mm+*.Cu/*.Mask，与DFN表贴器件及同文件独立F.Paste图形不符。厂商WSD90P06DN56资料文本p1明确DFN5X6_8L；未声称读懂PDF内未提取的引脚图或完成视觉机械图复核。本次按用户授权采用参考工程中精确型号的封装设计，未套用其它MOS型号。

## 焊盘

- pad1：1个，G，(1.9025,2.751)，0.579×1.199mm，180°。
- pad2：5个，D。4个外侧焊盘在y=-2.751；另EP中心(-0.0025,-0.4445)，4.6×4.0995mm。
- pad3：3个，S，y=+2.751，x=-1.9075/-0.6375/+0.6325，180°。

全部9焊盘改为smd rect，层F.Cu/F.Paste/F.Mask，无drill；原编号、坐标、旋转、尺寸、形状、UUID完全保留。移除只适用通孔的remove_unused_layers属性。补attr smd和来源/限制描述，更新footprint名与Value。

所有原图形保持，包括原有F.Paste多边形。焊盘新增标准F.Paste输出与原图形区域有重合；未凭猜测改原有EP开窗或减膏比例。投板/钢网需复核EP焊膏覆盖率及参考导入图形，多边形与铜盘几何极微差不视为厂商推荐工艺认证。

## 验证

脚本 `.layout-review/build_q1_reference_footprint.py` 对源/目标AST逐pad比较，通过以下断言：9pad；编号计数1:1、2:5、3:3；全部SMD且无drill；全部F.Cu/F.Paste/F.Mask；所有位置/尺寸/旋转/形状和原图形不变。详细结果和SHA256在 `.layout-review/q1-footprint-validation.json`。本轮未执行PCB更新、DRC或制造商图视觉核验。

原理图应用后CLI验证：q1-before.xml/q1-after.xml全部网络名称和(ref,pin)节点完全相同；power页文本差异断言仅Q1 Footprint字符串替换。原生ERC为352条（1error、351warning），封装链接告警为0，余346离网格、3引脚类型、2孤立标签、1电源未驱动。结果erc-after-q1.json。验证汇总读取第一次因系统默认GBK失败，已改UTF-8重读成功；网表和文本断言在首次已通过。
