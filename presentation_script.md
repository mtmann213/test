# Presentation Script: Disciplined AI Integration

## Slide 1: Title Slide
- **Title:** Disciplined AI Integration: From Chatbots to RF Engineering
- **Subtitle:** Practical Vignettes & Mental Models for the Wing
- **Presenter:** Mike (AI/ML Use Case Lead)
- **Visual Idea:** A clean, modern graphic showing an SDR (Software Defined Radio) connected to a neural network node.

## Slide 2: The "Why" - A Disciplined Approach
- **Key Message:** AI is a tool, not a magic wand. Integration requires discipline, not just hype.
- **Talking Points:**
    - Moving past "What is AI?" to "How do we solve mission problems?"
    - The difference between using AI as a curiosity vs. using it as a pipeline component.
    - Focus on Reproducibility, Security, and Mission Alignment.

---

## Phase 1: Foundations & Mental Models

## Slide 3: Tokens - The Currency of Meaning
- **Key Message:** AI doesn't see words; it sees "tokens."
- **Visual Idea:** A sentence broken into color-coded fragments (e.g., "Different-Frequency" -> "Diff", "erent", "-", "Freq", "uency").
- **Talking Points:**
    - Tokens are the atomic units of LLMs.
    - Understanding tokens helps explain why some technical jargon "costs" more in context than simple words.
    - It's not just about word count; it's about the density of meaning.

## Slide 4: The Context Window - Your AI's "Desk Space"
- **Key Message:** The context window is the limit of what the AI can "remember" at once.
- **Visual Idea:** An image of a desk. Small desk = small context (forgetting files). Large desk = large context (Project Opal Vanguard's entire codebase fits).
- **Talking Points:**
    - If the desk is full, the oldest "files" (data) get pushed off.
    - This explains why AI can lose track of a long conversation.
    - Strategy: Keeping the "desk" organized (Clean prompt engineering).

## Slide 5: Generalists vs. Specialists
- **Key Message:** Not all models are created equal.
- **Visual Idea:** A Swiss Army Knife (Gemini) vs. a Precision Scalpel (Codex/Sionna-specific logic).
- **Talking Points:**
    - **Generalists (Gemini):** Great for reasoning, planning, and bridging complex domains (RF + Coding).
    - **Specialists (Codex):** Optimized for syntax, boilerplate, and deep code completion.
    - Matching the right tool to the task is part of a disciplined approach.

## Slide 6: Demystifying "Training"
- **Key Message:** Stop saying "train a model" when you mean "give it a manual."
- **Visual Idea:** Three tiers:
    1. **Base Training:** A child learning to speak (Foundational).
    2. **Fine-Tuning:** A graduate going to Flight School (Specialized).
    3. **RAG (In-Context):** An expert with a Technical Manual (Project-specific).
- **Talking Points:**
    - Most of our work is Tier 3 (RAG/In-Context). We give the AI the mission data it needs *now*.

---

## Phase 2: The Workflow

## Slide 7: The Gemini CLI Advantage
- **Key Message:** Moving from "Chat" to "Pipeline."
- **Visual Idea:** A screenshot of a terminal window running `gemini "fix the dsp logic in this file"`.
- **Talking Points:**
    - Chat interfaces are for humans; CLIs are for engineers.
    - Using AI directly in the dev loop reduces friction.
    - Automating documentation, boilerplate, and bug fixes.

## Slide 8: Pair Programming: Gemini + Codex
- **Key Message:** Models work better together.
- **Visual Idea:** A "Dual Pilot" cockpit diagram. Mike (Gemini) + Teammate (Codex).
- **Talking Points:**
    - **Gemini (The Architect):** Plans the DF-OFDM structure, handles high-level DSP logic.
    - **Codex (The Mechanic):** Handles the gritty C++ syntax and fast autocompletion.
    - Result: 3x faster development on Project Opal Vanguard.

---

## Phase 3: Infrastructure

## Slide 9: Cloud vs. Local (Ollama & VRAM)
- **Key Message:** You don't always need the cloud.
- **Visual Idea:** A side-by-side comparison. Cloud (Scale/Speed) vs. Local (Privacy/Air-Gapped).
- **Talking Points:**
    - **Ollama:** Running powerful models (Llama 3, Mistral) on local hardware.
    - **VRAM:** The "engine displacement" of AI. More VRAM = bigger, smarter local models.
    - Critical for Air-Gapped systems and sensitive signal classification.

---

## Phase 4: The Vignette - Project Opal Vanguard

## Slide 10: The Objective: A Custom 2-Way Protocol
- **Key Message:** The core of Project Opal Vanguard is the engineering of a ground-up, fully customizable tactical communication protocol.
- **Visual Idea:** A flowchart showing the Link Layer (Session Manager, Packetizer, Depacketizer) and the flow of a 2-way SYN -> ACK handshake.
- **Talking Points:**
    - We aren't just using off-the-shelf standards; we've built a **Tactical Protocol** from the bit-level up.
    - **Session Management:** Developed autonomous SYN -> ACK handshakes with random-backoff to ensure stable 2-way links in high-collision environments.
    - **Physical Hardening:** 120-byte tactical blocks with self-healing headers and 32-bit Hamming syncwords to ensure links stay up even during signal fading.
    - **The Challenge:** Balancing absolute protocol integrity with the "Physics Bottleneck" of USRP hardware timing and frequency drift.

## Slide 11: The AI Solution: Protocol Engineering at Speed
- **Key Message:** Gemini was a force multiplier for link-layer logic and high-speed DSP optimization.
- **Visual Idea:** A "Speed of Iteration" chart or a code snippet showcasing a NumPy-vectorized interleaver.
- **Talking Points:**
    - **Link-Layer Optimization:** Replaced slow Python bit-loops with NumPy-vectorized matrix operations, achieving a 90% CPU reduction in the "hot path."
    - **Adaptive Waveforms:** Rapidly developed and tested a library of waveforms (GFSK, DBPSK, and ultra-resilient CSS) using AI-assisted code generation.
    - **Threaded Offload:** Decoupled the time-sensitive syncword search from heavy link-layer math (RS-FEC/CCSK), enabling fluid 2-way operation at 2.0 Msps.

## Slide 12: Vanguard Data Factory (VDF) & Specter's Edge
- **Key Message:** Protocol validation requires industrial-scale "Reality Testing."
- **Visual Idea:** A high-level diagram of the "Hardware Trinity": 3 USRPs (TX, RX, and Adversary) testing the 2-way link in a loop.
- **Talking Points:**
    - **VDF:** A fully automated pipeline for stress-testing the protocol under real-world hardware conditions.
    - **Mission: Specter's Edge:** 250,000+ snapshots captured across sweeping gains, drift levels, and interference profiles.
    - **The Result:** We didn't just build a protocol; we built an **industrial validation engine** to ensure that protocol is bulletproof on the wire.

## Slide 13: Impact: From Prototype to Production
- **Key Message:** A fully functional, production-ready 2-way tactical link achieved at record speed.
- **Visual Idea:** A 100% logic accuracy confirmation (18-point regression suite pass).
- **Talking Points:**
    - **Level 9 Realized:** The protocol now supports ultra-resilient Chirp Spread Spectrum (CSS) for "Deep Shadow" operations.
    - **Final State:** A fully customizable, 2-way tactical communication system that is resilient, authenticated (AES-CTR), and field-ready.
    - **The Conclusion:** This is the direct result of applying a disciplined AI/ML approach to the deepest layers of RF engineering.

---

## Phase 5: The Path Forward

## Slide 14: The Path to "S" (Secret)
- **Key Message:** Bringing AI into the secured space.
- **Visual Idea:** A secure vault door with a server rack inside.
- **Talking Points:**
    - **Capability Gaps:** Current manual workflows fail in classified environments due to lack of tools.
    - **Roadmap:** Deploying localized AI nodes (Ollama/Custom builds) in air-gapped spaces.
    - **Data Sovereignty:** Keeping our most sensitive data off the wire.

## Slide 15: Conclusion / Q&A
- **Key Message:** Start small, think disciplined, scale fast.
- **Talking Points:**
    - AI is ready for the Wing today.
    - Questions?
