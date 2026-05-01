# GMSK Modulation: Team Training Document

**Audience:** RF/Modulation engineers with working knowledge of FSK and BPSK  
**Duration:** ~90 minutes with exercises  
**Prepared:** May 2026

---

## Table of Contents

1. [Building the Bridge: From FSK to MSK to GMSK](#1-building-the-bridge-from-fsk-to-msk-to-gmsk)
2. [The Gaussian Filter: MSK → GMSK](#2-the-gaussian-filter-msk--gmsk)
3. [GMSK Signal Mathematics](#3-gmsk-signal-mathematics)
4. [GMSK Spectrum](#4-gmsk-spectrum)
5. [GMSK Receiver Design](#5-gmsk-receiver-design)
6. [GMSK in Practice: GSM](#6-gmsk-in-practice-gsm)
7. [GMSK vs. Other Schemes](#7-gmsk-vs-other-schemes-side-by-side)
8. [GMSK Generation (Transmitter Architecture)](#8-gmsk-generation-transmitter-architecture)
9. [Key Exercises](#9-key-exercises)
10. [Summary](#10-summary)

---

## 1. Building the Bridge: From FSK to MSK to GMSK

### 1.1 What You Already Know (Quick Recap)

In **FSK**, a binary `1` maps to frequency f₁ and a binary `0` maps to f₀. The modulated signal jumps abruptly between frequencies at symbol boundaries. This produces a wide occupied bandwidth because of the sharp phase discontinuities.

In **BPSK**, phase is the information carrier. Abrupt phase shifts (0°/180°) also produce wide spectral sidebands.

The common theme: **sharp transitions = wide bandwidth**.

---

### 1.2 MSK: The First Step Toward Elegant FSK

**Minimum Shift Keying (MSK)** is the direct foundation of GMSK. Start here.

MSK is binary FSK with one critical constraint — the **modulation index h = 0.5**.

The modulation index is defined as:

```
h = Δf / fb
```

Where:
- `Δf` = peak frequency deviation
- `fb` = bit rate

Setting h = 0.5 means the two frequencies are separated by exactly half the bit rate. This is the **minimum separation** at which two FSK tones remain orthogonal over a bit period — hence "minimum shift."

**Why orthogonal?** Two signals are orthogonal if their inner product over a symbol period equals zero:

```
∫₀ᵀ cos(2πf₁t) · cos(2πf₀t) dt = 0
```

This holds when `f₁ - f₀ = n/(2T)` for integer n. MSK uses n = 1.

#### MSK Key Properties

| Property           | Value                        |
|--------------------|------------------------------|
| Modulation index   | 0.5                          |
| Phase continuity   | Yes — continuous phase       |
| Phase change / bit | ±90° (π/2 radians)           |
| Spectral efficiency| Better than standard FSK     |

The **continuous phase** is what distinguishes MSK from ordinary FSK. At each bit boundary the signal phase does not jump — it arrives at a natural continuation point determined by the current bit value.

**MSK phase trajectory:** think of it as a phase wheel that rotates +90° for a `1` and −90° for a `0` over each bit period.

```
Bit:    1     0     1     1     0
Phase:  0° → 90° → 0° → 90° → 180° → 90°
```

This phase continuity narrows the spectrum compared to discontinuous FSK, but MSK still has **relatively high sidelobes** because the instantaneous frequency transitions remain abrupt (rectangular frequency pulses switching between f₁ and f₀).

---

## 2. The Gaussian Filter: MSK → GMSK

### 2.1 The Spectral Problem with MSK

In MSK the data bits drive a **rectangular frequency pulse** — frequency snaps instantly to f₁ or f₀ and holds for the full bit period T. A rectangular pulse in time produces a sinc-shaped spectrum, which has slowly-decaying sidelobes.

For systems such as GSM, where channels are packed closely together, those sidelobes cause adjacent-channel interference (ACI).

**The solution:** smooth the frequency pulse before it drives the modulator.

---

### 2.2 The Gaussian Filter

GMSK passes each rectangular bit pulse through a **Gaussian low-pass filter** before frequency modulation. The Gaussian filter impulse response has the form:

```
h(t) = (1 / √(2π)σT) · exp(−t² / (2σ²T²))
```

In practice the filter is characterized by the normalized **bandwidth-time product BT**:

```
B = 3 dB bandwidth of the Gaussian filter
T = bit period
```

The Gaussian filter spreads each bit's frequency pulse over several bit periods — this is **controlled intersymbol interference (ISI)**, introduced intentionally to gain spectral efficiency.

---

### 2.3 The BT Product — The Key Design Knob

BT is the single most important design parameter in GMSK.

| BT        | Effect                                                        |
|-----------|---------------------------------------------------------------|
| BT → ∞   | No filtering → pure MSK                                       |
| BT = 0.5  | Moderate smoothing, moderate ISI                              |
| BT = 0.3  | **Used in GSM** — good spectral containment, manageable ISI  |
| BT → 0   | Maximum smoothing → severe ISI → unusable                     |

**Lower BT = narrower spectrum = more ISI = more complex receiver.**

This is the fundamental GMSK design tradeoff.

---

## 3. GMSK Signal Mathematics

### 3.1 The Modulated Signal

A GMSK signal is a continuous-phase FM signal of the form:

```
s(t) = A · cos(2πfct + φ(t))
```

All information is carried in the **instantaneous phase**:

```
φ(t) = 2πh ∫₋∞ᵗ m̃(τ) dτ
```

Where:
- `h = 0.5` (modulation index, inherited from MSK)
- `m̃(t)` = data stream after Gaussian filtering

The Gaussian-filtered frequency pulse for a single isolated bit is:

```
g(t) = (1/2T) · [Q(2πB·(t − T/2)/√(ln2)) − Q(2πB·(t + T/2)/√(ln2))]
```

Where Q is the complementary error function tail integral.

---

### 3.2 Phase Trellis

Unlike pure MSK, GMSK phase does not make clean ±90° jumps per bit. The Gaussian filter spreads each bit's phase contribution across neighboring bit periods. The phase trellis (phase vs. time across all possible bit sequences) shows **smooth curves** rather than straight-line segments.

```
MSK Phase Trellis          GMSK Phase Trellis (BT = 0.3)
                                                          
  180° ─  /   /              180° ─  ~~~~~   ~~~~~        
   90° ─ / ─ / ─             90°  ─  ~~~~ ─ ~~~~         
    0° ─/ ─ /                 0°  ─ ~~~~   ~~~~           
```

This smooth phase trellis is central to understanding GMSK receiver design.

---

## 4. GMSK Spectrum

### 4.1 Spectral Shape

GMSK produces a more compact spectrum than MSK. The 99% occupied bandwidth for GMSK with BT = 0.3:

```
~0.86/T  Hz   (vs. ~1.2/T for MSK)
```

The sidelobes fall much faster, making dense channel plans feasible.

### 4.2 Power Spectral Density Comparison

```
Power (dB)
  |
  |  ██ GMSK (BT=0.3)
  |  ████
  |  ██████  ░░ MSK
  |  ████████░░░░░░
  |  ██████████░░░░░░░░░░
  |  ████████████████████░░░░░░░░░░░░
  |_________________________________________________ Frequency
                fc
```

GMSK is significantly more spectrally compact and rolls off faster beyond the main lobe.

---

## 5. GMSK Receiver Design

### 5.1 The ISI Challenge

Because the Gaussian filter spreads each bit across approximately 3 bit periods (for BT = 0.3), each received sample is influenced by several transmitted bits — intentional ISI. The receiver must account for this memory.

---

### 5.2 Demodulation Approaches

#### Option A: Simple FM Discriminator (suboptimal)

- Treat the signal as standard FM demodulation
- Apply a threshold detector to the discriminator output
- Suffers ~1–2 dB SNR penalty due to unresolved ISI
- Lowest receiver complexity
- Used in cost-sensitive or simpler applications

#### Option B: Viterbi Algorithm / MLSE (optimal)

- Model the Gaussian filter and channel as a trellis (finite state machine)
- Use Maximum Likelihood Sequence Estimation (MLSE) to find the most probable transmitted bit sequence
- For BT = 0.3 the effective ISI spans ~3 symbols → 4-state or 8-state Viterbi trellis
- Fully recovers the SNR penalty from ISI
- Used in GSM base stations and quality handsets

#### Option C: Differential Detection

- Exploits phase differences between adjacent bit periods
- Lower complexity than Viterbi, approximately 1 dB worse than optimal MLSE
- Used in low-power Bluetooth-class applications

---

### 5.3 Viterbi Trellis Example

With BT = 0.3 the ISI memory length L ≈ 2 bits, requiring a 4-state trellis. States are defined by the previous 2 transmitted bits:

```
States: {00, 01, 10, 11}

From state 00:  receive 0 → new state 00
                receive 1 → new state 01

From state 01:  receive 0 → new state 10
                receive 1 → new state 11

From state 10:  receive 0 → new state 00
                receive 1 → new state 01

From state 11:  receive 0 → new state 10
                receive 1 → new state 11
```

Each branch metric is computed against the expected phase increment for that state transition. The Viterbi algorithm finds the minimum accumulated metric path through the trellis, recovering the transmitted bit sequence.

---

## 6. GMSK in Practice: GSM

GSM is the canonical real-world GMSK deployment. Its parameter choices illustrate the key engineering tradeoffs directly.

| Parameter        | Value                          |
|------------------|--------------------------------|
| Bit rate         | 270.833 kbps                   |
| BT product       | 0.3                            |
| Channel spacing  | 200 kHz                        |
| Carrier bands    | 900 MHz and 1800 MHz           |
| Modulation index | 0.5                            |

GSM chose BT = 0.3 as the sweet spot between:
- **Spectral containment:** 200 kHz channel spacing at ~271 kbps is only possible with aggressive filtering
- **Manageable ISI:** L ≈ 2–3 bits → practical 8-state Viterbi decoder

The GSM equalizer uses a 5-tap MLSE Viterbi decoder to handle both the GMSK ISI and the multipath fading channel simultaneously.

---

### 6.1 Other Applications

| System              | Modulation        | BT  |
|---------------------|-------------------|-----|
| GSM (2G cellular)   | GMSK              | 0.3 |
| Bluetooth Classic   | GFSK (h ≈ 0.35)  | 0.5 |
| DECT cordless       | GFSK              | 0.5 |
| Satellite TT&C      | GMSK              | 0.5–0.7 |
| APRS / amateur AX.25| AFSK/GMSK-like    | varies |

---

## 7. GMSK vs. Other Schemes: Side-by-Side

| Property                    | BPSK     | FSK (h=1) | MSK      | GMSK (BT=0.3) |
|-----------------------------|----------|-----------|----------|----------------|
| Constant envelope           | No       | Yes       | Yes      | Yes            |
| Phase continuity            | No       | No        | Yes      | Yes            |
| Spectral efficiency         | Moderate | Poor      | Good     | Very good      |
| Intentional ISI             | None     | None      | None     | Yes            |
| Receiver complexity         | Low      | Low       | Moderate | High           |
| Power amp linearity required| High     | Low       | Low      | Low            |

**Constant envelope** is a critical practical advantage shared by MSK and GMSK. Because signal amplitude never varies, you can use a **nonlinear (saturated) power amplifier** — far more efficient than the linear PAs required by BPSK or QAM. This matters greatly for battery-powered portable devices and high-power transmitters where efficiency is paramount.

---

## 8. GMSK Generation (Transmitter Architecture)

```
           ┌──────────────┐    ┌──────────────────────┐    ┌──────────────┐
Data bits  │  NRZ Encoder │    │   Gaussian LPF       │    │  VCO / FM   │
──────────►│  (+1 / −1)   │───►│  h(t),  BT = 0.3     │───►│  Modulator  │──► RF Out
           └──────────────┘    └──────────────────────┘    └──────────────┘
                                                                  fc = carrier
```

**Step 1 — NRZ encode:** Map bits to ±1 (or corresponding voltage levels).

**Step 2 — Gaussian filter:** Smooth the rectangular frequency pulses. The filter output represents the desired instantaneous frequency deviation profile.

**Step 3 — VCO / FM modulator:** The VCO integrates the frequency deviation signal to produce continuous phase modulation on the carrier. The Gaussian filter has already shaped the deviation profile, so the VCO output is GMSK.

A voltage-controlled oscillator is the simplest FM modulator. In digital implementations the phase is computed numerically using a direct digital synthesizer (DDS) or I/Q modulator driven by precomputed waveforms.

---

## 9. Key Exercises

### Exercise 1 — BT Intuition

For BT = 0.5 vs. BT = 0.3, sketch qualitatively how the frequency pulse shape changes over time for an isolated `1` bit surrounded by `0`s.

- Which BT value produces more spreading into adjacent bit periods?
- Which BT value produces a narrower RF spectrum, and why?

---

### Exercise 2 — Phase Calculation (Pure MSK, BT → ∞)

Given: bit rate = 100 kbps, h = 0.5, starting phase = 0°, bit sequence = `1, 0, 1, 1`

1. Calculate the accumulated phase at each bit boundary.
2. Determine the two carrier frequencies f₁ and f₀ around a center frequency of 900 MHz.
3. What is the total frequency deviation Δf?

*Hint: each `1` adds +90°, each `0` adds −90° to the accumulated phase.*

---

### Exercise 3 — Receiver Complexity

For BT = 0.3 with effective ISI memory L = 2 bits:
1. How many states does the Viterbi trellis require?
2. How many trellis states would be needed if BT = 0.2 (L = 3 bits)?
3. Why does reducing BT increase receiver hardware cost?

---

### Exercise 4 — Spectrum and Channel Planning

A GMSK system operates at 1 Mbps with BT = 0.3.

1. Estimate the approximate 99% occupied bandwidth.
2. Propose a minimum channel spacing to achieve 20 dB adjacent-channel isolation.
3. How does your answer change if the bit rate doubles to 2 Mbps?

---

### Exercise 5 — System Tradeoff Analysis

You are designing a telemetry system with the following constraints:
- Available RF bandwidth: 25 kHz per channel
- Required data rate: 9.6 kbps
- Platform: battery-powered sensor node

1. Is GMSK a suitable modulation choice? Why or why not?
2. What BT value would you select and why?
3. What receiver architecture would you recommend given the power constraints?

---

## 10. Summary

| Concept              | Core Idea                                                                 |
|----------------------|---------------------------------------------------------------------------|
| MSK                  | FSK with h = 0.5; continuous phase; minimum orthogonal tone separation    |
| Gaussian filter      | Smooths frequency pulses; narrows spectrum; introduces controlled ISI     |
| BT product           | Key tradeoff: lower = narrower spectrum = more ISI = more complex receiver|
| Constant envelope    | Enables efficient nonlinear PAs — critical for portable/mobile devices    |
| MLSE receiver        | Viterbi decoder resolves the intentional ISI from the Gaussian filter     |
| GSM                  | Canonical deployment: BT = 0.3, 270.833 kbps, 200 kHz channels           |

---

### One-Line Intuition

> **GMSK is MSK with a Gaussian blur applied to the frequency transitions — trading a harder receiver problem for a much cleaner spectrum.**

---

## Further Reading

- Murota, K. and Hirade, K. — *"GMSK Modulation for Digital Mobile Radio Telephony,"* IEEE Transactions on Communications, 1981. (The original paper)
- Proakis, J. — *Digital Communications*, Chapter 5 (CPM and MSK)
- Haykin, S. — *Communication Systems*, Chapter 4 (Angle Modulation)
- ETSI TS 145 004 — GSM modulation specification (primary standard reference)

---

*Recommended next topic: Laurent decomposition of GMSK — shows how GMSK can be approximated as a sum of linearly modulated pulses, enabling simpler coherent I/Q demodulation without a full Viterbi decoder.*
