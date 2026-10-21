// Deterministic original educational artwork. No PDF/image input is read here.
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
const out = 'src/assets/hardware';
await mkdir(out, { recursive: true });
const esc = (s) => String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const text = (x,y,s,size=18,anchor='middle') => `<text x="${x}" y="${y}" font-size="${size}" text-anchor="${anchor}">${esc(s)}</text>`;
const box = (x,y,w,h,label,fill='#f4f1e8') => `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="5" fill="${fill}" stroke="#514d40"/>${label ? text(x+w/2,y+h/2+6,label) : ''}`;
const line = (points,arrow=true,dash=false) => `<path d="${points}" fill="none" stroke="#514d40" stroke-width="2"${arrow?' marker-end="url(#arrow)"':''}${dash?' stroke-dasharray="5 4"':''}/>`;
const circle = (x,y,r,fill='none') => `<circle cx="${x}" cy="${y}" r="${r}" stroke="#514d40" stroke-width="2" fill="${fill}"/>`;
const flow = (labels) => labels.map((s,i)=>box(30,15+i*76,260,48,s)+(i<labels.length-1?line(`M160 ${63+i*76} V${85+i*76}`):'')).join('');
const bits = (x,y,value,highlight=-1) => [...value].map((s,i)=>box(x+i*32,y,32,36,'',i===highlight?'#e8cf72':'#f4f1e8')+text(x+i*32+16,y+25,s)).join('');
const figures=[];
function add(id,lesson,after,title,alt,caption,height,body) {
  figures.push({id,lesson,after,title,alt,caption,height,body});
}
add('switching-technologies','basic-configuration','computer-generations','From switching devices to chips',
  'A vacuum-tube envelope, a three-terminal transistor and an integrated chip illustrate increasing integration. They are schematic symbols of construction, not to scale.',
  'Switching technology changed from separate large devices to many circuit elements integrated on one chip.',390,
  `<ellipse cx="65" cy="65" rx="26" ry="42" fill="#f4f1e8" stroke="#514d40"/>${line('M51 99 V120 M65 105 V120 M79 99 V120',false)}${text(205,61,'Vacuum tube')}${text(205,87,'Separate device')}${line('M160 130 V156')}${circle(65,204,30)}${line('M45 204 H62 M62 185 V223 M62 194 L83 180 M62 214 L83 230',false)}${text(205,199,'Transistor')}${text(205,225,'Semiconductor')}${line('M160 250 V276')}${box(35,295,65,55,'IC','#e8cf72')}${[40,55,70,85].map(x=>line(`M${x} 283 V295 M${x} 350 V362`,false)).join('')}${text(210,315,'Integrated circuit')}${text(210,341,'Many elements')}`);
add('computer-forms','basic-configuration','power-example','Different forms, different roles',
  'Original outlines show a rack, a desktop screen, a laptop and a handheld device. Size and shape do not determine whether a computer acts as a server or a client.',
  'A form factor describes physical packaging. Server, workstation and embedded controller describe roles.',275,
  `${box(20,20,70,105,'')}${[40,65,90].map(y=>box(30,y,50,14,'')).join('')}${text(205,72,'Rack system')}${box(25,158,60,40,'')}${line('M55 198 V212 M35 212 H75',false)}${text(205,185,'Desktop')}${box(27,234,55,27,'')}${line('M20 263 H90',false)}${text(205,256,'Portable computer')}`);
add('five-unit-control','basic-configuration','five-unit-flow','Data paths and control paths',
  'The control unit sends dashed command paths to input, storage, ALU and output. Solid arrows carry input to storage, storage to ALU and output, and ALU results back to storage.',
  'Solid arrows carry data; dashed arrows indicate commands. The CPU includes the control unit and ALU. Storage remains a separate functional unit in this model.',420,
  `${box(90,20,140,48,'Control unit','#e8cf72')}${box(20,140,110,50,'Input')}${box(90,245,140,50,'Storage')}${box(190,140,110,50,'Output')}${box(90,350,140,50,'ALU','#e8cf72')}${line('M75 190 V270 H86')}${line('M230 270 H245 V194')}${line('M140 295 V346')}${line('M180 350 V299')}${line('M105 68 V115 H75 V136',true,true)}${line('M160 68 V241',true,true)}${line('M215 68 V115 H245 V136',true,true)}${line('M230 44 H310 V375 H234',true,true)}`);
add('memory-persistence','basic-configuration','stored-program','Working memory and persistent storage',
  'Programs and data move from auxiliary storage into main memory for CPU use. Main RAM loses ordinary state without power; nonvolatile storage retains its recorded state.',
  'Loading is a transfer between two different stores. Nonvolatile storage retains data without power; it still needs backup against loss or failure.',330,
  `${box(40,15,240,55,'CPU')}${line('M145 70 V105')}${line('M175 110 V74')}${box(40,110,240,55,'Main RAM','#e8cf72')}${text(160,190,'Volatile working state')}${line('M145 205 V245')}${line('M175 250 V209')}${box(40,250,240,55,'Auxiliary storage')}`);
add('bit-patterns','data-representation','bits-and-units','Bits, patterns and a byte',
  'A binary tree doubles from two one-bit choices to four two-bit choices. Eight bit cells form one byte, with 256 possible patterns and unsigned values 0 to 255.',
  'Each independent bit doubles the pattern count. Eight bits give 256 patterns, not a greatest unsigned value of 256.',290,
  `${text(160,25,'1 bit → 2 patterns')}${box(65,45,60,36,'0')}${box(195,45,60,36,'1')}${line('M95 81 L55 118',false)}${line('M95 81 L125 118',false)}${line('M225 81 L195 118',false)}${line('M225 81 L265 118',false)}${['00','01','10','11'].map((s,i)=>box(25+i*70,120,60,36,s)).join('')}${text(160,188,'2 bits → 4 patterns')}${bits(32,207,'10100101')}${text(160,274,'1 byte = 8 bits = 256 patterns')}`);
add('radix-grouping','data-representation','grouping-digits','Group from the radix point',
  'The same binary pattern 101101.101 is grouped as 101 101 point 101 for octal 55.5 and as 0010 1101 point 1010 for hexadecimal 2D.A. Only outer padding zeros are added.',
  'Three binary digits select one octal digit; four select one hexadecimal digit. Group separately on each side of the point, padding only the outer ends.',305,
  `${text(160,25,'Binary: 101101.101',20)}${text(160,70,'Octal: groups of 3')}${box(25,90,270,43,'101 | 101 . 101','#e8cf72')}${text(160,160,'5       5  .   5')}${text(160,204,'Hex: groups of 4')}${box(10,220,300,43,'0010 | 1101 . 1010')}${text(160,282,'2        D   .    A')}`);
add('data-format-tree','data-representation','encoding-context','The meaning comes from the format',
  'Data branches into character codes and numeric formats. Numeric formats branch into decimal digit codes and binary formats, with fixed point and floating point under binary.',
  'A bit pattern has no intrinsic character or numeric meaning. The selected format determines how those bits are interpreted.',350,
  `${box(100,10,120,40,'Data')}${line('M160 50 V75 H80 V95')}${line('M160 75 H240 V95')}${box(5,100,150,50,'Characters')}${box(165,100,150,50,'Numbers')}${line('M240 150 V170 H85 V195')}${line('M240 170 V195')}${box(5,200,155,50,'Decimal codes')}${box(175,200,140,50,'Binary')}${line('M245 250 V270 H85 V295')}${line('M245 270 V295')}${box(10,300,145,40,'Fixed point')}${box(165,300,150,40,'Floating point')}`);
add('character-code','data-representation','character-encoding','A character code is a lookup',
  'The Latin capital letter A is U+0041 in Unicode and 0x41 in ASCII. Its UTF-8 byte is hexadecimal 41, binary 01000001. A grid uses high nibble 4 and low nibble 1 to locate hexadecimal 41.',
  'Split the byte into two nibbles to locate its hexadecimal code. A code point and an encoded byte sequence are different concepts.',330,
  `${box(105,10,110,55,'A', '#e8cf72')}${text(160,97,'Unicode: U+0041')}${text(160,125,'ASCII / UTF-8 byte: 0x41')}${bits(32,150,'01000001')}${text(160,220,'High nibble 4; low nibble 1')}${box(60,245,200,60,'4 × 16 + 1 = 65')}`);
add('decimal-packing','data-representation','decimal-codes','Decimal digits packed into nibbles',
  'Decimal 672 becomes BCD nibbles 0110, 0111, 0010. A common signed packed representation is hexadecimal 67 2C for positive 672. EBCDIC-style zoned positive digits are F6 F7 C2, with the final zone holding the sign.',
  'In this explicitly chosen convention, C is a positive sign and D a negative sign. Packed 67 2C uses two bytes; zoned F6 F7 C2 uses three. Sign codes depend on the format.',375,
  `${text(160,25,'Decimal digits: 6   7   2',20)}${text(160,70,'BCD: one nibble per digit')}${text(160,102,'0110 | 0111 | 0010')}${line('M160 120 V150')}${box(25,155,270,50,'Packed: 67 | 2C','#e8cf72')}${text(160,236,'C = positive sign nibble')}${box(25,265,270,50,'Zoned: F6 | F7 | C2')}${text(160,347,'Pack / unpack for I/O formats')}`);
add('signed-range','data-representation','decimal-codes','Two signed four-bit interpretations',
  'For four bits, sign-magnitude uses 0000 for plus zero and 1000 for minus zero, spanning minus 7 to plus 7. Two’s complement uses one zero, spans minus 8 to plus 7, and gives 1000 the value minus 8.',
  'The same 1000 pattern means −0 in sign-magnitude and −8 in two’s complement. Two’s complement uses all 16 patterns for 16 distinct integer values.',335,
  `${text(160,25,'Four bits: 16 patterns',20)}${box(20,55,280,90,'')}${text(160,85,'Sign-magnitude')}${text(160,115,'−7 … −0, +0 … +7')}${box(20,170,280,90,'','#e8cf72')}${text(160,200,'Two’s complement')}${text(160,230,'−8 … −1, 0 … +7')}${text(160,300,'1000 = −8; 0111 = +7')}`);
add('shift-paths','data-representation','shifting-bits','Three ways to shift right',
  'Starting with 10010110, logical right shift inserts zero to give 01001011; arithmetic right shift repeats one to give 11001011; rotate right wraps the discarded zero to give 01001011. Rotation differs from a shift even when this example’s results match.',
  'Eight-bit operations, shifted once. Logical fill is zero; arithmetic right fill repeats the sign; rotation wraps the outgoing bit. Left shifts can discard significant bits and overflow.',375,
  `${text(160,25,'Start: 10010110',20)}${text(160,75,'Logical: insert 0')}${bits(32,90,'01001011',0)}${text(160,170,'Arithmetic: repeat sign 1')}${bits(32,185,'11001011',0)}${text(160,265,'Rotate: wrap outgoing 0')}${bits(32,280,'01001011',0)}${line('M284 336 V355 H36 V320',true,true)}`);
add('cpu-data-path','cpu-and-main-memory','instruction-trace','Trace an instruction through the CPU',
  'Step 1: PC sends an instruction address to memory. Step 2: memory returns the instruction to IR, which feeds the decoder. Step 3: the decoder directs registers and ALU. Step 4: an operand is read and the ALU result is written back. PC advances or branches separately.',
  'PC holds an instruction address; IR holds the fetched instruction. The decoder directs an operation, while the ALU operates on data. Solid paths move addresses/data; the dashed path carries control.',465,
  `${box(30,10,260,60,'Main memory')}${box(15,105,290,310,'','#fffdf7')}${text(160,126,'CPU',20)}${box(30,140,100,45,'PC')}${box(185,140,100,45,'IR')}${line('M80 140 V74')}${line('M235 70 V136')}${line('M235 185 V216')}${box(170,220,120,45,'Decoder','#e8cf72')}${line('M230 265 V295 H95 V321',true,true)}${box(30,325,130,50,'Registers')}${line('M160 350 H181')}${box(185,325,100,50,'ALU','#e8cf72')}${line('M235 375 V395 H95 V379')}${line('M30 40 H5 V350 H26')}${text(160,452,'Fetch → decode → execute')}`);
add('clock-buses','cpu-and-main-memory','bus-rate-example','Timing and three bus roles',
  'Two rising edges delimit one clock period. CPU sends addresses and read/write control to memory; a bidirectional data path carries values. A 100 MHz clock has a 10 nanosecond period.',
  'Clock cycles provide timing. Address, data and control have different roles; one cycle need not equal one instruction or one useful bus transfer.',355,
  `${line('M30 70 H60 V30 H105 V70 H150 V30 H195 V70 H240 V30 H285',false)}${line('M60 90 H150',false)}${text(105,120,'1 period')}${text(160,155,'100 MHz → 10 ns')}${box(10,205,90,130,'CPU')}${box(220,205,90,130,'RAM')}${line('M100 225 H216')}${text(160,211,'Address')}${line('M100 270 H216')}${line('M220 278 H104')}${text(160,259,'Data')}${line('M100 320 H216',true,true)}${text(160,308,'Control')}`);
add('memory-cells','cpu-and-main-memory','memory-device-table','Two ways to retain a working bit',
  'A conceptual DRAM cell connects a data line through a selected transistor to a capacitor, whose charge must be refreshed. SRAM uses feedback to retain state while powered. Both are volatile.',
  'A capacitor stores charge in DRAM; feedback maintains a state in SRAM while power is supplied. These are conceptual models, not transistor-level manufacturing layouts.',410,
  `${text(160,28,'DRAM: charge',20)}${line('M40 65 H130 M130 45 V85 M140 65 H220 V112',false)}${line('M190 112 H250 M190 121 H250 M220 122 V150',false)}${text(160,178,'Selected access switch')}${text(160,210,'Capacitor → refresh needed')}${text(160,260,'SRAM: feedback',20)}${box(25,285,105,45,'State')}${box(190,285,105,45,'Feedback')}${line('M130 300 H186')}${line('M190 320 H134')}${text(160,385,'Power sustains the stored bit')}`);
add('memory-address-grid','cpu-and-main-memory','memory-access-flow','An address selects a location',
  'Address 2 enters a decoder, which selects row 2 from a four-row memory. The selected stored value is hexadecimal A6; the address 2 and data A6 are different.',
  'This four-location memory has two address bits and one byte per location: 2² × 8 = 32 bits total. The address is not the byte stored there.',340,
  `${box(15,15,290,50,'Address bus: binary 10')}${line('M160 65 V90')}${box(60,95,200,45,'Address decoder','#e8cf72')}${line('M160 140 V165')}${['0 : 00','1 : 3F','2 : A6  ← selected','3 : 18'].map((s,i)=>box(35,170+i*35,250,35,s,i===2?'#e8cf72':'#f4f1e8')).join('')}${text(160,335,'Data bus returns byte A6')}`);
add('instruction-format','cpu-and-main-memory','instruction-fields','An instruction contains fields',
  'An illustrative sixteen-bit instruction has a four-bit opcode, a four-bit register field and an eight-bit operand field. The format is a teaching example, not a particular ISA.',
  'Instruction layout is defined by the ISA. An operand field can encode a literal, register or address information; it is not always a final memory address.',250,
  `${text(160,28,'Example 16-bit instruction',20)}${box(30,60,260,45,'Opcode · 4 bits','#e8cf72')}${box(30,110,260,45,'Register · 4 bits')}${box(30,160,260,55,'Operand field · 8 bits')}${text(160,242,'4 + 4 + 8 = 16 bits')}`);
add('operand-addressing','cpu-and-main-memory','addressing-table','Follow the dereference',
  'Instruction field A is 40. Immediate mode uses operand 40; direct mode reads M[40], which is 700; indirect mode follows 700 to M[700], which is 12. Indexed addressing with R equal to 3 selects address 43.',
  'Each arrow through a memory box is a dereference. Immediate 40, direct 700 and indirect 12 are three different operands from the same instruction field.',405,
  `${box(40,10,240,45,'Field A = 40','#e8cf72')}${text(160,92,'Immediate → value 40')}${line('M160 110 V132')}${box(40,137,240,50,'M[40] = 700')}${text(160,216,'Direct → value 700')}${line('M160 230 V252')}${box(40,257,240,50,'M[700] = 12')}${text(160,343,'Indirect → value 12')}${text(160,385,'Indexed: EA = 40 + 3 = 43')}`);
// ANSI-style shapes: AND has a flat input edge; OR/XOR have curved input edges.
const gate = (type,x,y) => {
  let p = type==='NOT' ? `<path d="M${x} ${y} L${x+48} ${y+25} L${x} ${y+50} Z" fill="#f4f1e8" stroke="#514d40"/>` : type==='AND'||type==='NAND' ? `<path d="M${x} ${y} H${x+25} A25 25 0 0 1 ${x+25} ${y+50} H${x} Z" fill="#f4f1e8" stroke="#514d40"/>` : `<path d="M${x} ${y} Q${x+30} ${y+25} ${x} ${y+50} Q${x+45} ${y+50} ${x+65} ${y+25} Q${x+45} ${y} ${x} ${y} Z" fill="#f4f1e8" stroke="#514d40"/>`;
  if(type==='XOR')p+=`<path d="M${x-8} ${y} Q${x+22} ${y+25} ${x-8} ${y+50}" fill="none" stroke="#514d40"/>`;
  const end=type==='NOT'?48:type==='AND'||type==='NAND'?50:65;
  if(['NOT','NAND','NOR'].includes(type))p+=circle(x+end+5,y+25,5,'#fffdf7');
  return p;
};
add('logic-symbols','cpu-and-main-memory','logic-truth-table','Read the gate symbol',
  'AND has a flat input side, OR a curved input side and XOR an extra curved line. NOT is a triangle with an output bubble. NAND is AND with a bubble; NOR is OR with a bubble. A bubble means inversion.',
  'Gate shape identifies the operation. A small output bubble negates it. Compare the connections with the truth table above; the extra input-side curve distinguishes XOR from OR.',480,
  ['AND','OR','XOR','NOT','NAND','NOR'].map((s,i)=>{const y=15+i*76,x=['OR','NOR','XOR'].includes(s)?136:125;return text(48,y+31,s)+gate(s,125,y)+line(`M${x} ${y+(s==='NOT'?25:12)} H100`,false)+(['NOT'].includes(s)?'':line(`M${x} ${y+38} H100`,false))+line(`M${s==='NOT'?183:s==='AND'?175:s==='NAND'?185:s==='NOR'?200:190} ${y+25} H275`,false);}).join(''));
add('sr-latch','cpu-and-main-memory','adder-example','Feedback stores a state',
  'Two cross-coupled NAND gates form an active-low SR latch. S_n enters the upper gate and R_n the lower. Q feeds the lower feedback input; Q-bar feeds the upper feedback input. S_n=0 R_n=1 sets Q; S_n=1 R_n=0 resets Q; both one hold; both zero is forbidden.',
  'Active-low NAND SR latch, matching the source’s NAND convention. The suffix _n marks a low-active input. S_n=R_n=1 holds; 01 sets; 10 resets; 00 forces both outputs high and is forbidden.',335,
  `${text(30,45,'S_n')}${text(30,180,'R_n')}${gate('NAND',100,20)}${gate('NAND',100,155)}${line('M50 35 H100',false)}${line('M50 170 H100',false)}${line('M160 45 H285',false)}${line('M160 180 H285',false)}${text(290,33,'Q')}${text(285,210,'Q̅')}${line('M240 45 V100 L65 130 V193 H100',false)}${line('M240 180 V125 L65 95 V58 H100',false)}${circle(240,45,3,'#514d40')}${circle(240,180,3,'#514d40')}${text(160,250,'S_n R_n: 11 hold · 01 set')}${text(160,283,'10 reset · 00 forbidden')}`);
add('xor-network','cpu-and-main-memory','logic-truth-table','Construct XOR from two cases',
  'Input A and inverted B feed the upper AND gate. Inverted A and B feed the lower AND gate. The two AND outputs feed OR, so Y equals A AND NOT B OR NOT A AND B.',
  'XOR is true in exactly the two unequal-input cases. The labeled negations are part of the wiring; omitting either changes the function.',290,
  `${text(35,33,'A')}${text(35,58,'NOT B')}${text(35,188,'NOT A')}${text(35,213,'B')}${gate('AND',110,15)}${gate('AND',110,170)}${line('M70 27 H110 M70 53 H110 M70 182 H110 M70 208 H110',false)}${line('M160 40 H180 V110 H221',false)}${line('M160 195 H180 V136 H221',false)}${gate('OR',210,98)}${line('M275 123 H300',false)}${text(302,153,'Y')}${text(160,270,'Y = (A AND ¬B) OR (¬A AND B)')}`);
add('adders','cpu-and-main-memory','adder-example','A full adder from two half adders',
  'Half adder 1 takes A and B and gives intermediate sum s1 and carry c1. Half adder 2 takes s1 and carry-in, and gives sum and carry c2. OR combines c1 and c2 into carry-out.',
  'Each half adder computes XOR for its sum and AND for its carry. OR combines the two carry paths: carry-out = AB OR (carry-in AND (A XOR B)).',420,
  `${text(85,25,'A, B')}${line('M85 40 V60')}${box(20,65,130,65,'Half adder 1')}${line('M85 130 V195')}${text(55,170,'s1')}${line('M150 95 H195 V332 H206')}${text(218,165,'c1')}${text(260,215,'Carry-in')}${line('M230 225 H154')}${box(20,200,130,65,'Half adder 2','#e8cf72')}${line('M85 265 V308')}${text(85,338,'Sum')}${line('M150 240 H175 V358 H206')}${text(154,290,'c2')}${box(210,320,75,50,'OR')}${line('M247 370 V388')}${text(247,415,'Carry-out')}`);
add('cache-paths','cpu-and-main-memory','cache-and-interleaving','Buffering at different levels',
  'CPU registers connect through primary and secondary cache to main memory, and then through a disk-cache role to storage. A miss continues down the hierarchy; a hit returns earlier. A disk cache may use part of main RAM.',
  'Each buffer bridges levels with different access costs. A disk cache may occupy main RAM rather than being a separate physical chip. Arrows show a read lookup sequence, not all coherence traffic.',400,
  `${flow(['Registers','L1 / L2 cache','Main memory','Disk-cache role','Storage device'])}`);
add('bank-interleaving','cpu-and-main-memory','cache-and-interleaving','Distribute successive addresses',
  'Four memory banks contain addresses 0,4,8; 1,5,9; 2,6,10; and 3,7,11. A controller can overlap operations across banks. The bank number is address modulo four in this simplified word-addressed model.',
  'Successive word addresses go to different banks in this simplified mapping. Interleaving can improve sustained throughput; it does not divide every access latency by four.',285,
  `${box(35,10,250,45,'Memory controller')}${[0,1,2,3].map((n)=>{let x=8+n*78;return line(`M160 55 V80 H${x+35} V105`)+box(x,110,70,155,'',n%2?'#f4f1e8':'#e8cf72')+text(x+35,140,`Bank ${n}`)+[n,n+4,n+8].map((v,i)=>text(x+35,177+i*30,v)).join('');}).join('')}`);
add('pipeline-stalls','cpu-and-main-memory','pipeline-example','A stall delays following work',
  'A three-stage pipeline takes a bubble when instruction I2 cannot execute. In cycles 1 through 6, I1 runs F D E; I2 runs F D wait E; I3 runs F wait D E. A deeper pipeline splits stages but still must handle dependencies.',
  'F = fetch, D = decode, E = execute; “wait” is a bubble. Throughput falls when a stage cannot advance. Splitting stages in a super-pipeline does not remove dependencies.',310,
  `${text(160,25,'Cycles → 1  2  3  4  5  6',20)}${['I1: F D E · · ·','I2: · F D wait E ·','I3: · · F wait D E'].map((s,i)=>box(15,50+i*60,290,50,s,i===1?'#e8cf72':'#f4f1e8')).join('')}${text(160,260,'Deeper pipeline: smaller stages')}${text(160,290,'F → D1 → D2 → E1 → E2')}`);
add('disk-geometry-figure','auxiliary-storage','disk-geometry','Track, sector, head and cylinder',
  'A disk surface has concentric tracks and sector wedges. The read/write head sits over one track. A second view marks the same-radius tracks on three surfaces as one cylinder.',
  'A track circles one recording surface; sectors divide recording regions. Matching-radius tracks across surfaces form the simplified cylinder model. The drawing is not to scale.',485,
  `${[35,60,85,110].map(r=>circle(160,140,r)).join('')}${line('M160 140 L245 70 M160 140 L270 140',false)}${text(260,44,'Sector')}${line('M265 48 L240 80')}${box(17,123,90,30,'Head','#e8cf72')}${line('M105 137 H126')}${text(90,275,'Circular tracks')}${[325,370,415].map(y=>`<ellipse cx="160" cy="${y}" rx="115" ry="25" fill="#f4f1e8" stroke="#514d40"/><ellipse cx="160" cy="${y}" rx="65" ry="14" fill="none" stroke="#514d40"/>`).join('')}${line('M95 325 V415 M225 325 V415',false,true)}${text(160,472,'Same radius → cylinder')}`);
add('record-blocks','auxiliary-storage','records-and-blocks','Records, blocks and unused space',
  'A 512-byte block contains five 100-byte records and 12 unused bytes. A second schematic shows variable-length recorded blocks separated by interblock gaps, distinct from unused space inside a block.',
  'Five 100-byte records fit in 512 bytes without spanning. Unused bytes inside an allocated block differ from physical interblock gaps; the recording model must be stated.',350,
  `${text(160,25,'512-byte block',20)}${[0,1,2,3,4].map(i=>box(35,45+i*35,250,35,`Record ${i+1} · 100 bytes`)).join('')}${box(35,220,250,35,'12 bytes unused','#e8cf72')}${text(160,292,'Variable-block recording:')}${box(10,310,100,32,'Block A')}${text(155,334,'gap')}${box(210,310,100,32,'Block B')}`);
add('disk-access-timeline','auxiliary-storage','disk-access-model','Three parts of a disk read',
  'A timeline separates head movement (seek), waiting for rotation and transferring the requested bytes. At 7200 rpm, a rotation is 8.333 milliseconds and average rotational waiting is 4.167 milliseconds.',
  'Seek positions the head, rotation brings the sector under it, and transfer moves bytes. Controller overhead is added separately when specified. Segment lengths here are illustrative.',335,
  `${flow(['1. Seek: move head','2. Wait for sector','3. Transfer requested bytes'])}${text(160,270,'7,200 rpm → 8.333 ms / turn')}${text(160,304,'Average wait → 4.167 ms')}`);
add('io-processing','input-output','io-goals','From physical input to output',
  'A document scanner produces image data, memory and the CPU process it, and a printer produces a physical page. Input and output are relative to the computer.',
  'A multifunction device can contain all three stages. Scanning supplies image data; recognition or editing is processing; printing is output.',250,
  flow(['Scanner → image data','Memory + CPU processing','Printer → physical page']));
add('keyboard-signal','input-output','keyboard-input','One press, several contact transitions',
  'A raw key-contact waveform briefly toggles after the press and then stays high. A debounced waveform changes once after a settling delay. This differs from deliberate held-key repeat.',
  'Contact bounce can create several electrical transitions for one press. A debounce method waits or filters; the exact delay depends on the design.',260,
  `${text(160,25,'Raw contact',20)}${line('M20 95 H70 V50 H80 V95 H90 V50 H102 V95 H112 V50 H300',false)}${text(160,145,'After debouncing',20)}${line('M20 215 H140 V170 H300',false)}${line('M70 110 H140',false,true)}${text(160,252,'Time → (illustrative delay)')}`);
add('paper-readers','input-output','paper-reader-table','Recognition and capture differ',
  'OCR recognizes the printed glyph A; OMR reads a filled option position; a barcode reader decodes bars; MICR senses magnetic characters; a scanner captures pixels before any recognition.',
  'OCR reads character shapes; OMR reads marks at known positions; MICR senses magnetic characters. Capturing an image is different from identifying its contents.',375,
  `${text(50,45,'A',30)}${line('M85 40 H130')}${text(230,46,'OCR → character')}${[0,1,2].map(n=>circle(30+n*25,110,7,n===1?'#514d40':'none')).join('')}${line('M100 110 H135')}${text(235,116,'OMR → position')}${[0,1,2,3,4,5,6,7].map(n=>`<rect x="${18+n*10}" y="160" width="${n%2?3:6}" height="34" fill="#514d40"/>`).join('')}${line('M110 180 H135')}${text(235,186,'Bars → code')}${text(55,255,'Magnetic',18)}${line('M110 250 H135')}${text(235,255,'MICR → symbols')}${box(15,305,90,40,'Pixels')}${line('M110 325 H135')}${text(235,331,'Scan → image')}`);
add('touch-coordinates','input-output','pointing-input','Relative motion or absolute position',
  'A mouse reports a movement of plus 5 in x and minus 2 in y. A touch or digitizer surface identifies a point with absolute x,y coordinates inside its bounds. These are different input models.',
  'A mouse normally reports movement relative to a previous position. A touch panel or digitizer can locate a point on its surface; sensing technology and coordinate interpretation are separate.',345,
  `${text(160,25,'Mouse: change in position',20)}${line('M65 120 L235 60')}${text(160,150,'Δx = +5; Δy = −2')}${box(35,190,250,120,'')}${line('M55 290 H265 M55 290 V205',false)}${circle(210,230,6,'#e8cf72')}${text(160,334,'Touch: a point (x, y)')}`);
add('pixel-grid','input-output','display-calculations','A glyph is a grid of samples',
  'A five-by-seven binary pixel grid forms an A from 35 samples. RGB pixels can use eight bits each for red, green and blue, totaling 24 bits or three bytes per pixel.',
  'This original 5 × 7 glyph contains 35 samples. Resolution counts samples; color depth counts bits per sample. At 24 bits/pixel, a packed RGB image uses three bytes per pixel.',355,
  `${['01110','10001','10001','11111','10001','10001','10001'].map((row,y)=>[...row].map((v,x)=>`<rect x="${75+x*34}" y="${10+y*34}" width="32" height="32" fill="${v==='1'?'#514d40':'#f4f1e8'}" stroke="#d3cdbf"/>`).join('')).join('')}${text(160,273,'5 columns × 7 rows')}${box(10,295,95,40,'R: 8 bits')}${box(112,295,95,40,'G: 8 bits')}${box(214,295,95,40,'B: 8 bits')}`);
add('impact-printer','input-output','printer-types','Pins transfer ink through a ribbon',
  'An impact print head pushes pins toward an ink ribbon, which contacts paper. Pin positions form dots. It contrasts with inkjet droplets and laser-transferred toner.',
  'Mechanical impact transfers ink from the ribbon to the paper. Inkjet and laser printing form marks by different mechanisms; they do not strike an ink ribbon.',290,
  `${box(55,15,210,60,'Print head')}${[95,130,165,200,235].map(x=>line(`M${x} 75 V140`,false)).join('')}${line('M160 145 V172')}${box(20,180,280,25,'','#e8cf72')}${text(160,235,'Ink ribbon')}${line('M20 255 H300',false)}${text(160,282,'Paper receives dots')}`);
add('output-paths','input-output','other-output-examples','A path drawing or a projected image',
  'A plotter pen follows an x-y path to mark a physical surface. A projector sends an image using light onto a screen. Both are output, but they produce different physical results.',
  'A plotter controls a tool path. A projector casts light. A shared digital drawing can be represented by either kind of output without making their mechanisms identical.',300,
  `${box(15,10,290,120,'')}${line('M45 100 H100 V45 H200 V100 H270',false)}${text(160,156,'Plotter: controlled pen path')}${box(15,200,75,40,'Light')}${line('M90 210 L265 185 M90 230 L265 265',false)}${box(265,180,30,90,'')}${text(160,295,'Projector: light on screen')}`);
add('io-transfer','input-output','io-control-comparison','Who moves the block?',
  'Programmed transfer routes data from device through the CPU to memory. DMA routes data between a device controller and memory after CPU setup, then notifies the CPU on completion.',
  'DMA reduces per-byte CPU instructions. The CPU still sets up the transfer and handles completion; bus and memory resources are still used.',350,
  `${text(160,25,'Programmed transfer',20)}${box(10,50,90,45,'Device')}${box(115,50,90,45,'CPU','#e8cf72')}${box(220,50,90,45,'RAM')}${line('M100 73 H111')}${line('M205 73 H216')}${text(160,150,'DMA block transfer',20)}${box(10,190,130,50,'Controller')}${box(215,190,95,50,'RAM')}${line('M140 215 H211')}${box(95,290,130,45,'CPU','#e8cf72')}${line('M145 290 V260 H75 V244',true,true)}${line('M125 240 V270 H195 V286',true,true)}${text(160,180,'Device ↔ controller')}`);
add('interface-topologies-figure','input-output','interface-topologies','Star, cascade and daisy chain',
  'A star connects devices to one hub. A cascade connects a hub to another hub, with devices branching from them. A daisy chain connects onward through devices, with a terminator when that interface requires one.',
  'These are connection patterns, not interchangeable USB modes. USB uses hubs in a tiered star; a legacy SCSI daisy chain requires termination under its specified rules.',435,
  `${text(160,25,'Star',20)}${box(115,50,90,35,'Hub')}${line('M115 67 H65 V100')}${line('M160 85 V100')}${line('M205 67 H255 V100')}${[30,125,220].map(x=>box(x,105,70,35,'Device')).join('')}${text(160,195,'Cascade',20)}${box(20,215,100,35,'Hub 1')}${box(200,215,100,35,'Hub 2')}${line('M120 232 H196')}${line('M70 250 V270')}${line('M250 250 V270')}${box(20,275,100,35,'Device')}${box(200,275,100,35,'Device')}${text(160,355,'Daisy chain',20)}${box(5,375,80,35,'Host')}${box(115,375,85,35,'Dev 1')}${box(230,375,85,35,'Dev 2')}${line('M85 392 H111',false)}${line('M200 392 H226',false)}`);

add('radix-conversion-steps','data-representation','radix-worked','Read integer and fraction digits differently',
  'Repeated division of 26 by two yields remainders 0,1,0,1,1, read upward as 11010. Repeated multiplication of 0.625 by two yields integer parts 1,0,1, read downward as .101.',
  'Integer remainders are read from the final division back upward. Fractional integer parts are read in the order generated. The result is 11010.101₂.',425,
  `${text(160,28,'26: divide by 2',20)}${['26 → 13, remainder 0','13 → 6, remainder 1','6 → 3, remainder 0','3 → 1, remainder 1','1 → 0, remainder 1'].map((s,i)=>text(145,65+i*28,s)).join('')}${line('M295 182 V50')}${text(160,235,'0.625: multiply by 2',20)}${text(140,275,'0.625 × 2 = 1.25 → 1')}${text(140,310,'0.25 × 2 = 0.5 → 0')}${text(140,345,'0.5 × 2 = 1.0 → 1')}${line('M295 265 V350')}${text(160,405,'Integer ↑     Fraction ↓')}`);
add('repeating-fraction','data-representation','grouping-digits','A recurring remainder creates recurring bits',
  'Starting with decimal fraction 0.1, repeated multiplication by two emits bits 0,0,0,1,1 and leaves remainders 0.2,0.4,0.8,0.6,0.2. The remainder 0.2 repeats, so subsequent bits repeat 0011.',
  '0.1₁₀ = 0.000110011…₂. Once the same fractional remainder returns, the subsequent digits repeat. Finite storage must round or truncate this expansion.',390,
  `${text(160,25,'Fraction × 2 → bit, remainder',18)}${['0.1 × 2 → 0, 0.2','0.2 × 2 → 0, 0.4','0.4 × 2 → 0, 0.8','0.8 × 2 → 1, 0.6','0.6 × 2 → 1, 0.2'].map((s,i)=>box(30,45+i*55,260,45,s,i===4?'#e8cf72':'#f4f1e8')).join('')}${line('M290 285 H310 V120 H294',true,true)}${text(160,365,'Remainder 0.2 repeats → loop')}`);
add('float-formats','data-representation','floating-point-layout','Normalize, then store the fields',
  'Binary 1010.1 normalizes to 1.0101 times two cubed. For binary32 the sign is zero, biased exponent is 130 and the stored fraction begins 0101. Binary32 has field widths 1,8,23; binary64 has 1,11,52 and bias 1023.',
  'For normal finite values, the leading 1 is implicit. Binary32 has 24 significant binary digits including that 1; binary64 has 53. Zero/subnormal and all-ones exponent fields need separate rules.',375,
  `${text(160,25,'10.5 = 1010.1₂',20)}${line('M160 45 V65')}${box(15,70,290,45,'1.0101₂ × 2³','#e8cf72')}${text(160,150,'Binary32: S=0; E=3+127=130')}${text(160,181,'Stored fraction: 0101…')}${box(15,220,290,45,'32 bits: 1 + 8 + 23')}${box(15,280,290,45,'64 bits: 1 + 11 + 52')}${text(160,351,'Binary64 exponent bias: 1023')}`);
add('numeric-errors','data-representation','error-types','Precision and range are different limits',
  'With three significant decimal digits, 1.234 rounds to 1.23. Subtracting the rounded 1.234 and 1.233 gives zero instead of the exact 0.001. Adding 1 to 1.00 million can lose the small term. Underflow concerns tiny magnitudes near zero; overflow concerns excessive magnitude of either sign.',
  'Illustrative three-significant-digit decimal arithmetic. Cancellation and lost small terms concern precision. Underflow concerns tiny magnitudes near zero, not simply any value below a signed minimum.',385,
  `${text(160,25,'Round: 1.234 → 1.23',20)}${box(10,60,300,90,'')}${text(160,90,'Cancellation after rounding:')}${text(160,125,'1.23 − 1.23 = 0')}${box(10,175,300,90,'','#e8cf72')}${text(160,205,'Small term may disappear:')}${text(160,240,'1.00 × 10⁶ + 1 → 1.00 × 10⁶')}${text(160,315,'Underflow: tiny |value|')}${text(160,350,'Overflow: excessive |value|')}`);

const inventory=JSON.parse(await readFile('docs/development/figures/chapter1-inventory.json','utf8'));
const manifest=[];
for(const f of figures) {
  const svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 ${f.height}" width="320" height="${f.height}" role="img" aria-labelledby="${f.id}-title ${f.id}-desc"><title id="${f.id}-title">${esc(f.title)}</title><desc id="${f.id}-desc">${esc(f.alt)}</desc><defs><marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto-start-reverse"><path d="M0 0 L6 3 L0 6 Z" fill="#514d40"/></marker></defs><g fill="#302e27" font-family="system-ui, sans-serif">${f.body}</g></svg>\n`;
  // Marker IDs must be document-unique because diagrams are inline, including duplicate anchors.
  const unique=svg.replaceAll('id="arrow"',`id="${f.id}-arrow"`).replaceAll('url(#arrow)',`url(#${f.id}-arrow)`);
  await writeFile(`${out}/${f.id}.svg`,unique);
  const refs=inventory.regions.filter(r=>r.equivalent===f.id);
  if(!refs.length)throw new Error(`No reviewed source mapping for ${f.id}`);
  manifest.push({id:f.id,lesson:f.lesson,after:f.after,title:f.title,alt:f.alt,caption:f.caption,asset:`${f.id}.svg`,sha256:createHash('sha256').update(unique).digest('hex'),authorship:'authored-original',sourceReuse:false,editionId:inventory.editionId,sourceRegions:refs.map(r=>r.id),sourcePages:[...new Set(refs.map(r=>r.printedPage))].sort((a,b)=>a-b)});
}
await writeFile('src/content/hardware-figures.json',JSON.stringify(manifest,null,2)+'\n');
console.log(`Authored ${manifest.length} original SVG figures; no source crops read or copied.`);
