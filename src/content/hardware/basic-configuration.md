---
id: fe-v1-ch01-s01
title: Basic Configuration of Computers
---

<div id="basic-goals" data-reading-block>

A computer receives data, stores it, follows instructions and produces results. This lesson starts with how that arrangement developed, then traces a small calculation through the hardware. You will distinguish a physical device from the role it performs and explain why a faster processor alone does not guarantee a faster system.

</div>

<h2 id="history-of-computers" data-reading-block>History of Computers</h2>

<div id="computer-generations" data-reading-block>

Early electronic computers used large numbers of **vacuum tubes** to switch signals. They consumed substantial power and required considerable space and maintenance. The useful historical pattern is the change in switching technology, integration and accessibility—not a claim that every computer changed generation in the same year.

| Textbook classification | Main technology | Why the change mattered |
|---|---|---|
| First generation, 1940s | Vacuum tubes | Electronic switching replaced much slower mechanical operations. |
| Second generation, 1950s | Transistors | Smaller, more reliable switching devices reduced size and power requirements. |
| Third generation, 1960s | Integrated circuits (ICs) | Many circuit elements could be manufactured together on a chip. General-purpose systems became more practical. |
| “3.5th” generation, 1970s | Large-scale integration (LSI) | Increased integration enabled microprocessors, embedded control and smaller computers. |
| Fourth generation, 1980s onward | Very-large-scale integration (VLSI) | More functions fitted on a chip; personal computers and networked workstations spread. |
| Subsequent development | System-on-chip, programmable logic, parallelism | Designers combine functions, increase useful work and manage energy consumption. |

The textbook's “fifth generation” discussion is an outlook, not a universal hardware boundary. A **microprocessor** implements CPU functions on an integrated circuit. A **microcomputer** is a computer built around such a processor. A **microcontroller** commonly integrates a CPU, memory and peripheral functions for control tasks. A **system on a chip (SoC)** integrates several system functions; it need not mean that every component of the finished product is on one chip.

A **field-programmable gate array (FPGA)** contains configurable logic. Its circuits can be configured after manufacture. This differs from running a sequence of instructions on a general-purpose CPU, and from an application-specific integrated circuit whose logic is manufactured for a particular function. Cost, speed, development time and power determine which approach is appropriate; no one approach always wins.

**Think about the role.** A server provides services to other systems; a workstation supports an individual's demanding work; an embedded computer controls part of a larger product. These are uses and arrangements, not a simple ranking by physical size. A small network appliance can be a server.

</div>

<div class="worked-example" id="power-example" data-reading-block>

**Worked example: energy is not the same as power.** A device drawing 40 W for three hours uses 40 × 3 = 120 Wh = 0.12 kWh. Watts describe the rate of energy use. Watt-hours describe accumulated energy. Reducing wasted work or idle power can matter as much as increasing a clock frequency.

</div>

<h2 id="five-major-units" data-reading-block>Five Major Units of Computers</h2>

<div id="unit-roles" data-reading-block>

The five-unit model separates the work a computer must do. A single physical product can perform more than one of these roles: a touch display, for example, is both an input and an output device.

| Unit | Responsibility | Example |
|---|---|---|
| Input unit | Turn an external action or signal into data the computer can use | Keyboard, scanner or microphone |
| Output unit | Present results outside the computer | Display, printer or speaker |
| Storage unit | Hold instructions, operands and results | Main memory and auxiliary storage |
| Arithmetic and logical unit (ALU) | Perform arithmetic, comparisons and bit operations | Add two register values; test whether a result is zero |
| Control unit | Fetch and interpret instructions and direct the other units | Arrange a memory read, select an ALU operation, advance the program |

The **central processing unit (CPU)** combines control and arithmetic/logical processing, with registers holding immediate working values. Main memory is closely connected to the CPU but is a separate functional unit in this model. Auxiliary storage retains larger collections of programs and files; the CPU normally operates on instructions and data made available in main memory rather than treating an SSD file as an ALU register.

</div>

<figure class="flow-figure" id="five-unit-flow" data-reading-block>
  <ol class="flow-steps"><li>Input<br /><small>Receive values</small></li><li>Storage<br /><small>Hold program and data</small></li><li>CPU<br /><small>Control + ALU</small></li><li>Output<br /><small>Present the result</small></li></ol>
  <figcaption>Original functional diagram. Data can move in both directions between CPU and storage; the control unit directs the steps.</figcaption>
</figure>

<div id="stored-program" data-reading-block>

**The stored-program principle.** A sequence of machine instructions is stored in memory. The control unit fetches an instruction, determines the operation, obtains its operands and arranges execution. The program can change the instruction sequence through branches. This makes one physical machine useful for many tasks without rebuilding its circuits for every calculation.

In the simplified **von Neumann architecture**, instructions and data share memory and a transfer path. A **Harvard architecture** separates instruction and data paths or storage. Real designs may combine these ideas—for example, separate instruction and data caches with a shared main-memory system. The important distinction is which transfers can proceed independently, not whether a machine has a particular brand name.

**Trace 8 + 5.** Input supplies the two numbers. Memory holds those values and the program. The control unit fetches an addition instruction; operands enter working registers; the ALU produces 13; the result is stored and eventually sent to an output device. The ALU does not decide by itself whether the result should be printed or used in a later calculation: instructions and control determine that sequence.

**Hardware and software work together.** Hardware supplies the physical circuits; software describes operations to perform. A driver lets system software control a device, but is not itself the physical device. Firmware is software stored in nonvolatile memory, commonly used to initialize or control hardware.

The performance of the whole path matters. A processor waiting for memory, storage or input cannot make that waiting time disappear just by doing arithmetic faster. Later lessons examine each part of the path and show how to calculate the time spent there.

</div>

<div class="worked-note" id="basic-recap" data-reading-block>

**Check your understanding.** A touch screen receives a tap and displays a menu: it performs two unit roles. A program counter is a small CPU register, not a file store. An SSD can retain a program while power is off, but executing that program also needs the CPU, main memory and control of data transfers. Explain each answer in terms of function rather than appearance.

</div>
