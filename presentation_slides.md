---
marp: true
theme: default
paginate: true
header: "Disciplined AI Integration"
footer: "Unclassified"
---

# Disciplined AI Integration: From Chatbots to RF Engineering
### Practical Vignettes & Mental Models

**Presenter:** 
**Date:** March 2026

---

# The "Why" - A Disciplined Approach

* AI is a **tool**, not a magic wand.
* Integration requires **discipline**, not just hype.
* **Goals:**
    - Solve mission problems, don't just "do AI."
    - Focus on **Reproducibility, Security, and Mission Alignment.**
    - Move from "Chatting" to "Engineering."

---

<!-- _header: "Phase 1: Foundations & Mental Models" -->

# Tokens: The Currency of Meaning

* LLMs don't see words; they see **Tokens**.
* Tokens are atomic fragments of meaning.
* **Why it matters:** 
    - Technical jargon (e.g., "DF-OFDM") can be "dense" or "expensive."
    - Understanding tokens = better prompt engineering.

**Visual:** `Different-Frequency` $\rightarrow$ `[Diff] [erent] [-] [Freq] [uency]`

---

# The Context Window: Your AI's "Desk Space"

* **The Desk Analogy:** 
    - Small Desk = AI forgets the start of the file.
    - Large Desk = AI holds the entire project codebase.
* **Mission Impact:** 
    - Once the desk is full, the oldest data "falls off."
    - **Disciplined Workflow:** Keeping the "desk" organized (Clean Context).

---

# Generalists vs. Specialists

| Type | Example | Best For... |
| :--- | :--- | :--- |
| **Generalist** | **Gemini** | Reasoning, planning, bridging RF + Coding domains. |
| **Specialist** | **Codex** | Syntax, boilerplate, deep code completion. |

* **Matching the right tool to the task is key.**

---

# Demystifying "Training"

1. **Base Training:** Teaching a child to speak (Foundational knowledge).
2. **Fine-Tuning:** Sending a graduate to flight school (Specialized expertise).
3. **RAG / In-Context Learning:** Giving an expert a **Technical Manual** to look at while they work.

* **Crucial Point:** Use cases utilize **Tier 3 (RAG)**—giving AI mission data in real-time.

---

<!-- _header: "Phase 2: The Workflow" -->

# The Gemini CLI Advantage

* **Moving from "Chat" to "Pipeline."**
* CLIs are for **engineers**; Chat is for humans.
* **Capabilities:**
    - Direct file manipulation.
    - Automated bug fixes in C++/Python.
    - Documentation generation at mission speed.

---

# Pair Programming: Gemini + Codex

* **Dual-Pilot Cockpit:**
    - **Gemini (The Architect):** Plans DF-OFDM structures & high-level DSP logic.
    - **Codex (The Mechanic):** Handles gritty syntax & fast autocompletion.
* **Result:** **3x faster development** compared to manual coding.

---

<!-- _header: "Phase 3: Infrastructure" -->

# Cloud vs. Local (Ollama & VRAM)

* **Cloud:** High reasoning, massive scale, fast (but data leaves the workspace).
* **Local (Ollama):** Privacy, **Data Sovereignty**, Air-Gapped utility.
* **VRAM:** The "Engine Displacement" of AI.
    - More VRAM = Smarter local models.
    - **Use Case:** Local classification of sensitive projects.

---

<!-- _header: "Phase 4: The Vignette - Project Opal Vanguard" -->

# The Evolution: Tactical SDR to Neural Receiver

* **The Challenge:** Transitioning from fragile GRC-only designs to a **Resilient Tactical Transceiver**.
* **Key Specs:** 
    - **Waveforms:** GFSK, DQPSK, CCSK, and **Level 9: Deep Shadow (CSS)**.
    - **Timing:** 120-byte tactical blocks with 15-row matrix interleaving.
    - **Hardening:** AES-CTR crypto-sync, Reed-Solomon FEC, and NRZ-I phase resilience.
* **The Physics Bottleneck:** USRP "Tag Paradox" and CFO-induced "Donut" constellations.

---

# The AI Solution: Breaking the Bottleneck

* **Surgical Logic (Gemini CLI Assisted):**
    - **Super-Vectorization:** Replaced thousands of Python loops with **NumPy Matrix Operations** (90% CPU reduction).
    - **FFT-Lock Frequency Estimation:** Transformed "Donuts" into "Blobs" by locking onto the 50kHz pilot spectrum.
    - **Threaded Offload:** Decoupled syncword search from heavy RS-FEC/CCSK math for fluid 2.0 Msps operation.

---

# Vanguard Data Factory (VDF) & Specter's Edge

* **The "Hardware Trinity":** Automated 3x USRP array (TX, RX, Adversary) for industrial-scale data harvesting.
* **Mission: Specter's Edge:** 
    - **The Mega-Harvest:** 250,000+ snapshots of "dirty" real-world hardware data.
    - **Diversity:** Sweeping 24 Classes x 4 Gains x 3 Drift levels x 3 Offsets.
* **Result:** A model trained on the "Reality of the Wire," not just idealized simulations.

---

# Impact & Results

* **Level 9 "Deep Shadow" Realized:** Ultra-resilient Chirp Spread Spectrum (CSS) operational.
* **Speed to Mission:** Dataset generation and model refinement reduced from **months to hours**.
* **Stability:** 100% bit-perfect logic verified via 18-point regression suite.
* **Success:** Level 7 OFDM Master and Level 9 CSS Master status achieved.

---

<!-- _header: "Phase 5: The Path Forward" -->

# The Path to "S" (Secret)

* **Capability Gaps:** Current manual workflows fail in classified environments.
* **The Roadmap:**
    - Deploy localized AI nodes (Ollama/Custom builds) in secure, air-gapped spaces.
* **Goal:** Mission integrity without external reliance.

---

# Conclusion / Q&A

* AI is a **Force Multiplier**, not a replacement.
* Start **small**, think **disciplined**, scale **fast**.
* **Questions?**

---
