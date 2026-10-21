---
id: fe-v1-ch01-s04
title: Auxiliary Storage
---

<div id="storage-goals" data-reading-block>

Auxiliary storage keeps programs and data beyond the working capacity or lifetime of main memory. Compare devices by their physical recording method, access pattern, capacity and transfer behavior. A large capacity does not imply low latency, and a high sequential transfer rate does not imply fast small random reads.

</div>

<h2 id="magnetic-disk" data-reading-block>Magnetic Disk</h2>

<div id="disk-geometry" data-reading-block>

An HDD stores magnetic patterns on rotating surfaces. A head reads or writes a location as the surface moves beneath it. A **track** is a circular recording path; a **sector** is a subdivision used for physical recording and transfer. Tracks at corresponding radii on multiple surfaces form a simplified **cylinder** model. A moving arm positions the heads across the radii.

The geometry model is useful for exam calculations, but a modern drive normally exposes logical block addresses and handles physical placement internally. Do not infer that every actual track has an identical sector count unless the problem specifies that model. Older floppy disks illustrate the same magnetic recording principle at different capacity, packaging and performance.

</div>

<h3 id="disk-capacity" data-reading-block>Storage Capacity of Magnetic Disk Drive</h3>

<div class="worked-example" id="disk-capacity-example" data-reading-block>

For a simplified drive with uniform geometry:

<p class="formula">capacity = recording surfaces × tracks/surface × sectors/track × bytes/sector</p>

Suppose there are four recording surfaces, 2,000 tracks per surface, 100 sectors per track and 512 bytes per sector. The raw modeled capacity is 4×2,000×100×512 = **409,600,000 bytes**. Expressing it as 409.6 MB uses decimal megabytes; in binary units it is about 390.625 MiB. Formatting, reserved regions and the model's assumptions can distinguish this value from usable file capacity.

Count recording **surfaces**, not just platters, and do not multiply by the number of heads again if it already represents the same recording surfaces.

</div>

<h3 id="disk-recording" data-reading-block>Recording Area in Magnetic Disk Drive</h3>

<div id="records-and-blocks" data-reading-block>

A **record** is a logical unit used by an application. A **block** groups data for physical or system transfer. Fixed-length records can be grouped into one block to reduce per-transfer overhead. The **blocking factor** is the number of records that fit in a block under the specified storage rules. Gaps and control information consume space but do not contain the application records.

If a usable block has 512 bytes and records are 100 bytes with no spanning, the blocking factor is floor(512/100)=5. Five records use 500 bytes and leave 12 unused bytes. Storing 103 records needs ceiling(103/5)=**21 blocks**. If the problem includes a header or an interblock gap, account for it using the specified format before calculating capacity.

A file system allocates space in blocks or clusters. Its allocation units need not match a record, and its file layout need not be physically contiguous. **Internal fragmentation** wastes space within allocated units; a file spread across separated regions experiences a different issue: noncontiguous placement that can increase mechanical movement.

</div>

<h3 id="disk-access" data-reading-block>Average Access Time of Magnetic Disk Drive</h3>

<div id="disk-access-model" data-reading-block>

An HDD read includes several distinct delays. **Seek time** moves the head to the appropriate track. **Rotational latency** waits for the needed sector to arrive. **Transfer time** moves the selected bytes. Some questions also state controller overhead.

<a class="concept-highlight" id="concept-disk-access" data-concept="disk-access" href="/practice/disk-access/"><mark>Disk access time</mark> ↗</a> is the sum of the components included by the question:

<p class="formula">T = T<sub>seek</sub> + T<sub>controller</sub> + T<sub>rotation</sub> + T<sub>transfer</sub><br />one rotation in ms = 60,000 ÷ rpm<br />average rotational latency = half one rotation<br />transfer time = data size ÷ transfer rate</p>

The half-rotation average assumes a uniformly distributed starting angular position. At 7,200 rpm one rotation takes about 8.333 ms, so average rotational latency is 4.167 ms. It is not 7,200 rotations per second.

**Worked example.** Read 2 MB at 100 MB/s after a 3 ms average seek and 0.2 ms controller delay on this drive. Transfer takes 2/100 s = 20 ms. Total = 3+0.2+4.167+20 = **27.367 ms**. A small random read can spend most of its time positioning; a long sequential transfer amortizes that delay over more data.

</div>

<div id="defragmentation-example" data-reading-block>

<a class="concept-highlight" id="concept-defragmentation" data-concept="defragmentation" href="/practice/defragmentation/"><mark>Disk defragmentation</mark> ↗</a> rearranges file blocks to reduce noncontiguous placement. On an HDD this can reduce head travel while following a file. It does not remove physical gaps between recorded blocks, delete unwanted files, repair hardware or replace a backup. Its mechanical-seek rationale does not apply to an SSD, which has no moving head; flash management has different constraints.

</div>

<h2 id="optical-disc" data-reading-block>Optical Disc</h2>

<div id="optical-types" data-reading-block>

Optical drives use light to read recorded differences on a disc. The categories describe what can be written and erased, not just how much the medium holds.

| Category | Behavior | Examples and mechanism |
|---|---|---|
| Read-only | Recorded content is manufactured into the medium | CD-ROM, DVD-ROM |
| Write-once | A location can be recorded but is not erased for reuse | CD-R and similar recordable formats |
| Rewritable | Recording material can change between readable states | Phase-change optical media such as CD-RW and suitable DVD formats |
| Higher-density optical formats | Different optical/recording design increases density | Blu-ray uses a shorter-wavelength laser than earlier common optical formats |

Writing a disc all at once (**disc-at-once**), by tracks, in sessions, or by packets concerns recording organization. **Multisession** can add a later session when the format allows it; it does not make a write-once physical location rewritable. Capacity depends on format, layers and sides, so obtain any numerical assumptions from the problem rather than from a generic “DVD” label.

Optical media can be useful for distribution or offline retention, but their readability still depends on compatible drives, suitable handling and the persistence of the physical medium. Nonvolatile does not mean indestructible.

</div>

<h2 id="semiconductor-storage" data-reading-block>Semiconductor Memory</h2>

<div id="flash-storage" data-reading-block>

An **SSD** uses electronic storage, commonly flash, and has no magnetic head to seek or platter to rotate. Its access time is therefore modeled differently from an HDD. It still has controller, transfer, program/erase and workload-dependent costs; “no moving parts” does not mean “zero access time.”

Flash typically programs smaller units and erases larger blocks. A controller maps logical addresses to physical locations, distributes wear, corrects errors and reclaims space. Erase/program endurance is finite. Copying data to a nonvolatile device is useful persistence, but losing the device or suffering a controller failure can still lose access to it.

USB flash drives and SD cards are removable flash media. Their interfaces, physical compatibility and supported format matter; a matching-looking connector does not guarantee every capability. A **RAM disk**, by contrast, uses a portion of RAM as a disk-like logical device. Ordinary volatile RAM loses that data on power loss unless another mechanism preserves it. A RAM disk is not automatically an SSD.

**Compare an operation.** Reading a file on an HDD may wait for a head movement. Reading it on an SSD does not require that mechanical positioning. Opening a file already cached in RAM may avoid a storage-device read entirely. Identify which level is actually being accessed before applying a formula.

</div>

<h2 id="other-storage" data-reading-block>Other Auxiliary Storage Media and Drives</h2>

<div id="tape-and-mo" data-reading-block>

**Magneto-optical (MO) media** combine magnetic recording with optical techniques; the drive and media must support the same format. **Magnetic tape** records along a moving strip. It is suited to long sequential transfers and removable offline copies, but reaching a particular item can require positioning through earlier tape regions. This contrasts with direct access to an addressed disk block.

**PC cards** are a historical expansion-card form factor. A card can provide storage or another function; the shape of a card does not define its storage technology. Distinguish the medium, its drive, the controller and the interface that connects it to the computer.

**Choose by access pattern.** A large archive written and read in long runs has a different workload from a database making many small unpredictable reads. Capacity, positioning delay, sustained throughput, removability and retention requirements all matter. A second copy on the same physical device does not protect against losing that device; persistent storage and independent backup are different ideas.

</div>
