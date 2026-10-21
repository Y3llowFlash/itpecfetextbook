---
id: fe-v1-ch01-s02
title: Data Representation in Computers
---

<div id="data-goals" data-reading-block>

The same bit pattern can represent a number, a character, an instruction or a color. Its meaning comes from the encoding and context. Start with the capacity of a bit pattern, then work through positional notation, numeric formats, errors and operations on bits.

</div>

<h2 id="data-representation" data-reading-block>Data Representation</h2>

<div id="bits-and-units" data-reading-block>

A **bit** has two possible values, 0 and 1. A **byte** is eight bits. A **word** is a processor's natural grouping for some operations; its width depends on the architecture. Do not assume that the word size, address width and external bus width must all be identical.

Each additional independent bit doubles the number of available patterns. With *n* bits there are 2<sup>n</sup> patterns. An unsigned integer uses these for values from 0 through 2<sup>n</sup> − 1. Eight bits provide 256 patterns, but the greatest unsigned value is 255, because zero is one of the values.

**Worked example.** A code needs to identify 40 equipment types. Five bits offer only 32 patterns; six offer 64. The minimum width is therefore six bits. Unused patterns do not automatically create additional equipment types: they are simply codes available for future use or error detection.

Information amount can also describe surprise. An event of probability *p* carries self-information I = −log<sub>2</sub>(*p*) bits. An event with probability 1/8 carries three bits of information. This is different from saying that every stored record occupies three bits: storage format and event probability answer different questions.

| Unit or prefix | Meaning | Example |
|---|---|---|
| B and bit | Bytes and bits are different units | 16 B = 128 bits |
| k, M, G, T, P | Decimal powers 10³, 10⁶, 10⁹, 10¹², 10¹⁵ | 1 MB = 1,000,000 B in decimal notation |
| Ki, Mi, Gi, Ti, Pi | Binary powers 2¹⁰, 2²⁰, 2³⁰, 2⁴⁰, 2⁵⁰ | 1 MiB = 1,048,576 B |
| ms, µs, ns, ps | 10⁻³, 10⁻⁶, 10⁻⁹, 10⁻¹² seconds | 2 µs = 2,000 ns |

Older descriptions and exam problems sometimes use KB or MB for binary quantities. Always follow an explicit definition in the question. Never silently mix bits/s with bytes/s or milliseconds with seconds.

</div>

<h2 id="radix-conversion" data-reading-block>Radix and Radix Conversion</h2>

<div id="radix-weights" data-reading-block>

In a positional number system, each digit has a weight that is a power of the **radix**, or base. The units digit has weight *b*<sup>0</sup> = 1. Moving left multiplies the weight by *b*; moving right across the radix point divides by *b*. The allowed digits are 0 through *b* − 1.

| Base | Allowed digits | Weights near the radix point |
|---|---|---|
| Binary, 2 | 0, 1 | 8, 4, 2, 1 . 1/2, 1/4, 1/8 |
| Octal, 8 | 0–7 | 512, 64, 8, 1 . 1/8, 1/64 |
| Decimal, 10 | 0–9 | 1,000, 100, 10, 1 . 1/10, 1/100 |
| Hexadecimal, 16 | 0–9 and A–F | 4,096, 256, 16, 1 . 1/16, 1/256 |

Hexadecimal A through F stand for decimal 10 through 15. They are digits, not variables in this notation. A subscript such as (2B)<sub>16</sub> makes the base explicit.

<a class="concept-highlight" id="concept-radix-conversion" data-concept="radix-conversion" href="/practice/radix-conversion/"><mark>Radix conversion</mark> ↗</a> to decimal means multiplying each digit by its positional weight and adding. For example, (2B.8)<sub>16</sub> = 2 × 16 + 11 × 1 + 8/16 = **43.5**. The digit after the point is not a decimal tenth.

</div>

<div class="worked-example" id="radix-worked" data-reading-block>

**Decimal to binary: 26.625.** For the integer part, repeatedly divide by two: 26→13 remainder 0; 13→6 remainder 1; 6→3 remainder 0; 3→1 remainder 1; 1→0 remainder 1. Read the remainders upward: **11010**.

For the fractional part, repeatedly multiply by two and record each integer part: 0.625×2 = 1.25 gives 1; 0.25×2 = 0.5 gives 0; 0.5×2 = 1 gives 1. Read these in the order produced: **.101**. Thus 26.625 = (11010.101)<sub>2</sub>. Check by summing 16 + 8 + 2 + 1/2 + 1/8.

</div>

<div id="grouping-digits" data-reading-block>

To convert between binary and hexadecimal, group bits in fours **outward from the radix point**. For octal, group them in threes. Add zeros only at the outside ends where they do not change the value. For example, (101101.01)<sub>2</sub> becomes (0010 1101 . 0100)<sub>2</sub> = (2D.4)<sub>16</sub>. Appending a zero to the right end of a fraction is harmless; appending one to an integer multiplies it by two.

Not every terminating decimal fraction terminates in binary. For example, 1/10 has a repeating binary expansion. A finite representation must then round or truncate; the error is a consequence of the chosen format, not a failure of the conversion method.

</div>

<h2 id="representation-form" data-reading-block>Representation Form of Data</h2>

<div id="encoding-context" data-reading-block>

Before interpreting bytes, identify the format. The byte 01000001 can be the unsigned number 65 or an encoded letter A in ASCII. Neither interpretation follows from the bits alone. Correctly moving bytes does not ensure correctly interpreting them.

</div>

<h3 id="character-data" data-reading-block>Character Data</h3>

<div id="character-encoding" data-reading-block>

A character code associates a written symbol or control function with a value. **ASCII** is a seven-bit code with 128 positions. **EBCDIC** is a different historical code family; a byte meaningful under one encoding can mean something else under another. **JIS**, Shift JIS and EUC are important in the history of Japanese character representation. Do not assume that all character encodings use one byte per character.

**Unicode** assigns code points, such as U+0041 for A. An encoding such as UTF-8 turns code points into code units or bytes. UTF-8 uses one to four bytes per Unicode scalar value; the familiar ASCII subset uses one byte. A displayed symbol may combine several code points, so byte count, code-point count and displayed-character count can differ. Encoding and font are also different: the encoding identifies characters; a font supplies their visual forms.

**Concrete example.** The text “AB” takes two bytes in UTF-8 without a terminator or other overhead. A two-symbol string containing non-ASCII symbols need not take two bytes. When estimating file size, use the specified encoding and count what the question actually asks for.

</div>

<h3 id="numeric-data" data-reading-block>Numeric Data</h3>

<div id="decimal-codes" data-reading-block>

**Decimal-coded numbers.** In binary-coded decimal (BCD), each decimal digit has its own four-bit code. Decimal 58 becomes 0101 1000 in BCD, whereas the ordinary binary integer 58 is 00111010. Codes 1010 through 1111 are not decimal digit codes. Packed decimal stores two digit-sized nibbles per byte, often reserving a final nibble for a sign; a common convention uses hexadecimal C for positive and D for negative. Zoned decimal uses a byte for each decimal digit, with zone/sign information. The exact sign convention is part of the format, not a universal meaning of the bit pattern.

**Fixed-point numbers** have an agreed radix-point position. If an unsigned eight-bit value has four fractional bits, stored integer 24 represents 24/16 = 1.5. The precision step is 1/16. Increasing fractional precision without increasing the total width reduces the available integer range.

| Signed integer format | How a negative value is encoded | Eight-bit range |
|---|---|---|
| Sign and magnitude | One sign bit plus the absolute value | −127 to +127, with two zeros |
| One's complement | Invert all bits of the positive representation | −127 to +127, with two zeros |
| Two's complement | Invert the positive representation and add one | −128 to +127, with one zero |

In eight-bit two's complement, +5 is 00000101. Invert to 11111010 and add one to get −5 = **11111011**. Another interpretation is that the most significant bit has weight −128 and the remaining bits have weights 64 through 1: −128 + 64 + 32 + 16 + 8 + 2 + 1 = −5. Sign extension repeats the sign bit when increasing the width.

Addition uses the same binary adder for positive and negative values. For example, 7 + (−5) = 00000111 + 11111011 = 1 00000010; discard the carry beyond the eight-bit width to obtain 2. A carry-out and signed overflow are different: adding two positive numbers and obtaining a negative result is signed overflow even if there is no carry-out.

</div>

<div id="floating-point-layout" data-reading-block>

<a class="concept-highlight" id="concept-floating-point" data-concept="floating-point" href="/practice/floating-point/"><mark>Floating-point representation</mark> ↗</a> stores a sign, an exponent and a significand. It allows a wide range of magnitudes, but gives finite precision. A normalized binary number has a nonzero leading digit; for a normal binary IEEE 754 value that leading digit is 1.

<figure class="bit-figure" aria-label="IEEE 754 binary32 field layout"><div class="bit-fields"><span>Sign<br /><strong>1 bit</strong></span><span>Biased exponent<br /><strong>8 bits</strong></span><span>Stored fraction<br /><strong>23 bits</strong></span></div><figcaption>Original field diagram: 32 bits in total. The leading 1 of a normal significand is implicit.</figcaption></figure>

For a normal binary32 value, with 0 &lt; E &lt; 255:

<p class="formula">value = (−1)<sup>S</sup> × 2<sup>E − 127</sup> × (1 + F)</p>

Here F is the binary fraction encoded by the 23 stored bits. For **10.5**, binary 1010.1 normalizes to 1.0101 × 2³. Therefore S=0, E=3+127=130, and the stored fraction begins 0101 followed by zeros. The implicit leading 1 must not be counted again in F or omitted from the significand.

Exponent fields of all zeros or all ones are special cases: zeros/subnormal numbers, infinities and NaNs do not all follow the normal-number formula. An exam may deliberately restrict E so that only the normal case is relevant. Read that restriction before decoding the fields.

</div>

<h3 id="numeric-error" data-reading-block>Error</h3>

<div id="error-types" data-reading-block>

Finite formats have range and precision limits. **Overflow** exceeds the available range. **Underflow** concerns a nonzero magnitude too small for the format's normal range; some formats support subnormal values with reduced precision. **Rounding error** arises when an exact value is replaced with a nearby representable value. **Truncation error** can arise when a computation or expansion is cut short.

**Cancellation**, or loss of significant digits, occurs when nearly equal rounded values are subtracted. Suppose measurements rounded to four significant digits are 1.234 and 1.233: their difference has very little reliable precision. **Loss of trailing digits** can occur when a small value is added to a much larger floating-point value and falls beyond its precision. The small quantity was not necessarily zero; the selected format could not retain its effect on that sum.

Absolute error = |approximation − exact value|. Relative error divides that amount by |exact value|, when the exact value is nonzero. Approximating 2/3 by 0.67 gives absolute error about 0.00333 and relative error about 0.005, or 0.5%. State whether an error measure is a fraction or a percentage.

Use more suitable precision, avoid subtracting nearly equal quantities where an equivalent stable expression exists, and consider adding smaller-magnitude terms first. These can reduce error; they do not turn finite arithmetic into exact real-number arithmetic.

</div>

<h3 id="shift-operation" data-reading-block>Shift Operation</h3>

<div id="shifting-bits" data-reading-block>

A **logical shift** moves bits and fills vacated positions with zeros. A **rotation** moves bits around the ends instead of discarding them. An **arithmetic right shift** repeats the sign bit of a two's-complement value to preserve its sign. For example, eight-bit −8 = 11111000 becomes 11111100, or −4, after one arithmetic right shift. Shifting a negative odd value right can round differently from division that truncates toward zero.

For an integer whose result remains representable, a left shift by *k* positions multiplies by 2<sup>k</sup>. In a fixed-width machine, discarded high bits can cause overflow, so the mathematical identity needs that qualification. Some textbook descriptions reserve the sign bit when illustrating arithmetic shifts; follow the word width and shifting rule stated in the question.

<a class="concept-highlight" id="concept-signed-shifts" data-concept="signed-shifts" href="/practice/signed-shifts/"><mark>Signed integers and shifts</mark> ↗</a> let us replace certain multiplications with powers of two. For example, 13n = 8n + 4n + n = (n shifted left 3) + (n shifted left 2) + n, subject to sufficient width. Work out the algebra before moving bits.

</div>

<div id="mask-example" data-reading-block>

<a class="concept-highlight" id="concept-bit-masks" data-concept="bit-masks" href="/practice/bit-masks/"><mark>Bit masks</mark> ↗</a> select individual positions. AND with 1 retains a bit; AND with 0 clears it. OR with 1 sets a bit. XOR with 1 toggles a bit. NOT reverses every bit within the selected width.

For source 10110110 and mask 11110000, AND gives **10110000**. This retains the upper four bits in place; it does not move them into the low positions. An additional four-bit logical right shift would produce 00001011. Distinguishing “retain,” “clear” and “shift” prevents a common exam mistake.

</div>
