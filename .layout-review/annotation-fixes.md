# 原理图批注阻塞修复

## 根因

当前工程7张原理图共870个符号实例中存在17组隐藏电源位号重复。KiCad原生netlist会省略隐藏电源实例，因此此前只检查netlist实体位号时没有暴露此问题；F8批注检查则包括这些隐藏实例。

- FOC_M1与Interface重复：#PWR9301～#PWR9310（10组）。
- MCU与FOC_M1重复：#PWR9041～#PWR9044（4组）。
- MCU与power重复：#PWR9038～#PWR9040（3组）。
- #PWR9037在当前工程未重复，无需改动。

未发现实体器件未注释位号、实体重复unit、缺失unit、实例Reference/Unit与属性不一致、当前工程层级路径不匹配。U1、U10/U1010、U9101/U9102等多单元同位号属于合法重复，全部保留。#FLG位号也已纳入检查，未重复。

## 最小修复

仅修改MCU.kicad_sch和Interface.kicad_sch，共17个隐藏电源符号：每个同步修改property Reference和instances/reference。共34处字符串变更；未改变实体位号、任何UUID、元件坐标、网络名称或连线。

|文件|旧位号|新位号|
|---|---|---|
|Interface|#PWR9301|#PWR12000|
|MCU|#PWR9041|#PWR12001|
|MCU|#PWR9044|#PWR12002|
|MCU|#PWR9043|#PWR12003|
|MCU|#PWR9042|#PWR12004|
|Interface|#PWR9302|#PWR12005|
|Interface|#PWR9303|#PWR12006|
|Interface|#PWR9304|#PWR12007|
|Interface|#PWR9305|#PWR12008|
|Interface|#PWR9306|#PWR12009|
|Interface|#PWR9307|#PWR12010|
|Interface|#PWR9308|#PWR12011|
|Interface|#PWR9309|#PWR12012|
|Interface|#PWR9310|#PWR12013|
|MCU|#PWR9038|#PWR12014|
|MCU|#PWR9039|#PWR12015|
|MCU|#PWR9040|#PWR12016|

## 验证

1. 修复前原生KiCad CLI导出明确输出“警告: 原理图存在批注错误, 请使用原理图编辑器修复它们”。
2. 修复后原生CLI成功导出，**不再输出该提示**。最终捕获stdout与stderr的`annotation-cli-final.log`为空（0字节），进程退出0。
3. 修复前后实体网络名称及每个网络(ref,pin)集合完全一致。
4. 将17个隐藏位号反向替换后，所有7张原理图均与备份逐字节一致，证明无其它原理图变化。
5. 全870实例重新审计：隐藏电源和flag、Reference/Unit、层级实例path、合法多unit和未注释检查全部通过；每页对象UUID唯一。

本任务没有修改任何PCB、库文件或现有实体器件位号。未声称F8实际GUI已验证，验证对象是当前保存的原理图文件。

## 脚本、备份与交接

- 完整备份：`.layout-review/annotation-backup/`（7张原理图）。
- 审计脚本：`.layout-review/audit_annotation.py`。
- 最小修改脚本：`.layout-review/fix_annotation.py`（基于修复前审计，已执行；不应重复执行）。
- 验证脚本：`.layout-review/verify_annotation.py`。
- 逐UUID变更清单：`.layout-review/annotation-changes.json`。
- 修复前后审计：`annotation-audit-before.json`、`annotation-audit-after.json`。
- 验证结果：`annotation-validation.json`。
- 修复前后网表：`annotation-before.xml`、`annotation-after.xml`、`annotation-final.xml`。

**编辑器可能仍保留旧内存状态。应重新打开工程/原理图加载磁盘修改，避免将旧内存内容保存覆盖，然后再按F8。** 本次消除的是批注阻塞；此前已有的封装缺失、ERC问题若在后续同步中出现，应作为不同问题处理，不再归因为批注。
