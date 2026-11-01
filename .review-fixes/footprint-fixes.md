# 封装库链接修复结果

## 精确功率器件模型补充

已注册VerifiedParts库，新建模型，原理图映射由父代理执行：

|位号|建议Footprint|证据|
|---|---|---|
|Q5–Q10、Q1005–Q1010|VerifiedParts:NCE7560K|HQ9608/G4211875，精确MPN，1G2D3S|
|D8/D9/D10、D1008/D1009/D1010|VerifiedParts:B16WS_MDD|HQ8820/G4211045，MDD精确MPN，1K2A|
|Q3|VerifiedParts:WSD80120DN56_GDS123|HQ9453/G4741569精确MPN模型适配简化符号，见下|
|C164/C165|VerifiedParts:50TZV220M10X10.5|HQ6464/G1465018，实例实际MPN已为Rubycon220uF50V；旧VKME仅符号名。HQ符号正极pin1，当前网表pin1→DCBUS，pin2→PGND|
|L6|VerifiedParts:SMNR6045-680MT|HQ9415/G6508172，实际68uH而非旧symbol470；无极性pad1/2|
|L9|VerifiedParts:MPIH252010-4R7M-LF|HQ9880/G5907610，实际4.7uH而非旧symbol2.2uH；无极性pad1/2|

Q3原理图符号是1G2D3S，但HQ器件原封装编号1/2/3=S、4=G、5/6/7/8/9=D（含EP9）。适配封装将这些焊盘分别改为3、1、2；几何与层保持不变，重复同号焊盘代表同一电极，不增加原理图网络。`.review-fixes/adapt_q3.py` 已验证除名称与pad编号之外逐字一致。原始未适配模型也保存在VerifiedParts.pretty/WSD80120DN56.kicad_mod供追溯，不能直接赋给3脚符号。

Q1 WSD90P06DN56：HQ无搜索结果。精确厂商PDF已存`.review-fixes/WSD90P06DN56.pdf`与txt，但引脚与封装图未被文本提取，当前模型无法读取图像，未取得可核对的精确模型。明确保留该项，不把N沟道Q3模型套用到Q1。

## 第二轮更新（优先于下方第一轮历史记录）

按父代理后续授权，新增官方C_0402_1005Metric/R_0402_1005Metric别名至Board库C0402/R0402（5项），官方C_0603_1608Metric/R_0603_1608Metric别名至IPB库C0603/R0603（51项）。这些是明确的标准封装设计选择，不宣称与原PCB几何完全相同，PCB需要重新更新和匹配。

测试点采用本机KiCad官方TestPoint_Keystone_5010-5014_Multipurpose（明确覆盖5012），复制至Board库测试点.kicad_mod（52项）。pad1通孔钻孔1.6mm、铜盘直径2.8mm、F.Fab外形直径3.2mm。官方模型提供厂商来源 http://www.keyelco.com/product-pdf.cfm?p=1319；本环境网络抓取失败，未独立视觉复核厂商图纸，未自行构造封装。

第二轮原生ERC `.review-fixes/erc-footprints-pass2.json` 仅剩38条footprint_link_issues，均为ProDoc_Boa-easyedapro空名。56个R/C及52个测试点全部解析成功；Interface11项也已由父代理原理图修复消失。我的库文件修改可归因修复总计116项（第一轮8+本轮108），其余下降归因并行原理图修复。第二轮同样未修改任何原理图、符号库或PCB。


范围：仅修改fp-lib-table，新增必要封装文件与本报告/诊断记录；未修改任何原理图、现有符号库、sym-lib-table或PCB。备份：`.review-fixes/fp-lib-table.before`。

## 确认修复8项

|修改|依据|基线告警消失数量|
|---|---|---:|
|注册GD32F505xx库，新增GD32F505xx.pretty/LQFP100_14x14x1.6.kicad_mod|HQ搜索GD32F505VGT6，manufacturer3040，G56000628；模型名字与原理图一致|1|
|新增Board库C0603.kicad_mod|C130/131/132及C1130/1131/1132的Supplier Footprint=0603且3D Model Title明确L1.6-W0.8；复制KiCad官方C_0603_1608Metric|6|
|新增Board库SO-8_L4.9-W3.9-P1.27-LS6.0-BL-EP.kicad_mod|U6 LM5164DDAR，HQ manufacturer7614，G4672537精确型号模型；焊盘1–8及EP9与原理图编号一致|1|

U6模型为HSOP-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.1mm_ThermalVias，包含热过孔。模型由HQ匹配该器件提供，没有用近似SO8代换或自行改焊盘几何。

模型来源：
- GD32 https://file.eda.cn/web1/M00/9F/06/wKgzJGqjtz-Aa1ZXAAD52-0S6yM2681672.kicad_mod
- U6 https://file.eda.cn/web1/M00/CB/6C/wKgzI2rer7uAWjNMAAAX9XIoY5w1689887.kicad_mod

## 仍有208项（本轮检查时）

原生ERC `.review-fixes/erc-footprints.json`：footprint_link_issues由216降至208。其它代理正在修改原理图，不能把总ERC数量变化归因于本子任务。

|原因|数量|处理限制/建议|
|---|---:|---|
|ProDoc_Boa-easyedapro: 后无封装名|89|源kicad_sym也同样为空，不能用库表恢复；需按器件元数据在原理图赋值。89是实例条数，含多unit重复|
|Board库测试点|52|value5012，但现有TESTPOINT-TH_BD2.0不是已证明对应5012；HQ查询无结果，不擅自替换|
|Board库C0402 / R0402|4 / 1|当前实例无Supplier封装尺寸元数据，仅0402名称；未擅自替换|
|IPB库C0603 / R0603|24 / 27|当前实例无Supplier封装尺寸元数据，仅0603名称；未擅自替换|
|Interface中文转义名|11|见下方|

## Interface别名诊断

新增两个别名文件：
- Interface.pretty/c0402-_u65e0_u4e1d_u5370-_u5168_u5c3a_u5bf8_2.kicad_mod
- Interface.pretty/r0402-_u65e0_u4e1d_u5370-_u5168_u5c3a_u5bf8_1.kicad_mod

来源为对应现有Unicode中文文件，不改变几何。已匹配内部名称并用官方 `kicad-cli fp upgrade --force` 正常化，CLI可以读出，但ERC仍报11项找不到。故不计为已修复。建议主代理将原理图11实例的Footprint直接指向现有Unicode原名并复核：`Interface:c0402-无丝印-全尺寸_2`、`Interface:r0402-无丝印-全尺寸_1`。本子任务无权修改原理图。

## 空名字可恢复信息

已输出 `.review-fixes/empty-footprint-source-map.json`（逐实例完整属性）和 `.review-fixes/named-footprint-metadata.json`。

- 32个10uF实例Supplier Footprint=1206、3D尺寸L3.2W1.6，可选官方C_1206_3216Metric。
- C67/C66/C172/C68为0603；R47/R43/R154/R44/R45/R155/R46为0603；L5/L7/L8为0603，分别对应标准C/R/L封装。
- U10/U1010为TSSOP14，D8/9/10/1008/1009/1010为SOD323。功率MOS、分流器、电感等需继续依据型号与引脚编号核实，不能仅按3D名字决定。

没有提取PCB封装，没有屏蔽ERC规则。
