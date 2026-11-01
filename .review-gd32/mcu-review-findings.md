# GD32F505 MCU 只读核对结果

依据：用户指定权威 get_project_netlist JSON；datasheet.txt 为 GD32F505xx Rev0.9RC5 (2026-03)；manual.txt 为 GD32F50x 用户手册；errata.txt 为 V1.1 (2025-11)。以下页码均为文档印刷页码。未修改任何原理图，仅新增本报告。

## 结论与证据等级

本次目标范围未发现可确认的 MCU 引脚错接或非法外设复用。已确认若干装配/功能事实及需要固件或实测验证的条件，不能把它们直接称为硬件错误。

- R9101/R9103 实例 dnp=no；R9102/R9104 实例 dnp=yes。FOC_M1.kicad_sch:56407/56410，FOC_M2.kicad_sch:56423/56426。因此现默认3.3V编码器供电并未把5V短接到VCC。选5V时必须移除3.3V桥；同时装两桥才短路。不要将裸网表中两电阻均存在误报为现有短路。
- M2_VBUS 确认未接 U1：网络只有 C1078.2,D1018.2,CN1040.1,R1102.1,R1094.2。两路共享 DCBUS，U1.33 已测 M1_VBUS，是否需要第二路测量属于需求项。
- J201 的 M1_BRKIN、M2_BRKIN 确认仅接 MCU、10k 上拉及外接接口，没有网表中的板上故障输出源。它们是外部保护输入预留，不能据此宣称已具备板上自主硬件过流关断。

## 电源/复位/启动/调试

- U1 GD32F505VxTx LQFP100 与 datasheet 表2-3 pp24–30 相符；VDD 11/28/50/75/100 全接 VCC；VSS 10/27/49/74/99 全接 GND；VBAT.6 接VCC。C200–204 各100nF，C205=4.7uF。数量满足5个VDD基本去耦建议，VBAT独立近端100nF及布局距离不能由网表证实。datasheet p73 图4-1要求每VDD近端100nF、总4.7uF、VBAT100nF。
- VDDA.22 / VREFP.21 同接 MCU_VDDA，经 R203=0R 接 VCC；VSSA.19/VREFN.20 接AGND，经 R3=0R 接GND。C206/C208=100nF、C207=1uF。与同源供电约束一致（datasheet p58、p72），但图4-1 p73 推荐模拟支路1uF+10nF，与当前100nF值不同，是推荐配置差异，不能直接判失效。PCB近端、噪声及电容分配待查。
- VCC 由 U20 XC6210B332MR 输出.5供电；AVCC 是独立 U2 LP5907QMFX-3.3Q1 输出.5，绝非MCU的VDDA网络。datasheet p72：VDD/VDDA 2.6–3.6V，同电压；>=240MHz时VDD>=3.0V。实际纹波、负载、时序待测。
- BOOT0 U1.94→R201=10k→GND；BOOT1/PB2 U1.37→R202=10k→GND。正常低电平启动配置合法，但主Flash启动还要求OTP的BTFOSEL等匹配，不能只凭电阻保证。manual pp40–41 表1-3，复位后第4个CK_SYS上升沿锁存。
- NRST U1.14→R200=10k→VCC，C209=100nF→GND，匹配 datasheet p97 图4-9；外部复位要达到低于0.3VDD，非滤除脉冲宽度至少350ns（表4-27）。
- SWDIO U1.72/PA13→J200.3；SWCLK U1.76/PA14→J200.4；J200.1=VCC/.2=GND；datasheet p28、manual pp485–486合法。J200没有NRST，因此该口没有直接connect-under-reset路径。
- R8901/8902/8903 是 HSLink 到SWDIO/SWCLK/NRST桥，三者实例均dnp=yes（HSLink.kicad_sch:12213、10155、14283）。当前默认板载HSLink未连目标，需装桥才可用；外部J200仍可SWD。属于明确装配条件。
- U1.73=NC保持未连接，合法。OSCIN/OSCOUT 12/13、PC14/15未连接：允许内部时钟方案；不得假定固件已配置外部晶振，频率/精度须核实。

## ADC 引脚与量程

|网络|U1脚/端口|合法ADC通道|证据|
|---|---|---|---|
|M1_IA/IB/IC|23 PA0 /24 PA1 /25 PA2|ADC0/1/2_IN0/1/2|datasheet p25|
|M2_IA|26 PA3|ADC0/1/2_IN3|p25|
|M2_IB/IC|29 PA4 /30 PA5|ADC0/1_IN4/5，不能选ADC2|p25|
|M1_IBUS|18 PC3|ADC0/1/2_IN13|p25|
|M2_IBUS|34 PC5|ADC0/1_IN15|p26|
|M1_VBUS|33 PC4|ADC0/1_IN14|p26|
|M1_NTC / M2_NTC|38 PE7 /39 PE8|ADC2_IN4/5，不能选ADC0/1|p26|

注意 PE7/PE8 在本型号确实支持ADC2；不可按其他GD32系列判错。PA4/5与PE7/8虽通道号相同，但ADC实例不同。

电流放大器 U10/U1010 的4脚V+=AVCC、11脚V-=AGND；AVCC来自3.3V U2，不是5V供电。MCU电流输入接22Ω串联电阻（R70/R73/R53/R50、R1070/R1073/R1053/R1050）与1nF到AGND，网表相应ADC节点未见外部钳位二极管。不能据此保证输入永不超量程：AVCC与VREFP=VCC来自不同LDO，容差、上电次序、放大器饱和摆幅/过冲待核实，但没有证据支持“5V运放直接灌3.3V ADC”的指控。

M1_VBUS分压是 DCBUS→R87 10k→R94 10k→采样点→R102 1k→GND，理想比例1/21；VREFP=3.3V时理论满量程约69.3V，需按实际母线及误差留裕量，不能推定项目使用该电压。采样点D18接VCC钳位，但二极管钳位通常位于VCC以上，不能证明ADC精确量程得到保护；注入电流、断电反灌需另核。M2对应R1087/R1094/R1102，未接U1。

datasheet p101 表4-34：ADC输入0…VREFP，VREFP 2.6…VDDA、上电时也不得高于VDDA；ADC时钟<=42MHz。p101–102 表4-35及采样公式要求结合源阻抗确定采样时间。NTC 10k上拉/热敏电阻与100nF滤波不能以最快采样时间无条件接受；六相电流双/三ADC调度、注入触发、同步和校准均是待核实固件项。

## PWM/BRKIN/编码器/SPI 复用

|功能/网络|U1引脚|复用配置|证据|
|---|---|---|---|
|M1_HIN1/2/3|67 PA8 /68 PA9 /69 PA10|AF1 → TIMER0_CH0/1/2|datasheet pp28、54|
|M1_LIN1/2/3|52 PB13 /53 PB14 /54 PB15|PB13/14 AF2，PB15 AF1 → TIMER0_CH0/1/2_ON|pp27、55|
|M2_HIN1/2/3|63 PC6 /64 PC7 /65 PC8|PC6/7 AF3，PC8 AF2 → TIMER7_CH0/1/2|pp28、55|
|M2_LIN1/2/3|15 PC0 /16 PC1 /17 PC2|AF0 → TIMER7_CH0/1/2_ON|pp24–25、55|
|M1_BRKIN|51 PB12|AF4 → TIMER0_BRKIN|pp27、55|
|M2_BRKIN|31 PA6|AF4 → TIMER7_BRKIN|pp25、54|
|M1_HALL_A/B/C|90 PB4 /91 PB5 /35 PB0|AF1 /AF0 /AF1 → TIMER2_CH0/1/2|pp26、29、54|
|M2_HALL_A/B/C|59 PD12 /60 PD13 /61 PD14|AF1 /AF0 /AF0 → TIMER3_CH0/1/2|pp27–28、56|
|SPI2_SCK/MISO/MOSI|78 PC10 /79 PC11 /80 PC12|AF2 → SPI2|pp29、55|
|M1_SPI1_CS0/M2_SPI1_CS0|1 PE2 /2 PE3|GPIO软件片选可用；不是硬件SPI1_NSS|pp24、56|

两套PWM分别驱动 U7/U1007 FD6288Q的HIN22/23/24和LIN1/2/3，每线10k下拉到GND，网表映射一致。PC7同有TIMER7_CH3_ON(AF2)，必须用AF3才是主输出CH1；PB15、PB5、PD13/14等AF值不统一，固件不能整组硬套相同AF。

PB4复位默认NJTRST，要释放JTAG占用并保留SWD，再配置TIMER2_CH0（manual p486）。正交解码使用CH0/CH1，故两路A/B映射合法（manual p361）；C在CH2支持第三霍尔输入/捕获，不能把三路Hall模式和A/B正交模式视为同一配置；Z索引语义另核。

M1_BRKIN仅U1.51、J201.3、R204.2（10k上拉VCC）；M2_BRKIN仅U1.31、J201.4、R205.2（10k上拉VCC）。manual p332：BRKP=0低有效，BRKP=1高有效，BRKEN=1使能。需核实外接故障源及有效极性/输入路由/使能/关闭状态/死区；上拉本身不产生故障保护。按低有效设计时断线保持高，不是断线失效安全。此为外接系统和固件约束，并非确认接线错误。

SPI片选网络名称含SPI1而总线实际SPI2，只是命名不一致，软件GPIO片选可正常工作。两设备共享总线时需保证非选中MISO高阻，器件型号和固件未在本次核实。

## 勘误

errata V1.1 pp5–8列出I2C 10位从机STOP、CAN发送邮箱、Core访问错误优先级；未列出推翻上述ADC/PWM引脚表的限制。该版适用GD32F505（p5），需按实际芯片Revision核对；“未列”不等同于实物无其他限制。OLED通常为I2C主机用途，但未读固件，不能宣称该限制必然不适用。
