# MCU页去耦、NC与外部复位接入修复

负责页为 MCU.kicad_sch；未修改其他页、PCB或库表。修改前备份：MCU.before-fixes.kicad_sch。主agent追加授权后，仅同步ProDoc_Boa-easyedapro.kicad_sym中U2的LP5907QMFX-3.3Q1源符号，解决其原引脚几何与缓存不同的mismatch；该操作前全库备份U2-source.before-cache-sync.kicad_sym。其它源符号保持。

## 已实施

- C212=100nF，0603，VCC—GND；注明放置于U1.6 VBAT近端。VBAT仍连接VCC。
- C206/C208由100nF改为10nF；新增C213=1uF，0603，MCU_VDDA—AGND。明确C206+C207(1uF)给U1.22 VDDA近端，C208+C213给U1.21 VREFP近端。保留MCU_VDDA共网和R203供电方式。依据GD32F505 Datasheet Rev0.9RC5 p73 Figure4-1，每模拟引脚1uF+10nF，VBAT100nF。
- U2.4/U20.4增加no_connect标记，坐标分别(201.93,59.69)/(201.93,36.83)，未接任何导线。
- 新增TP200，标准Connector:TestPoint、TestPoint:TestPoint_Pad_D1.5mm，连接NRST。J200保持4针，外部探针可通过测试点执行复位/复位下连接，注明开漏驱动并使用J200 GND。HSLink所有DNP保持。
- 已有保护说明和PWM说明原坐标与晶体区重叠，移至(245,230)/(15,220)并合理换行；保留原内容。新增电容坐标(254,63.5)/(292.1,63.5)，TP200(254,95.25)，通过坐标确认与现有器件位置不重叠。

## 验证

原生KiCad CLI已成功读取并导出实际保存页网表。精确(ref,pin)集合比较：VCC只新增C212.1、GND只新增C212.2、MCU_VDDA只新增C213.1、AGND只新增C213.2、NRST只新增TP200.1；其余所有原有网络不变。C206/C208值修改不改变拓扑。相关脚本verify_mcu.py、mcu-before.net、mcu-after.net均保留。

SVG导出成功：mcu-svg/MCU.svg。当前模型不支持图片输入，未进行视觉渲染审阅；几何坐标与文本尺寸估计检查不能替代人工视觉确认。

最终单页独立ERC：158→156，power_pin_not_driven 6→4，pin_not_connected 2→0，pin_not_driven 2→0。其余38离网格、41孤立标签、12封装链接未增加；lib_symbol_issues 57→61是独立页缺项目库上下文所致，新增4个StylePower符号在主工程正常解析。最终全工程检查当时596条，/MCU/仅4个power_pin_not_driven，没有U2库不一致或新增电容/测试点问题；工程其它页由其它agent修改，此数字为当时快照，最终统一结果由主agent汇总。

## 引脚类型修复证据

15处缓存类型修复，日志mcu-type-changes.json：电阻、电容和5012测试点改passive；U2/U20第1/2脚power_in、3脚保持input、4脚no_connect、5脚power_out。未改变引脚坐标或连接。应用共享pin_types.py的patch函数，未执行其修改其它文件的main。

厂商依据通过HQ器件搜索得到文档并下载：LP5907.pdf / LP5907.txt印刷p4 Pin Functions，XC6210.pdf / XC6210.txt印刷p4 PIN ASSIGNMENT，明确确认电源/地/使能/NC/输出。LP5907源库原x=±12.7而缓存x=±10.16，不能整块更新缓存；故按追加授权用已修正缓存几何更新源库单个U2符号，现全工程无U2 mismatch。

封装采用已安装KiCad标准0603电容、TestPoint_Pad_D1.5mm；没有新增库表或改PCB。

## 追加局部供电声明

主agent授权后，追踪最新全工程原生网表 mcu-supply-project.net，确认5V由U19.6 SW→L9.1/.2送至U2/U20输入；AGND经R3.1/.2接GND；MCU_VDDA经R203.2/.1接VCC；GND为供电回流。新增标准power:PWR_FLAG #FLG200..203仅对应5V/GND/AGND/MCU_VDDA四网，未改变真实器件引脚类型或屏蔽规则。加标记前备份MCU.before-flags.kicad_sch。

最终再次导出网表验证：物理(ref,pin)集合仍只有上述两个电容和测试点新增，全部旧网保持。供电标记是非BOM/非PCB对象，原生netlist省略其节点。最终单页ERC152条全部warning；项目上下文的/MCU/页0条违规。全工程此时410条是并行修复快照，以主agent最终报告为准；根页聚合的既有离网格警告仍可能包含MCU对象，不能将/MCU/0条说成整张图所有规则无告警。
