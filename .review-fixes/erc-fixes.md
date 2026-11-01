# 导入符号电气类型与悬空线修复

## 范围与备份

负责文件：FOC_M1.kicad_sch、FOC_M2.kicad_sch、HSLink.kicad_sch、Interface.kicad_sch、power.kicad_sch；本地符号库ProDoc_Boa-easyedapro.kicad_sym、ProDoc_IPB-easyedapro.kicad_sym、Interface.kicad_sym。修改前各文件已备份到本目录同名文件。未修改MCU.kicad_sch、fp-lib-table、sym-lib-table，未改变DNP、未屏蔽规则。

## 修复依据

- 电阻、电容、二极管、TVS、连接器、测试点、开关、磁珠、电感、无源晶体从input/unspecified改为passive；离散MOS/BJT为passive，与KiCad离散器件ERC建模方式相符，并非把IC改passive。
- FD6288Q：LIN/HIN保留input，LO/HO为output，VCC/COM/VS/VB/EP为power_in，NC5/7/8/21为no_connect。
- RS6334：IN为input，OUT为output，V+/V-为power_in；LM321供电脚power_in。
- LM5164：GND/VIN/BST为power_in、SW为power_out、PG为open_collector（KiCad用于开漏输出类别）、EP为passive。资料见下载的LM5164.pdf/LM5164.txt，Pin Functions表与7.3.10：PG是开漏状态输出；EP无内部电气连接，要求焊接到GND。U6.6目前无网，标记未使用。
- TD1466/TPS563201：明确的VIN/GND/BST供电脚power_in，SW为power_out；反馈/使能输入保留或修为input。CH213K的VI+/GND为power_in、VO-为power_out。
- HPM5301：GPIO为bidirectional；明确VDD_SOC/VIO/VPMC/VREF/VANA/VSS为power_in；RESETN/WAKEUP/XTALI输入、XTALO输出。DCDC_LP/VDD_OTPCAP/VDD_PMCCAP未获得手册确认，保持unspecified，不能为消除告警猜测。
- MCU页源库LP5907和XC6210已修为1power_in/2power_in/3input/4no_connect/5power_out，待主agent同步缓存。

可复用代码：pin_types.py提供patch(text)->(patched_text,changes)，按解析token区间替换电气类型，不重新序列化整个原理图，不变动几何。主agent可用于MCU页缓存。

## NC和八条悬空线

补U7/U1007的5/7/8/21脚NC标记，U6.6 PG未使用标记，USB8002.3/.9 SBU未使用标记。

删8条单端悬空线：两FOC页各三条12V标记/自举二极管旁死支路；FOC_M2 HO3向左的死支路；FOC_M2从(255.27,280.67)伸至(323.85,280.67)的长死支路。删前枚举物理引脚、线端、标签、结点，确认线段内部没有连接。原ERC坐标/长度缩小100倍，实际并不全是0.07mm短线，不以显示长度作为删除依据。

## 验证

原生CLI成功导出before.xml、after-types.xml。按网络内(ref,pin)集合比较，有效连接LOST=[]、NEW=[]；检查排除了其他agent负责的U1/Y200/C210/C211，当前这几项也不受本任务改变。

中间ERC从原895下降至606（此时其它agent的MCU和封装修复还未全同步）：349离网格、208封装链接、36电源未驱动、5输入未驱动、3未定义类型连接、2孤立标签、2未接引脚、1库符号不一致。随后又修复电阻中文名称符号的两脚类型，消除HSLink三个输入未驱动来源。最终统一ERC由主agent运行，本数字不是最终结论。

剩余电源未驱动包括外部DCBUS/GND、电感/二极管/0R分隔后的电源、自举电源；应确认物理来源再局部加PWR_FLAG，不可全局改power_out。剩余HPM三个特殊供电脚需厂商文档。离网格未批量吸附，避免改变有效连接。

BRKIN和HSLink装配策略未改，仍保持用户的DNP选择；不能用取消DNP来消除功能或电源问题。

## 追加：封装引用与相节点标记

按主agent授权，完成94处实例封装属性修复：11处Interface封装名的字面Unicode转义改为真实中文（现有同几何文件）；32处1206电容、4处0603电容、7处0603电阻；U10/U1010共8运放单元分配TSSOP-14_4.4x5mm_P0.65mm；6只B16WS分配D_SOD-323；8只分流器分配R_2512_6332Metric；3只LL34分配D_MiniMELF；3只LED分配Interface:LED_0603_1608Metric_A1K2；12只功率MOS分配VerifiedParts:NCE7560K。

运放封装依据实例Supplier Footprint和3D Model Title尺寸5.0x4.4、LS6.4、P0.65，符号引脚1..14与四运放脚序一致。B16WS实例数据表（本目录B16WS.pdf/.txt）确认SOD323；缓存符号阴极线位于pin1，标准封装pin1为阴极。数据表额定60V而实例Description为40V，采购元数据有旧料残留，需报告核对。

LED缓存符号是pin1阳极/pin2阴极，与标准KiCad LED封装相反；新增Interface.pretty/LED_0603_1608Metric_A1K2.kicad_mod，来自标准LED_0603_1608Metric，保持全部几何/极性丝印仅互换焊盘编号，避免实际LED反装。LL34的ZMM15V=1K2A、ZMM62=1C2A，与MiniMELF的1阴极匹配。

8只1mΩ分流器使用2512只是封装设计选择，不保证功率额定，采购型号/温升/脉冲额定仍待定。MOS采用主agent转交HQ验证模型：NCE7560K HQ9608/G4211875；缓存symbol确认为1G2D3S，与模型焊盘1/2/3映射一致。

12处M1/M2的MA/MB/MC、VA/VB/VC由电源符号改为同坐标同名字global_label，真实供电标记未改，未增加PWR_FLAG。LM321 OUT本已为output，无需改。

追加修改前备份为本目录*.before-footprint、*.before-signal-label、*.before-passive-footprint、*.before-verified-mos，最初baseline未覆盖。清单见footprint-assignment-changes.json、diode-signal-changes.json、passive-footprint-changes.json。

原生after-types-final.xml→after-footprints.xml真实器件网络集合LOST=[]、NEW=[]；after-footprints.xml→after-footprints-final.xml集合完全一致。之后MOS只修改Footprint字符串。没有修改MCU页或源库U2。非MCU页写入已释放给power agent。

剩余6个独立器件空封装（Q1/Q3、C164/C165、L6/L9）由主agent/精确模型agent继续处理。
