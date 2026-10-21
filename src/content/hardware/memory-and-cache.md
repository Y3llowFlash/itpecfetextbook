---
id: fe-v1-ch01-memory-cache
title: Memory hierarchy & cache
description: Learn how registers, cache and RAM work together, and calculate effective memory access time with real ITPEC FE questions.
chapter: Hardware
contentVersion: hardware-pilot-1
---

<div id="learning-goals" data-reading-block>

By the end of this section, you will be able to place cache in the memory hierarchy, distinguish a hit from a miss, and calculate an average access time. You will then apply those ideas to three published ITPEC FE questions.

</div>

<h2 id="why-a-hierarchy" data-reading-block>Why do computers need several kinds of memory?</h2>

<div id="memory-tradeoff" data-reading-block>

A CPU can work on data much faster than a large memory can always deliver it. Very fast memory is expensive per bit, so a computer uses several layers. Small, fast layers hold the data needed immediately. Larger, slower layers hold more of the program and its data.

**Registers** are small storage locations inside the CPU used directly by instructions. **Cache** keeps copies of recently or frequently accessed memory blocks near the CPU. **Main memory (RAM)** holds programs and data currently in use. **Secondary storage**, such as an SSD, retains files when power is off. Cache and RAM are usually volatile; an SSD is persistent storage.

</div>

<figure class="hierarchy-figure" id="memory-hierarchy" data-reading-block aria-labelledby="hierarchy-caption">
  <div class="hierarchy-scale"><span>Faster · smaller</span><span>Slower · larger</span></div>
  <ol class="memory-layers">
    <li><strong>Registers</strong><span>Working values inside the CPU</span></li>
    <li><strong>Cache</strong><span>Copies of memory blocks close to the CPU</span></li>
    <li><strong>Main memory</strong><span>Programs and data in use · RAM</span></li>
    <li><strong>Secondary storage</strong><span>Persistent files · SSD or HDD</span></li>
  </ol>
  <figcaption id="hierarchy-caption">An original, simplified memory hierarchy. Real CPUs commonly have several cache levels, such as L1, L2 and L3.</figcaption>
</figure>

<h2 id="cache-hits-and-misses" data-reading-block>A small memory with a useful shortcut</h2>

<div id="cache-definition" data-reading-block>

<a class="concept-highlight" id="concept-cache-memory" data-concept="cache-memory" href="/practice/cache-memory/"><mark>Cache memory</mark><span class="concept-link-symbol" aria-hidden="true"> ↗</span></a> stores copies of data from a slower memory. When the CPU requests an item, a **cache hit** means that the item is found in the cache. A **cache miss** means it is absent, so the request must continue to another level. In a simple cache-and-RAM model, that next level is main memory.

The cache helps because programs tend to reuse nearby data. **Temporal locality** means an item accessed recently is likely to be accessed again. **Spatial locality** means nearby addresses are likely to be used. Caches transfer blocks, rather than guessing one independent byte at a time.

</div>

<div class="worked-note" id="hit-miss-example" data-reading-block>

**Try the idea.** Imagine repeatedly adding numbers in the same small array. Once the relevant blocks have entered the cache, many later reads can be hits. The first read of a block may be a miss. A miss does not mean the data was lost or that the CPU fetches it from ROM.

</div>

<h2 id="hit-ratio" data-reading-block>Hit ratio and miss ratio</h2>

<div id="ratios-definition" data-reading-block>

The **hit ratio**, usually written as *h*, is the fraction of accesses that hit. If 80 out of 100 accesses hit, then *h* = 0.8 = 80%. The **miss ratio** is 1 − *h*, which is 0.2 = 20% in this example. The two ratios add to 1.

Do not confuse a percentage with a count. A hit ratio of 0.8 says how often a hit occurs, not that the cache has 80 locations or that a hit takes 0.8 nanoseconds.

</div>

<h2 id="average-access-time" data-reading-block>Calculate a weighted average</h2>

<div id="weighted-average" data-reading-block>

If a hit takes *T*<sub>hit</sub> and the **complete miss path** takes *T*<sub>miss</sub>, the average time is:

<p class="formula">T<sub>average</sub> = h × T<sub>hit</sub> + (1 − h) × T<sub>miss</sub></p>

The word “complete” matters. If a question gives the **additional** time needed after a failed cache check, use the cache-check time plus that miss penalty. Equivalently, average time = cache-check time + miss ratio × miss penalty. Read the question's timing assumptions before substituting values.

</div>

<div class="worked-example" id="worked-calculation" data-reading-block>

### Worked example

A cache hit takes 10 ns. A complete miss takes 100 ns, including the cache lookup. The hit ratio is 0.9.

<p class="formula">0.9 × 10 + 0.1 × 100 = 9 + 10 = <strong>19 ns</strong></p>

Nine out of ten accesses are fast, but the occasional slow access still increases the average. If 100 ns were instead an additional miss penalty, the result would be 10 + 0.1 × 100 = **20 ns**. These describe different timing models.

</div>

<h2 id="exam-checklist" data-reading-block>Before you answer an exam question</h2>

<div id="exam-reading-checks" data-reading-block>

1. Identify whether the question gives a **hit ratio or a miss ratio**.
2. Check the units: keep all times in nanoseconds, or convert them consistently.
3. Decide whether the main-memory time includes checking the cache.
4. Write the two possible access paths and weight each by its probability.
5. Check that the result lies between the fastest and slowest complete path times.

If two systems have the same effective time, write an expression for each system using the same unknown hit ratio, then set the expressions equal. You will use this technique in the linked practice.

</div>

<h2 id="section-recap" data-reading-block>Keep these three ideas</h2>

<div id="recap-content" data-reading-block>

Cache holds copies of memory blocks to reduce average access time. A hit finds the item in cache; a miss continues down the hierarchy. Average access time is a weighted average, and the correct formula depends on whether the stated miss time is a complete path or an extra penalty.

</div>
