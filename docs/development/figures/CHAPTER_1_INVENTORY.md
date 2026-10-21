# Chapter 1 figure inventory

Source: **New FE Textbook Vol.1, IT Fundamentals, First Edition April 2015**, printed pages **13–111**. All 99 numbered pages and the unnumbered inserted physical page were visually reviewed. The inventory covers every numbered figure **1-1 through 1-47**, plus photographs, tables, worked visual examples and relevant margin annotations. One region may group related images or a multi-part worked example; 130 regions is not a claim of 130 separately numbered figures.

The [machine-readable inventory](chapter1-inventory.json) records complete PDF-point crop bounds, physical/printed page pairs, baseline comparison, destination and review decision for each region. Source crops are editorial-only under `.local/figures/`; publication permission has not been established. Only newly authored artwork is integrated.

**Comparison key:** `recreated` = new conceptual SVG equivalent; `existing-equivalent` = the current lesson’s original explanation/table/diagram already covers the teaching role, with table expansions where needed; `editorial-only` = no source artwork published. Equivalence preserves the concept and necessary labels, not source layout, product likeness or every historical sample value.

## basic-configuration

| Region | Printed / PDF page | Visual learning material | Website block / equivalent | Decision |
|---|---|---|---|---|
| hw-p013-01 | 13 / 18 | ENIAC and vacuum-tube photographs | `computer-generations` → `switching-technologies` | recreated |
| hw-p014-01 | 14 / 19 | Discrete switching-device illustrations | `computer-generations` → `switching-technologies` | recreated |
| hw-p015-01 | 15 / 20 | Supercomputer photograph | `computer-generations` → `computer-forms` | recreated |
| hw-p015-02 | 15 / 20 | Desktop, laptop and handheld computer photographs | `computer-generations` → `computer-forms` | recreated |
| hw-p016-01 | 16 / 21 | Figure 1-1: human calculation analogy | `unit-roles` → `five-unit-control` | recreated |
| hw-p017-01 | 17 / 22 | Figure 1-2: computer calculation analogy | `unit-roles` → `five-unit-control` | recreated |
| hw-p018-01 | 18 / 23 | Figure 1-3: control and data paths between the five units | `unit-roles` → `five-unit-control` | recreated |
| hw-p018-02 | 18 / 23 | Volatile main memory versus nonvolatile auxiliary storage | `stored-program` → `memory-persistence` | recreated |

## data-representation

| Region | Printed / PDF page | Visual learning material | Website block / equivalent | Decision |
|---|---|---|---|---|
| hw-p020-01 | 20 / 25 | Figure 1-4: one bit and an eight-bit byte | `bits-and-units` → `bit-patterns` | recreated |
| hw-p021-01 | 21 / 26 | Figure 1-5: binary-pattern branching and powers of two | `bits-and-units` → `bit-patterns` | recreated |
| hw-p022-01 | 22 / 27 | Decimal and binary large-unit prefix table | `bits-and-units` → `bits-and-units` | existing-equivalent |
| hw-p023-01 | 23 / 28 | Small decimal-unit prefix table | `bits-and-units` → `bits-and-units` | existing-equivalent |
| hw-p023-02 | 23 / 28 | Decimal positional-weight expansion | `radix-weights` → `radix-weights` | existing-equivalent |
| hw-p024-01 | 24 / 29 | Figure 1-6: decimal and binary number correspondence | `radix-weights` → `radix-grouping` | recreated |
| hw-p024-02 | 24 / 29 | Figure 1-7: decimal and octal number correspondence | `grouping-digits` → `radix-grouping` | recreated |
| hw-p024-03 | 24 / 29 | Binary, octal and hexadecimal positional expansions | `radix-weights` → `radix-weights` | existing-equivalent |
| hw-p025-01 | 25 / 30 | Figure 1-8: hexadecimal digit correspondence | `grouping-digits` → `radix-grouping` | recreated |
| hw-p025-02 | 25 / 30 | Grouping binary digits into octal and hexadecimal digits | `grouping-digits` → `radix-grouping` | recreated |
| hw-p026-01 | 26 / 31 | Binary positional-weight conversion example | `radix-worked` → `radix-conversion-steps` | recreated |
| hw-p027-01 | 27 / 32 | Integer division and fractional multiplication conversion diagrams | `radix-worked` → `radix-conversion-steps` | recreated |
| hw-p028-01 | 28 / 33 | Octal grouping and repeating binary fraction loop | `grouping-digits` → `repeating-fraction` | recreated |
| hw-p028-02 | 28 / 33 | Figure 1-9: data representation classification tree | `encoding-context` → `data-format-tree` | recreated |
| hw-p030-01 | 30 / 35 | Character encoding example and Figure 1-10: JIS code lookup grid | `character-encoding` → `character-code` | recreated |
| hw-p032-01 | 32 / 37 | BCD digits and zoned decimal byte layouts | `decimal-codes` → `decimal-packing` | recreated |
| hw-p033-01 | 33 / 38 | Packed decimal nibble layouts | `decimal-codes` → `decimal-packing` | recreated |
| hw-p033-02 | 33 / 38 | Figure 1-11: input, decimal packing, ALU and output conversion | `decimal-codes` → `decimal-packing` | recreated |
| hw-p034-01 | 34 / 39 | Fixed radix point and sign-magnitude bit layouts | `decimal-codes` → `signed-range` | recreated |
| hw-p035-01 | 35 / 40 | Complement subtraction and signed two’s-complement bit layouts | `decimal-codes` → `signed-range` | recreated |
| hw-p036-01 | 36 / 41 | Subtraction by complement and addition | `decimal-codes` → `decimal-codes` | existing-equivalent |
| hw-p037-01 | 37 / 42 | Sign-magnitude versus two’s-complement range tables | `decimal-codes` → `signed-range` | recreated |
| hw-p037-02 | 37 / 42 | Large-number fixed-point versus floating-point layout example | `floating-point-layout` → `floating-point-layout` | existing-equivalent |
| hw-p038-01 | 38 / 43 | Floating-point sign/exponent/fraction layouts: 32 and 64 bits | `floating-point-layout` → `float-formats` | recreated |
| hw-p039-01 | 39 / 44 | Biased exponent table and normalization example | `floating-point-layout` → `float-formats` | recreated |
| hw-p040-01 | 40 / 45 | Normalization continuation and single-precision encoding example | `floating-point-layout` → `float-formats` | recreated |
| hw-p041-01 | 41 / 46 | Lost trailing digits in aligned floating-point addition | `error-types` → `numeric-errors` | recreated |
| hw-p042-01 | 42 / 47 | Cancellation example and finite numeric-range diagram | `error-types` → `numeric-errors` | recreated |
| hw-p043-01 | 43 / 48 | Arithmetic left shift with retained sign and discarded bits | `shifting-bits` → `shift-paths` | recreated |
| hw-p044-01 | 44 / 49 | Arithmetic right shift versus logical right shift | `shifting-bits` → `shift-paths` | recreated |
| hw-p045-01 | 45 / 50 | Circular right shift / rotation | `shifting-bits` → `shift-paths` | recreated |

## cpu-and-main-memory

| Region | Printed / PDF page | Visual learning material | Website block / equivalent | Decision |
|---|---|---|---|---|
| hw-p046-01 | 46 / 51 | Figure 1-12: CPU control, ALU, registers and clock | `cpu-register-table` → `cpu-data-path` | recreated |
| hw-p047-01 | 47 / 52 | CPU register roles | `cpu-register-table` → `cpu-register-table` | existing-equivalent |
| hw-p048-01 | 48 / 53 | Figure 1-13: clock waveform and one cycle | `bus-rate-example` → `clock-buses` | recreated |
| hw-p048-02 | 48 / 53 | Internal/external and address/control/data bus classifications | `bus-rate-example` → `clock-buses` | recreated |
| hw-p049-01 | 49 / 54 | Semiconductor memory device classifications | `memory-device-table` → `memory-device-table` | existing-equivalent |
| hw-p049-02 | 49 / 54 | Added margin annotation: transistor-level TTL two-input NAND circuit | `memory-device-table` → `editorial only` | editorial-only |
| hw-p050-01 | 50 / 55 | Added margin annotation: clocked JK storage circuit | `memory-device-table` → `editorial only` | editorial-only |
| hw-p050-02 | 50 / 55 | SRAM, DRAM and ROM types | `memory-device-table` → `memory-cells` | recreated |
| hw-p051-01 | 51 / 56 | Figure 1-14: address selection and read/write memory organization | `memory-access-flow` → `memory-address-grid` | recreated |
| hw-p052-01 | 52 / 57 | Memory read/write sequence and expansion options | `memory-expansion-example` → `memory-expansion-example` | existing-equivalent |
| hw-p053-01 | 53 / 58 | Instruction types | `instruction-fields` → `instruction-fields` | existing-equivalent |
| hw-p053-02 | 53 / 58 | Figure 1-15: opcode and address/operand instruction fields | `instruction-fields` → `instruction-format` | recreated |
| hw-p054-01 | 54 / 59 | Figure 1-16: fetch, decode, effective address, operand fetch and compute flow | `instruction-trace` → `fetch-execute-flow` | existing-equivalent |
| hw-p055-01 | 55 / 60 | Figure 1-17: CPU and main memory baseline | `instruction-trace` → `cpu-data-path` | recreated |
| hw-p055-02 | 55 / 60 | Figure 1-18: instruction fetching, PC increment and IR load | `instruction-trace` → `cpu-data-path` | recreated |
| hw-p056-01 | 56 / 61 | Figure 1-19: instruction decoding path | `instruction-trace` → `cpu-data-path` | recreated |
| hw-p056-02 | 56 / 61 | Figure 1-20: effective address and operand fetching | `instruction-trace` → `cpu-data-path` | recreated |
| hw-p057-01 | 57 / 62 | Figure 1-21: ALU execution and result write-back | `instruction-trace` → `cpu-data-path` | recreated |
| hw-p057-02 | 57 / 62 | Absolute addressing address path | `addressing-table` → `operand-addressing` | recreated |
| hw-p058-01 | 58 / 63 | Indexed, base and PC-relative address addition diagrams | `addressing-table` → `operand-addressing` | recreated |
| hw-p058-02 | 58 / 63 | Figure 1-22: immediate addressing | `addressing-table` → `operand-addressing` | recreated |
| hw-p059-01 | 59 / 64 | Figure 1-23: direct addressing | `addressing-table` → `operand-addressing` | recreated |
| hw-p059-02 | 59 / 64 | Figure 1-24: indirect addressing | `addressing-table` → `operand-addressing` | recreated |
| hw-p060-01 | 60 / 65 | Interrupt processing sequence and classification | `interrupt-priority` → `interrupt-priority` | existing-equivalent |
| hw-p061-01 | 61 / 66 | Basic logical operations truth table | `logic-truth-table` → `logic-truth-table` | existing-equivalent |
| hw-p062-01 | 62 / 67 | Figure 1-25: active-low NAND SR latch and state table | `adder-example` → `sr-latch` | recreated |
| hw-p062-02 | 62 / 67 | Figure 1-26: AND gate and truth table | `logic-truth-table` → `logic-symbols` | recreated |
| hw-p063-01 | 63 / 68 | Figure 1-27: OR gate and truth table | `logic-truth-table` → `logic-symbols` | recreated |
| hw-p063-02 | 63 / 68 | Figure 1-28: NOT gate and truth table | `logic-truth-table` → `logic-symbols` | recreated |
| hw-p063-03 | 63 / 68 | Figure 1-29: NAND gate and truth table | `logic-truth-table` → `logic-symbols` | recreated |
| hw-p063-04 | 63 / 68 | Figure 1-30: NOR gate and truth table | `logic-truth-table` → `logic-symbols` | recreated |
| hw-p064-01 | 64 / 69 | Figure 1-31: XOR gate and truth table | `logic-truth-table` → `logic-symbols` | recreated |
| hw-p065-01 | 65 / 70 | Boolean algebra laws | `logic-truth-table` → `logic-truth-table` | existing-equivalent |
| hw-p066-01 | 66 / 71 | Two equivalent XOR networks and Boolean derivation | `logic-truth-table` → `xor-network` | recreated |
| hw-p067-01 | 67 / 72 | Half-adder truth table | `adder-example` → `adders` | recreated |
| hw-p067-02 | 67 / 72 | Figure 1-32: half-adder XOR/AND connections | `adder-example` → `adders` | recreated |
| hw-p068-01 | 68 / 73 | Full-adder three-input truth table and Boolean derivation | `adder-example` → `adders` | recreated |
| hw-p069-01 | 69 / 74 | Three-input addition as two half additions | `adder-example` → `adders` | recreated |
| hw-p069-02 | 69 / 74 | Figure 1-33: full adder made from two half adders and OR | `adder-example` → `adders` | recreated |
| hw-p070-01 | 70 / 75 | Figure 1-34: register/cache/main-memory buffering | `cache-and-interleaving` → `cache-paths` | recreated |
| hw-p071-01 | 71 / 76 | Weighted cache and main-memory access-time example | `cache-and-interleaving` → `cache-and-interleaving` | existing-equivalent |
| hw-p072-01 | 72 / 77 | Cache write-through and write-back policies | `cache-and-interleaving` → `cache-and-interleaving` | existing-equivalent |
| hw-p072-02 | 72 / 77 | Figure 1-35: multilevel cache path | `cache-and-interleaving` → `cache-paths` | recreated |
| hw-p072-03 | 72 / 77 | Figure 1-36: main-memory/disk buffering | `cache-and-interleaving` → `cache-paths` | recreated |
| hw-p073-01 | 73 / 78 | Figure 1-37: memory hierarchy pyramid | `cache-and-interleaving` → `memory-hierarchy` | existing-equivalent |
| hw-p073-02 | 73 / 78 | Figure 1-38: sequential addresses distributed over memory banks | `cache-and-interleaving` → `bank-interleaving` | recreated |
| hw-p075-01 | 75 / 80 | Figure 1-39: overlapped instruction pipeline timing | `pipeline-example` → `pipeline-example` | existing-equivalent |
| hw-p075-02 | 75 / 80 | Figure 1-40: uneven stage duration and pipeline stalls | `pipeline-example` → `pipeline-stalls` | recreated |
| hw-p076-01 | 76 / 81 | Figure 1-41: pipeline versus super-pipeline timing | `pipeline-example` → `pipeline-stalls` | recreated |
| hw-p077-01 | 77 / 82 | SISD/SIMD/MISD/MIMD classification | `pipeline-example` → `pipeline-example` | existing-equivalent |

## auxiliary-storage

| Region | Printed / PDF page | Visual learning material | Website block / equivalent | Decision |
|---|---|---|---|---|
| hw-p078-01 | 78 / 84 | Figure 1-42: tracks, sectors and magnetic recording orientations | `disk-geometry` → `disk-geometry-figure` | recreated |
| hw-p079-01 | 79 / 85 | Figure 1-43: head, access arm and target track | `disk-geometry` → `disk-geometry-figure` | recreated |
| hw-p079-02 | 79 / 85 | Figure 1-44: HDD photograph and platter/head/cylinder schematic | `disk-geometry` → `disk-geometry-figure` | recreated |
| hw-p080-01 | 80 / 86 | Uniform disk geometry capacity table | `disk-capacity-example` → `disk-capacity-example` | existing-equivalent |
| hw-p081-01 | 81 / 87 | Capacity calculation continuation | `disk-capacity-example` → `disk-capacity-example` | existing-equivalent |
| hw-p081-02 | 81 / 87 | Variable-length blocks and interblock gaps | `records-and-blocks` → `record-blocks` | recreated |
| hw-p082-01 | 82 / 88 | Sector recording and block grouping | `records-and-blocks` → `record-blocks` | recreated |
| hw-p082-02 | 82 / 88 | Recording area calculation table and worked example | `records-and-blocks` → `records-and-blocks` | existing-equivalent |
| hw-p083-01 | 83 / 89 | Recording area calculation continuation | `records-and-blocks` → `records-and-blocks` | existing-equivalent |
| hw-p084-01 | 84 / 90 | Seek, rotational wait and data-transfer timing diagram | `disk-access-model` → `disk-access-timeline` | recreated |
| hw-p085-01 | 85 / 91 | Rotation/transfer formulas and worked specification table | `disk-access-model` → `disk-access-model` | existing-equivalent |
| hw-p086-01 | 86 / 92 | Worked average disk access time calculation | `disk-access-model` → `disk-access-model` | existing-equivalent |
| hw-p088-01 | 88 / 94 | Optical-disc recording method comparison | `optical-types` → `optical-types` | existing-equivalent |

## input-output

| Region | Printed / PDF page | Visual learning material | Website block / equivalent | Decision |
|---|---|---|---|---|
| hw-p092-01 | 92 / 98 | Figure 1-45: input-processing-output data path | `io-goals` → `io-processing` | recreated |
| hw-p092-02 | 92 / 98 | Keyboard illustration | `keyboard-input` → `keyboard-signal` | recreated |
| hw-p093-01 | 93 / 99 | OCR device illustration | `paper-reader-table` → `paper-readers` | recreated |
| hw-p093-02 | 93 / 99 | OMR response-sheet example | `paper-reader-table` → `paper-readers` | recreated |
| hw-p093-03 | 93 / 99 | MICR document example | `paper-reader-table` → `paper-readers` | recreated |
| hw-p094-01 | 94 / 100 | Barcode reader illustration | `paper-reader-table` → `paper-readers` | recreated |
| hw-p094-02 | 94 / 100 | One-dimensional barcode and two-dimensional QR examples | `paper-reader-table` → `paper-readers` | recreated |
| hw-p095-01 | 95 / 101 | Image scanner illustration | `paper-reader-table` → `paper-readers` | recreated |
| hw-p095-02 | 95 / 101 | Mouse illustration | `pointing-input` → `touch-coordinates` | recreated |
| hw-p096-01 | 96 / 102 | Touch-sensing methods comparison | `pointing-input` → `pointing-input` | existing-equivalent |
| hw-p096-02 | 96 / 102 | Digitizer/tablet illustration | `other-input-examples` → `touch-coordinates` | recreated |
| hw-p098-01 | 98 / 104 | Display illustration and resolution standards table | `display-calculations` → `pixel-grid` | recreated |
| hw-p098-02 | 98 / 104 | Frame-buffer capacity worked example | `display-calculations` → `display-calculations` | existing-equivalent |
| hw-p100-01 | 100 / 106 | Figure 1-46: character glyph as dots at different resolutions | `printer-types` → `pixel-grid` | recreated |
| hw-p100-02 | 100 / 106 | Figure 1-47: impact print head, ink ribbon and paper | `printer-types` → `impact-printer` | recreated |
| hw-p101-01 | 101 / 107 | Inkjet printer illustration | `printer-types` → `printer-types` | existing-equivalent |
| hw-p102-01 | 102 / 108 | Plotter illustration | `other-output-examples` → `output-paths` | recreated |
| hw-p102-02 | 102 / 108 | Projector illustration | `other-output-examples` → `output-paths` | recreated |
| hw-p103-01 | 103 / 109 | LAN interface card function | `bidirectional-io` → `bidirectional-io` | existing-equivalent |
| hw-p104-01 | 104 / 110 | Contact chatter definition | `keyboard-input` → `keyboard-signal` | recreated |
| hw-p104-02 | 104 / 110 | Programmed transfer versus DMA data paths (source text) | `io-control-comparison` → `io-transfer` | recreated |
| hw-p105-01 | 105 / 111 | I/O channel classifications | `io-control-comparison` → `io-control-comparison` | existing-equivalent |
| hw-p106-01 | 106 / 112 | Star, cascade and daisy-chain connection diagrams | `interface-topologies` → `interface-topologies-figure` | recreated |
| hw-p107-01 | 107 / 113 | SCSI parallel width/rate comparison | `interface-types-table` → `interface-types-table` | existing-equivalent |
| hw-p108-01 | 108 / 114 | USB transfer modes and historical speeds | `interface-types-table` → `interface-types-table` | existing-equivalent |
| hw-p108-02 | 108 / 114 | Bus-power and hot-plug comparison | `interface-types-table` → `interface-types-table` | existing-equivalent |
| hw-p110-01 | 110 / 116 | Bluetooth characteristics and historical distance-class table | `interface-types-table` → `interface-types-table` | existing-equivalent |
| hw-unnumbered-i2c | unnumbered / 83 | Unnumbered inserted serial-interface exam screenshot and commentary | `interface-types-table` → `editorial only` | editorial-only |

## Newly authored public artwork

| SVG | Lesson / immediate context | Verified printed source pages |
|---|---|---|
| [From switching devices to chips](../../../src/assets/hardware/switching-technologies.svg) | basic-configuration / `computer-generations` | 13, 14 |
| [Different forms, different roles](../../../src/assets/hardware/computer-forms.svg) | basic-configuration / `power-example` | 15 |
| [Data paths and control paths](../../../src/assets/hardware/five-unit-control.svg) | basic-configuration / `five-unit-flow` | 16, 17, 18 |
| [Working memory and persistent storage](../../../src/assets/hardware/memory-persistence.svg) | basic-configuration / `stored-program` | 18 |
| [Bits, patterns and a byte](../../../src/assets/hardware/bit-patterns.svg) | data-representation / `bits-and-units` | 20, 21 |
| [Group from the radix point](../../../src/assets/hardware/radix-grouping.svg) | data-representation / `grouping-digits` | 24, 25 |
| [The meaning comes from the format](../../../src/assets/hardware/data-format-tree.svg) | data-representation / `encoding-context` | 28 |
| [A character code is a lookup](../../../src/assets/hardware/character-code.svg) | data-representation / `character-encoding` | 30 |
| [Decimal digits packed into nibbles](../../../src/assets/hardware/decimal-packing.svg) | data-representation / `decimal-codes` | 32, 33 |
| [Two signed four-bit interpretations](../../../src/assets/hardware/signed-range.svg) | data-representation / `decimal-codes` | 34, 35, 37 |
| [Three ways to shift right](../../../src/assets/hardware/shift-paths.svg) | data-representation / `shifting-bits` | 43, 44, 45 |
| [Trace an instruction through the CPU](../../../src/assets/hardware/cpu-data-path.svg) | cpu-and-main-memory / `instruction-trace` | 46, 55, 56, 57 |
| [Timing and three bus roles](../../../src/assets/hardware/clock-buses.svg) | cpu-and-main-memory / `bus-rate-example` | 48 |
| [Two ways to retain a working bit](../../../src/assets/hardware/memory-cells.svg) | cpu-and-main-memory / `memory-device-table` | 50 |
| [An address selects a location](../../../src/assets/hardware/memory-address-grid.svg) | cpu-and-main-memory / `memory-access-flow` | 51 |
| [An instruction contains fields](../../../src/assets/hardware/instruction-format.svg) | cpu-and-main-memory / `instruction-fields` | 53 |
| [Follow the dereference](../../../src/assets/hardware/operand-addressing.svg) | cpu-and-main-memory / `addressing-table` | 57, 58, 59 |
| [Read the gate symbol](../../../src/assets/hardware/logic-symbols.svg) | cpu-and-main-memory / `logic-truth-table` | 62, 63, 64 |
| [Feedback stores a state](../../../src/assets/hardware/sr-latch.svg) | cpu-and-main-memory / `adder-example` | 62 |
| [Construct XOR from two cases](../../../src/assets/hardware/xor-network.svg) | cpu-and-main-memory / `logic-truth-table` | 66 |
| [A full adder from two half adders](../../../src/assets/hardware/adders.svg) | cpu-and-main-memory / `adder-example` | 67, 68, 69 |
| [Buffering at different levels](../../../src/assets/hardware/cache-paths.svg) | cpu-and-main-memory / `cache-and-interleaving` | 70, 72 |
| [Distribute successive addresses](../../../src/assets/hardware/bank-interleaving.svg) | cpu-and-main-memory / `cache-and-interleaving` | 73 |
| [A stall delays following work](../../../src/assets/hardware/pipeline-stalls.svg) | cpu-and-main-memory / `pipeline-example` | 75, 76 |
| [Track, sector, head and cylinder](../../../src/assets/hardware/disk-geometry-figure.svg) | auxiliary-storage / `disk-geometry` | 78, 79 |
| [Records, blocks and unused space](../../../src/assets/hardware/record-blocks.svg) | auxiliary-storage / `records-and-blocks` | 81, 82 |
| [Three parts of a disk read](../../../src/assets/hardware/disk-access-timeline.svg) | auxiliary-storage / `disk-access-model` | 84 |
| [From physical input to output](../../../src/assets/hardware/io-processing.svg) | input-output / `io-goals` | 92 |
| [One press, several contact transitions](../../../src/assets/hardware/keyboard-signal.svg) | input-output / `keyboard-input` | 92, 104 |
| [Recognition and capture differ](../../../src/assets/hardware/paper-readers.svg) | input-output / `paper-reader-table` | 93, 94, 95 |
| [Relative motion or absolute position](../../../src/assets/hardware/touch-coordinates.svg) | input-output / `pointing-input` | 95, 96 |
| [A glyph is a grid of samples](../../../src/assets/hardware/pixel-grid.svg) | input-output / `display-calculations` | 98, 100 |
| [Pins transfer ink through a ribbon](../../../src/assets/hardware/impact-printer.svg) | input-output / `printer-types` | 100 |
| [A path drawing or a projected image](../../../src/assets/hardware/output-paths.svg) | input-output / `other-output-examples` | 102 |
| [Who moves the block?](../../../src/assets/hardware/io-transfer.svg) | input-output / `io-control-comparison` | 104 |
| [Star, cascade and daisy chain](../../../src/assets/hardware/interface-topologies-figure.svg) | input-output / `interface-topologies` | 106 |
| [Read integer and fraction digits differently](../../../src/assets/hardware/radix-conversion-steps.svg) | data-representation / `radix-worked` | 26, 27 |
| [A recurring remainder creates recurring bits](../../../src/assets/hardware/repeating-fraction.svg) | data-representation / `grouping-digits` | 28 |
| [Normalize, then store the fields](../../../src/assets/hardware/float-formats.svg) | data-representation / `floating-point-layout` | 38, 39, 40 |
| [Precision and range are different limits](../../../src/assets/hardware/numeric-errors.svg) | data-representation / `error-types` | 41, 42 |

## Explicit exclusions and adaptations

- Physical PDF page 83 is an unnumbered inserted exam screenshot. It receives no fabricated printed reference.
- The margin additions on printed 49 and 50 are a transistor-level TTL NAND circuit and a clocked JK circuit. They are not DRAM-cell figures or newly licensed textbook figures. They remain editorial-only.
- The source’s SR storage circuit uses active-low NAND inputs. The original SVG uses `S_n` and `R_n` to make polarity explicit: 11 hold, 01 set, 10 reset, 00 forbidden.
- Historical device photographs are represented by original conceptual schematics and role illustrations; no product photographs or third-party source annotations are reused.
- Legacy interface mode/rate tables are matched to the existing interface comparison and version-dependent explanation; they are not copied verbatim or presented as current universal specifications.
- The error illustration distinguishes underflow near zero from signed range overflow. It does not repeat the source’s misleading implication that any value below a signed minimum is floating-point underflow.
- Worked numeric examples use original values and layouts. Existing arithmetic text is retained where it already teaches the figure’s operation; two additional tables cover Boolean laws and every full-adder input combination.
