---
id: fe-v1-ch01-s03
title: Central Processing Unit and Main Memory Unit
---

<div id="cpu-goals" data-reading-block>

This section connects the five-unit model to an instruction actually running. You will identify CPU registers, calculate memory addresses and bus throughput, build simple arithmetic from gates, and explain how caches and parallel execution improve performance. Keep the distinction between an address, an instruction and an operand in view throughout.

</div>

<h2 id="cpu-configuration" data-reading-block>Configuration of CPU</h2>

<div id="cpu-register-table" data-reading-block>

The **control unit** coordinates transfers and execution. The **ALU** performs arithmetic, comparisons and logical operations. Registers provide small, fast working locations. The instruction decoder interprets an instruction's operation code; the CPU's clock provides timing events that organize these activities.

<a class="concept-highlight" id="concept-cpu-registers" data-concept="cpu-registers" href="/practice/cpu-registers/"><mark>CPU registers</mark> ↗</a> have distinct roles. Similar names do not mean that two registers store the same kind of value.

| Register | What it holds | Distinguishing question |
|---|---|---|
| Instruction register (IR) | The fetched instruction being interpreted | Which operation and operand fields were fetched? |
| Program counter (PC), instruction address register | An instruction address | Where is the next instruction to fetch? |
| General-purpose register | Operands, addresses or results as permitted by the architecture | What working value does this instruction need? |
| Accumulator | An arithmetic operand or result | Where is the running arithmetic result? |
| Base and index registers | Values used to calculate effective addresses | Where does a region or indexed element begin? |
| Flag/status register | Conditions such as zero, negative, carry or overflow | Which condition can a later branch test? |
| Stack pointer (SP) | The current stack position | Where do push and pop operate? |
| Program Status Word (PSW) | Architecturally defined execution-state information | What state must be saved or restored? |

A stack is last-in, first-out storage. Push saves an item and pop retrieves the most recently saved item. The stack's growth direction and whether SP points to an occupied or next-free location depend on the architecture; neither changes the register's role.

**Clock period** is the reciprocal of clock frequency. A 100 MHz clock has a period of 1/(100×10⁶) s = 10 ns. An instruction may take more than one clock cycle, and different designs do different amounts of work per cycle. For a simplified instruction stream:

<p class="formula">CPU time = instruction count × average cycles per instruction ÷ clock frequency</p>

For 2 million instructions, average CPI 3 and a 200 MHz clock, time = (2×10⁶×3)/(200×10⁶) = **0.03 s**. Comparing clock rates alone would ignore both instruction count and CPI.

</div>

<div id="bus-rate-example" data-reading-block>

An **address bus** identifies a location, a **data bus** transfers the value, and a **control bus** carries signals such as read/write and completion. Internal buses connect parts of a CPU; external/system, memory, I/O and expansion buses connect broader parts of a system. Serial links send bits sequentially; parallel buses transfer multiple bits at once. A physical data width need not equal the processor's advertised word width.

<a class="concept-highlight" id="concept-bus-transfer" data-concept="bus-transfer" href="/practice/bus-transfer/"><mark>Bus transfer rate</mark> ↗</a> depends on useful transfers per second, not just the input clock:

<p class="formula">bytes/s = (data bits per transfer ÷ 8) × (input clock cycles/s ÷ input cycles per transfer)</p>

A 32-bit bus using a 50 MHz input clock and two input cycles per transfer carries 4 × 25×10⁶ = **100 MB/s** in a decimal theoretical model. Waiting, arbitration and protocol overhead may reduce useful throughput. DDR-style signaling can use both clock edges, but apply that multiplier only when the transfer rules specify it. Historical PCI uses a shared parallel bus; PCI Express uses serial lanes. Their versions, lane counts and protocols matter more than the superficial “serial versus parallel” label.

</div>

<h2 id="main-memory" data-reading-block>Main Memory Configuration</h2>

<h3 id="memory-devices" data-reading-block>Memory Devices</h3>

<div id="memory-device-table" data-reading-block>

Semiconductor memory stores state in electronic circuits. MOS/CMOS and bipolar technologies describe device construction; they do not by themselves tell us whether a finished memory is volatile. For the functional distinction, ask how it retains bits and whether power or refresh is needed.

| Memory | Retention and behavior | Typical role |
|---|---|---|
| SRAM | State-holding circuits; volatile, no periodic refresh while powered | Fast caches and small working stores |
| DRAM | Charge-based cells; volatile and periodically refreshed | Dense, economical main memory |
| Mask ROM | Contents set during manufacture; nonvolatile | Fixed firmware or data |
| PROM | User-programmable once under the specified technology | Permanently programmed information |
| UV-EPROM | Erased with ultraviolet light, then reprogrammed | Historical reusable firmware storage |
| EEPROM | Electrically erased/reprogrammed; finite endurance | Small persistent settings |
| Flash memory | Electrically erasable memory with block erase; nonvolatile | Firmware, SSDs and removable storage |

“Random access” describes reaching locations without sequentially passing through all earlier ones. It does not mean random contents. **Volatile** means ordinary stored state is lost when its sustaining power is removed. A flash-based SSD is semiconductor memory, yet is not volatile main DRAM. Cache does not replace the need to understand this distinction.

</div>

<h3 id="memory-components" data-reading-block>Components of Main Memory</h3>

<div id="memory-access-flow" data-reading-block>

Main memory has storage cells, address-selection circuitry and read/write circuitry. A read sends an address, selects the corresponding location and returns its stored value. A write supplies both an address and the new value, with control signals identifying the operation. The **address** identifies a location; it is not the data stored there.

With *a* address bits, a simple address space has 2<sup>a</sup> addressable locations. Capacity also depends on the amount stored at each location. Sixteen address bits and one byte per location give 65,536 bytes, or **64 KiB**. If each address selects a two-byte word, the same number of addresses covers 128 KiB. Check the addressing unit rather than assuming one address always means one byte.

</div>

<h3 id="memory-expansion" data-reading-block>Capacity Expansion of Main Memory</h3>

<div id="memory-expansion-example" data-reading-block>

Memory modules combine chips into an appropriate width and number of locations. Historical SIMM and DIMM names refer to module arrangements; adding a module requires matching the system's supported technology and organization. A removable flash memory card increases storage capacity, not automatically the CPU's directly usable main RAM.

**Worked example.** One chip organized as 1M × 8 stores 2²⁰ locations of eight bits, or 1 MiB. Four chips operating side by side can supply a 32-bit word at each location: 1M × 32 = 4 MiB. Two banks of that arrangement double the location count and require eight chips in total. Distinguish widening each access from adding more addresses.

</div>

<h2 id="instructions-addressing" data-reading-block>Instruction and Addressing</h2>

<h3 id="instruction-types" data-reading-block>Types and Configuration of Instructions</h3>

<div id="instruction-fields" data-reading-block>

A machine instruction contains an **opcode** identifying the operation and fields identifying operands, registers or addressing information. Its binary layout is defined by the instruction-set architecture. An operand field might be a literal value, a register number or part of a memory address; interpreting every operand field as a final address is a mistake.

Data-transfer instructions load, store or move values. Arithmetic instructions add or subtract; logical instructions combine or shift bits; comparison and conditional-branch instructions select a path; call and return instructions manage procedure flow. A branch changes which instruction address is used next. An I/O instruction or memory-mapped device access controls an external device under the system's rules.

The number of explicit operands varies. An accumulator machine can have an implicit operand; a register-register instruction may name two sources and a destination. “One instruction” is not necessarily “one memory access” or “one clock cycle.”

</div>

<h3 id="instruction-sequence" data-reading-block>Execution Sequence of Instructions</h3>

<figure class="flow-figure" id="fetch-execute-flow" data-reading-block>
  <ol class="flow-steps"><li>Fetch<br /><small>PC → memory → IR</small></li><li>Decode<br /><small>Interpret opcode</small></li><li>Obtain operands<br /><small>Registers or memory</small></li><li>Execute and store<br /><small>ALU → destination</small></li></ol>
  <figcaption>Original simplified instruction-cycle diagram. Control flow determines the next PC; real implementations may overlap these stages.</figcaption>
</figure>

<div id="instruction-trace" data-reading-block>

Suppose PC=200 and a two-byte instruction at that address means “add the value at address 900 to register R1.” Fetch puts the instruction word into IR and advances the sequential PC to 202 under this model. Decode identifies the addition and addressing mode. Operand fetching obtains memory[900]; the ALU adds it to R1; write-back stores the result. A taken branch would select a different next PC.

The PC and IR therefore contain different kinds of information even during the same instruction. The instruction decoder consumes instruction fields from IR, not the data value produced by an earlier arithmetic operation. Condition flags may change after execution and guide a later branch.

</div>

<h3 id="addressing-modes" data-reading-block>Addressing Mode</h3>

<div id="addressing-table" data-reading-block>

The **effective address (EA)** is the address actually used to access an operand. Let A be an instruction's address field, M[x] the value stored at memory address x, R an index register and B a base register. Register contents and address fields must use consistent units.

| Mode | How the operand is found | Example with A=40, R=3, B=1,000 |
|---|---|---|
| Immediate | The field is the value itself | Operand is 40; no operand-memory address is calculated |
| Register | A named register holds the operand | Read that register's value |
| Direct | EA=A | Access M[40] |
| Indirect | EA=M[A] | If M[40]=700, access M[700] |
| Indexed | EA=A+R | Access M[43] |
| Base-relative | EA=B+A | Access M[1,040] |
| PC-relative | EA=the specified PC reference+displacement | If reference PC=204 and displacement=−8, EA=196 |

Indexed access supports repeated elements; base-relative access supports locating a program or data region; PC-relative access supports nearby branches or data references. The PC reference may be defined as the current or next instruction address, so use the problem's convention. Likewise, an array index may need scaling by element size before it becomes a byte displacement.

**Check the indirection.** If A=40 and M[40]=700, the immediate operand is 40, a direct load returns 700, and an indirect load returns the value held at address 700. The same number appears in the instruction, but the results need not be equal.

</div>

<h3 id="interrupts" data-reading-block>Interrupt</h3>

<div id="interrupt-priority" data-reading-block>

An interrupt or exception causes the processor to suspend its current sequence and run a handler. An external device completion or timer can generate an external interrupt. A running instruction can cause a synchronous exception such as an invalid operation. Names and exact classifications vary by architecture; the essential point is that the processor needs a controlled way to enter a handler and resume safely.

The system saves the necessary PC and status, selects a handler and enters an appropriate privileged execution context. The handler services the event, acknowledges it as required, restores state and returns. An interrupt does not mean that the suspended program starts again at its first instruction.

<a class="concept-highlight" id="concept-interrupts" data-concept="interrupts" href="/practice/interrupts/"><mark>Interrupt priority</mark> ↗</a> determines which eligible handler can run when several events compete. With nested interrupts permitted, a higher-priority handler can preempt a lower-priority one. The lower-priority handler then continues its unfinished work; it does not run its entire original duration again. Masked events may wait until enabled.

**Timeline example.** A low-priority handler starts at time 0 and needs 3 ms. A high-priority event arrives at 1 ms and needs 0.5 ms. The low-priority handler has completed 1 ms, so 2 ms remain. It resumes at 1.5 and finishes at 3.5 ms. Total handler CPU time is still 3.5 ms if switching overhead is ignored. Mark exact time boundaries before counting how much time the main program receives.

</div>

<h2 id="alu-circuits" data-reading-block>Circuit Configuration of ALU</h2>

<h3 id="logic-circuits" data-reading-block>Logic Circuit</h3>

<div id="logic-truth-table" data-reading-block>

Boolean logic works with two states. AND is true when both inputs are true; inclusive OR is true when at least one is true; NOT inverts a state. XOR is true when two inputs differ. NAND negates AND, and NOR negates OR. A bubble on a circuit symbol means inversion at that connection.

<a class="concept-highlight" id="concept-logic-gates" data-concept="logic-gates" href="/practice/logic-gates/"><mark>Logic gates and equivalent circuits</mark> ↗</a> can be compared by evaluating every input combination, rather than judging a drawing's appearance.

| A | B | A AND B | A OR B | A XOR B | A NAND B | A NOR B |
|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| 0 | 1 | 0 | 1 | 1 | 1 | 0 |
| 1 | 0 | 0 | 1 | 1 | 1 | 0 |
| 1 | 1 | 1 | 1 | 0 | 0 | 0 |

Useful identities include A AND 1=A, A OR 0=A, A AND 0=0, A OR 1=1, and A XOR A=0. **De Morgan's laws** move a negation across an entire group: NOT(A AND B)=(NOT A) OR (NOT B), and NOT(A OR B)=(NOT A) AND (NOT B). Change both the operation and the inputs' negations; changing only one produces a different function.

A two-input **multiplexer (MUX)** selects one data input. With select S, output Y=(NOT S AND I₀) OR (S AND I₁). If I₀=A and I₁=NOT A, the output is A when S=0 and inverted A when S=1: exactly A XOR S. This is a function derived from the connections, not a rule that every MUX is an XOR gate.

To derive a circuit from a truth table, write one AND term for each row where output=1, using an input or its negation to match that row; OR the terms together. Then simplify with identities and verify the resulting truth table. Naming intermediate outputs makes complemented connections easier to follow.

</div>

<h3 id="arithmetic-circuits" data-reading-block>Arithmetic Operation Circuit</h3>

<div id="adder-example" data-reading-block>

A **half adder** adds two one-bit inputs. Its sum is A XOR B, and its carry is A AND B. For 1+1, the result is binary 10: sum 0 and carry 1. A **full adder** also accepts an incoming carry C<sub>in</sub>:

<p class="formula">sum = A XOR B XOR C<sub>in</sub><br />carry = (A AND B) OR (C<sub>in</sub> AND (A XOR B))</p>

For A=1, B=0 and C<sub>in</sub>=1, sum=0 and carry=1. Connecting stages produces a multi-bit adder; in a simple ripple-carry arrangement a later stage waits for an earlier carry. A **flip-flop** stores a bit of state, unlike a purely combinational gate whose output depends only on its present inputs. Registers combine state-holding elements.

Two's-complement subtraction reuses addition: A−B=A+(NOT B)+1 within a chosen width. An ALU can select normal or complemented operand bits and use the carry-in for the added one. Separate logic detects conditions such as zero and signed overflow. An adder's final carry is not automatically the signed-overflow flag.

</div>

<h2 id="high-speed" data-reading-block>High Speed Technologies</h2>

<h3 id="high-speed-memory" data-reading-block>High Speed Memory Access</h3>

<div id="cache-and-interleaving" data-reading-block>

Registers, cache, main memory and auxiliary storage form a hierarchy balancing speed, capacity and cost. **Temporal locality** favors recently reused data; **spatial locality** favors nearby addresses. A cache keeps copies of memory blocks so many accesses can avoid a slower level. A miss continues to the next level; it is not a failure to retain the original file.

For hit probability h and complete hit/miss path times, average access time = h×T<sub>hit</sub>+(1−h)×T<sub>miss</sub>. If the given miss time is an additional penalty, instead add it to the lookup time with its miss probability. The existing <a href="/chapters/hardware/memory-and-cache/">Memory hierarchy & cache focus lesson</a> develops both timing models and preserves its three reviewed questions.

**Write-through** updates the next level when the cache is written; it simplifies keeping that level current but creates write traffic. **Write-back** marks a cache block dirty and writes it to the next level when required, often on eviction. A dirty block is modified, not defective. Buffers and coherence mechanisms are important in actual systems, so do not assume every cache uses the same write policy.

**Memory interleaving** places successive locations in different banks so operations can overlap. If a bank needs several cycles before accepting another access, alternating independent banks can improve the sustained transfer rate. Four banks do not necessarily make every single access four times faster: latency, access patterns, conflicts and bus capacity still matter.

</div>

<h3 id="processor-speed" data-reading-block>Speeding-up of Processor</h3>

<div id="pipeline-example" data-reading-block>

A pipeline overlaps stages of different instructions. It improves throughput when the stages can proceed smoothly; it need not shorten the latency of one instruction. With three one-cycle stages—fetch F, decode D and execute E—four independent instructions take six cycles instead of twelve in an ideal non-overlapped model:

| Instruction | Cycle 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| I₁ | F | D | E | | | |
| I₂ | | F | D | E | | |
| I₃ | | | F | D | E | |
| I₄ | | | | F | D | E |

This original timing diagram shows filling and draining the pipeline. A data dependency, shared hardware resource or branch can insert stalls or flush work. A **super-pipeline** splits work into more stages; it can reduce the work per stage but increases the number of stages affected by a disruption.

**RISC** emphasizes a relatively regular instruction organization, often with simpler load/store operations and fixed-length formats. **CISC** includes more complex instruction forms and often variable-length encodings. Hard-wired control implements control decisions with circuits; microprogrammed control sequences smaller internal control operations. These are design approaches, not a guarantee that one named family always finishes a program faster. Real implementations can combine techniques.

**Superscalar** hardware finds opportunities to issue multiple instructions in parallel; **VLIW** makes parallel-operation groupings more explicit in compiler-generated long instruction words. Out-of-order execution can perform ready operations ahead of blocked ones while preserving the program's required architectural behavior.

**Multicore** places multiple processing cores on a chip. Independent tasks can run concurrently, but shared memory, coordination and serial parts of a program limit speedup. If 25% of execution is inherently serial and 75% can be divided perfectly across four cores, the ideal total time relative to one core is 0.25+0.75/4=0.4375, giving speedup about 2.29—not four.

| Instruction/data streams | Classification | Model |
|---|---|---|
| One instruction, one data stream | SISD | A scalar sequential-processing model |
| One instruction, multiple data streams | SIMD | Apply the same operation to several vector elements |
| Multiple instructions, one data stream | MISD | A less common theoretical classification |
| Multiple instructions, multiple data streams | MIMD | Independent processors or cores execute different instruction streams |

Use the technique that addresses the actual bottleneck. A deeper pipeline does not increase disk rotation speed, and more cores do not remove a dependency that requires one calculation's result before another can begin.

</div>
