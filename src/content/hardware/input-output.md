---
id: fe-v1-ch01-s05
title: Input/Output Unit
---

<div id="io-goals" data-reading-block>

Input and output connect a computer's stored representations with people, objects and signals. First identify what a device measures or produces. Then distinguish the device's role from its interface, transfer-control method and software driver. Those are separate layers of the same operation.

</div>

<h2 id="input-unit" data-reading-block>Input Unit</h2>

<h3 id="signal-input" data-reading-block>Devices for Entering Characters and Numbers by Using Signals</h3>

<div id="keyboard-input" data-reading-block>

A keyboard turns key actions into signals that system software interprets. A key's physical position or scan code is not necessarily the final encoded character: modifiers, layout and an input method can change the result. For example, one key can produce a lowercase letter, an uppercase letter or a command shortcut depending on the current state.

Mechanical contacts may **bounce** briefly after a press, producing several transitions. Debouncing interprets the action as a single intended change. This is distinct from deliberate key-repeat behavior after a key is held. Numeric keypads and specialized button panels use the same general idea of turning user actions into input signals.

</div>

<h3 id="paper-input" data-reading-block>Device for Reading Data Written on Paper</h3>

<div id="paper-reader-table" data-reading-block>

| Device or technique | What it recognizes | Suitable example |
|---|---|---|
| OCR, optical character recognition/reader | Shapes of written or printed characters | Turn a photographed invoice's printed text into character data |
| OMR, optical mark reader | Filled marks at known positions | Read answers on a marked response sheet |
| MICR, magnetic ink character reader | Characters printed with magnetic ink | Process suitably printed bank documents |
| Barcode/QR reader | An encoded one- or two-dimensional pattern | Read an item's identifier or a QR payload |
| Image scanner | A grid of image samples | Capture a document or picture as image data |

Scanning an image is not the same as recognizing its text. OCR may process the image afterward and can make recognition errors. OMR usually relies on a prepared layout rather than arbitrary handwriting. A barcode's encoded identifier may need a database lookup; it does not necessarily contain the full description or price of the product.

**Resolution example.** Scanning a 2-by-3-inch region at 300 dots per inch gives 600×900 samples. With eight bits per sample and no compression or overhead, storage is 600×900×8/8 = **540,000 bytes**. Doubling resolution in both directions gives four times as many samples, not twice as many.

</div>

<h3 id="pointing-devices" data-reading-block>Pointing Device</h3>

<div id="pointing-input" data-reading-block>

A mouse generally reports relative movement; a touch panel or digitizer can identify an absolute location within a surface. Joysticks indicate direction or displacement for navigation and control. A light pen is a historical pointing device associated with the display technology it was designed to sense. The application's interpretation turns these physical events into selection, dragging or another action.

Touch panels use different sensing principles. A **resistive** panel detects contact between layers under pressure. A **capacitive** panel detects electrical changes associated with a touch. An **infrared** arrangement detects interrupted or changed light paths. A matrix-switch arrangement identifies an activated row/column location. These mechanisms differ in what they sense; a “touch display” combines a display output with a separate input mechanism.

</div>

<h3 id="other-input" data-reading-block>Other Input Devices</h3>

<div id="other-input-examples" data-reading-block>

A digitizer/tablet captures pen position and, where supported, pressure or other properties. A card reader may sense magnetic data or communicate with an embedded IC, depending on the card and reader technology. A biometric device samples a physical characteristic such as a fingerprint; matching and access decisions require processing beyond the sensor itself.

A microphone converts sound into an electrical signal. Digital capture requires sampling and quantization, while a camera captures image samples from light. These are input functions even when the camera or microphone is part of a larger device with its own display or speakers. A 3D scanner measures an existing object's shape and produces data; it does not manufacture that object.

**Check the direction.** A temperature sensor produces readings for a controller. A heater receives a control output and changes the physical world. A single control system can therefore contain both input and output devices without making the sensor an actuator.

</div>

<h2 id="output-unit" data-reading-block>Output Unit</h2>

<h3 id="display" data-reading-block>Display</h3>

<div id="display-calculations" data-reading-block>

A raster display organizes output as pixels. **Resolution** gives the horizontal and vertical pixel counts; **color depth** gives bits used to represent each pixel's color in a particular format. They describe different quantities. If *b* bits independently select a pixel value, there are up to 2<sup>b</sup> possible codes.

For an uncompressed packed image with no padding, headers or additional buffers:

<p class="formula">bytes = width × height × bits per pixel ÷ 8</p>

An 800×600 image with 24-bit RGB uses 800×600×24/8 = **1,440,000 bytes**. Eight bits for each of red, green and blue provide 256 choices per channel and 256³ = 16,777,216 RGB combinations. A framebuffer format that stores an additional eight-bit channel uses 32 bits per pixel instead; use the stated format.

**CRT** displays use an electron beam and phosphor. **LCD** panels modulate light and typically use a backlight. **PDP** refers to plasma display panels. **OLED** pixels emit light from organic light-emitting elements. These technologies do not change the basic distinction between pixel count, color depth and the rate at which images are refreshed. A higher resolution alone does not specify a larger physical screen or better rendering of every image.

</div>

<h3 id="printer" data-reading-block>Printer</h3>

<div id="printer-types" data-reading-block>

| Method | How an image is formed | Useful distinction |
|---|---|---|
| Dot impact | Pins strike a ribbon against paper | Physical impact can support suitable multipart forms |
| Line printer | Prints a line using its mechanism | Historically suited to high-volume character output |
| Direct thermal | Heat changes suitable heat-sensitive paper | Requires a compatible recording medium |
| Thermal transfer / dye sublimation | Heat transfers recording material | Differs from directly darkening thermal paper |
| Inkjet | Deposits small ink droplets | Places color on the recording surface |
| Laser/electrophotographic | An electrostatic image attracts toner, which is fixed | Forms a page image using toner rather than ink droplets |

Printer resolution may be expressed in dpi, and speed in pages or characters per unit time. A page description language specifies how a page should be rendered; it is software information, not a printing mechanism. A spooler queues print jobs so applications need not directly manage every physical step.

**Modern exam connection.** <a class="concept-highlight" id="concept-three-dimensional-printing" data-concept="three-dimensional-printing" href="/practice/three-dimensional-printing/"><mark>3D printing</mark> ↗</a> fabricates a physical object from a digital model, often layer by layer. Fused filament fabrication deposits material to build those layers. This differs from a scanner measuring an existing object, thermal printing on paper, or projection mapping light onto a surface. The digital-to-physical direction identifies the output role even though the result is not a sheet of paper.

</div>

<h3 id="other-output" data-reading-block>Other Output Devices</h3>

<div id="other-output-examples" data-reading-block>

A plotter produces drawings along controlled paths; a projector casts an image onto a surface. Electronic paper emphasizes persistent, paper-like display behavior rather than being ordinary printed paper. A voice synthesizer converts a symbolic representation into speech output; a speaker converts the resulting electrical signal into sound.

Different outputs may represent the same underlying result. A navigation instruction can appear as text, a map arrow or synthesized speech. Choosing an output device means considering the required physical result and the user's environment, not merely counting the bytes of the source data.

</div>

<h2 id="other-io" data-reading-block>Other Input/Output Units</h2>

<div id="bidirectional-io" data-reading-block>

Communication controllers and network interfaces both send and receive data. Storage drive units accept writes and return reads. Imaging systems can combine scanning, processing and printing. Classify the particular operation before deciding its direction: receiving a disk block is input relative to the CPU; sending a new block for storage is output.

A controller can translate system commands into device-specific signals and report completion or errors. This separates low-level physical timing from the application's request. Mechanical drives and actuators can also turn control outputs into motion. Contact chattering needs filtering when such mechanisms produce repeated electrical transitions for one intended event.

**Trace a copy.** A scanner first supplies an image as input. Memory stores it, processing may adjust it, and a printer produces output. A multifunction device contains these roles together, but each stage still has a distinct direction and representation.

</div>

<h2 id="io-control" data-reading-block>Input/Output Control Methods</h2>

<div id="io-control-comparison" data-reading-block>

| Method | CPU involvement | Why it is used |
|---|---|---|
| Program control / direct control | CPU issues commands and moves data through program instructions | Simple, explicit control; can occupy CPU time waiting or transferring |
| DMA, direct memory access | CPU sets up the operation; a controller transfers a block between device and memory | Reduces per-byte CPU involvement for block transfers |
| Channel control | A dedicated I/O processor executes an I/O sequence | Offloads more control work as well as data movement |

**Polling** repeatedly checks device status. **Interrupt-driven I/O** allows a device to notify the CPU when attention is needed. These describe how readiness/completion is detected; DMA describes how data is moved. They are not mutually exclusive: a DMA transfer can interrupt the CPU when the whole block is complete.

A selector channel serves a selected high-speed operation; multiplexer arrangements share channel service among devices, at byte or block granularity under the particular design. The channel is doing more than being an electrically passive cable: it manages work that would otherwise require CPU control.

**Worked example.** If a CPU must execute one 100 ns transfer instruction per byte for 4,000 bytes, the transfer instructions alone occupy 400,000 ns = 0.4 ms, before any waiting. DMA can avoid that instruction per byte, but still needs setup, memory/bus access and completion handling. It does not make the device's physical transfer time zero.

</div>

<h2 id="io-interfaces" data-reading-block>Input/Output Interfaces</h2>

<h3 id="interface-classification" data-reading-block>Classification of Input/Output Interfaces</h3>

<div id="interface-topologies" data-reading-block>

An interface specifies how connected components communicate. Serial interfaces transfer bits in sequence on a signaling path; parallel interfaces carry several bits concurrently. More parallel wires do not automatically guarantee greater useful throughput: timing, signaling rate, interference and protocol overhead also matter.

Connections may form a **star** through a hub, a **cascade** of successive stages, or a **daisy chain** that connects a device onward to another. The topology determines how traffic and connection limits are shared. Distinguish topology from duplex capability: full duplex can send in both directions at once, while half duplex alternates direction on the relevant shared channel.

**Connector, interface and protocol are different.** Physical fit alone cannot prove support for every data rate, power level or device function. A controller, cable and peripheral must agree on compatible behavior.

</div>

<h3 id="interface-types" data-reading-block>Types of Input/Output Interfaces and their Characteristics</h3>

<div id="interface-types-table" data-reading-block>

The textbook includes several interfaces that are now mainly encountered in historical equipment or specialized applications. Their names remain useful exam terminology. Rate and distance depend on the particular standard version and implementation; no single generic number describes every device with the same interface name.

| Interface | Main association |
|---|---|
| RS-232C | Historical serial links to terminals and other devices |
| SCSI | Commands/connections for storage and other peripherals; historical parallel SCSI and later forms differ |
| USB | Host-managed peripheral connections through hubs |
| IEEE 1394 | Serial peripheral communication, historically including audiovisual equipment |
| Centronics | Historical parallel printer connection |
| GPIB | Instrument control and measurement equipment |
| Serial ATA (SATA) | Serial storage-device connection |
| IrDA | Infrared communication requiring a suitable optical path |
| Bluetooth | Short-range radio connections under its defined profiles and modes |
| HDMI | Digital audiovisual signals to compatible displays and receivers |

<a class="concept-highlight" id="concept-usb-interface" data-concept="usb-interface" href="/practice/usb-interface/"><mark>USB interfaces</mark> ↗</a> use a host-controlled tiered arrangement. The familiar theoretical limit is **127 addressed devices on a bus**, including addressed hubs. Hubs do not create an independent full-bandwidth link for every attached device. Power, bandwidth, supported topology and controller resources impose practical limits before every theoretical address is usable.

**Hot plug** means devices can be connected or removed under the supported operating conditions without shutting down the whole computer. It does not mean interrupting an outstanding storage write is safe. **Bus-powered** devices receive power through the connection; that power is finite and must meet the interface and system limits. Wireless interfaces remove a data cable but do not remove the need for power or compatible protocol support.

</div>

<h3 id="device-driver" data-reading-block>Device Driver</h3>

<div id="drivers-firmware" data-reading-block>

A **device driver** is software that translates system requests into the operations a device understands and returns status or data to the system. It hides many device-specific details from an application. Installing a driver does not create a missing physical interface or increase a cable's hardware capabilities.

**BIOS** is the textbook's firmware term for initializing hardware and providing basic system services. It has a different role from an operating-system driver, even when both interact with the same device. **Plug and Play (PnP)** automates discovery and configuration of supported devices and resources. It still depends on compatible hardware, firmware and software; “automatically detected” does not mean “no driver or configuration information is needed.”

**Follow one read request.** An application asks the operating system for data. The system uses an appropriate driver, the controller issues the hardware operation, data arrives by programmed transfer or DMA, and completion is reported. The user-facing action, software layers, interface and physical device describe different parts of this same chain.

</div>
