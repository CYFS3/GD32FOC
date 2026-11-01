# 剩余真实供电ERC建模修复

已修改 power.kicad_sch、FOC_M1.kicad_sch、FOC_M2.kicad_sch、HSLink.kicad_sch 和 ProDoc_Boa-easyedapro.kicad_sym。各原理图本轮前备份为 .review-fixes/<文件名>.before-power-model。

添加15个局部PWR_FLAG，位号#FLG9700–9714，并附真实来源文字：

- DCBUS_IN/PGND_IN：CN1外部供电及回路；不代表已确认连接器物理极性。
- DCBUS/PGND：分别经过Q1/Q3保护MOSFET。
- 12V：U6 LM5164 SW经L6输出滤波。
- U6 BST：LM5164内部VCC经内部自举二极管给C67充电。厂商LM5164.txt相关bootstrap章节有明确说明。
- U19 BST：实际BOM为RY8411；通过HQ文档取得官方RY8411.pdf。p2确认BS1/GND2/FB3/EN4/IN5/SW6，与现有TD1466命名符号针序一致，BS为高侧驱动浮动供电。C172跨BS/SW。
- M1/M2三组VB：12V经D8/D9/D10及D1008/D1009/D1010充电，相应C130–132/C1130–1132跨VB/VS。
- HSL_LINK_3V3：VCC经R8052 0R。
- HSL_USB_VBUS：USB8002外部主机VBUS输入。

VREF是U12.4缓冲输出，而HSL_SHIELD仅USB壳及1M/1nF泄放回路，因此原power glyph改同名global_label，未伪装电源驱动。

FD6288的VS1/VS2/VS3（18/15/12）是浮动回流参考，改为passive；VB仍power_in。两张缓存及来源库同步。网表明确证明各VS接对应M1/M2_MA/MB/MC，未以类型修改掩盖悬空引脚。

按主代理提供的已核对映射补5个封装：Q3=VerifiedParts:WSD80120DN56_GDS123；C164/C165=VerifiedParts:50TZV220M10X10.5；L6=VerifiedParts:SMNR6045-680MT；L9=VerifiedParts:MPIH252010-4R7M-LF。Q1仍留缺封装。

六只B16WS描述中旧B5819WS数据改为中性描述，同时删除其他含40V/B5819的旧附加属性。没有改变电路网络。

## 保留问题

1. HSL_VDD_SOC由电感U8007接U8006.DCDC_LP，缺HPM5301官方资料确认该脚及OTPCAP/PMCCAP电气语义，所以未改这些引脚类型，也未添加SOC flag。保留这一真实未证实模型的ERC错误。
2. CN1符号pin1名“-”却接DCBUS_IN，pin2名“+”接PGND_IN。已读取现封装及HQ XT30PW-M模型；HQ符号不含极性且另有机械焊盘，厂商目录PDF未获得可读的针脚极性证据。因此仅确认符号极性名与网名矛盾，不能证明实物一定反接；未改连接。需复核实物/厂商图的接触端方向与PCB焊盘编号。

## 验证

本轮before-power-model.xml与after-power-model.xml所有实际器件ref/pin网络分区完全相同；仅两匿名BST网改为/POWER_SHARED/PWR_BST_U6和PWR_BST_U19。verify_power_model.py通过。

ERC结果erc-power-model.json共353：1条error（HSL_VDD_SOC电源未驱动）、352条warning（346离网格、3引脚类型连接、2孤立标签、1封装链接）。没有新增库不一致警告，未关闭任何ERC规则。
