---
marp: true
theme: default
paginate: true
header: "Disciplined AI Integration: Mike's Vignette"
footer: "Unclassified // FOUO (Sample)"
---

# Disciplined AI Integration: From Chatbots to RF Engineering
### Practical Vignettes & Mental Models for the Wing

**Presenter:** Mike (AI/ML Use Case Lead)
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
    - Large Desk = AI holds the entire Project Opal Vanguard codebase.
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

* **Crucial Point:** Most Wing use cases utilize **Tier 3 (RAG)**—giving AI mission data in real-time.

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
* **Result:** **3x faster development** on Project Opal Vanguard compared to manual coding.

---

<!-- _header: "Phase 3: Infrastructure" -->

# Cloud vs. Local (Ollama & VRAM)

* **Cloud:** High reasoning, massive scale, fast (but data leaves the wire).
* **Local (Ollama):** Privacy, **Data Sovereignty**, Air-Gapped utility.
* **VRAM:** The "Engine Displacement" of AI.
    - More VRAM = Smarter local models.
    - **Use Case:** Local classification of sensitive signals.

---

<!-- _header: "Phase 4: The Vignette - Project Opal Vanguard" -->

# The Challenge: Custom DF-OFDM

* **Problem:** Manual classification of frequency-hopping signals is slow and error-prone.
* **Signal Spec:** 120-byte stability frames, 500ms hopping.
* **RF Friction:** Phase-inversion and timing synchronization issues.

---

# The AI Solution: Neural Receivers

* Leveraging **Neural Receivers** via TensorFlow/Sionna.
* **AI-Assisted Code Gen:**
    - Gemini CLI generated the C++ correlators.
    - Software-Defined Timing Scanner for automatic FFT alignment.
* **Pattern Matching:** AI identifies signals in nanoseconds, not minutes.

---

# Impact & Results

* **Level 7 OFDM Master Achieved.**
* **Speed to Mission:** Time-to-classification reduced from **weeks to days**.
* **Reproducibility:** The entire workflow is automated and sharable across the Wing.

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
