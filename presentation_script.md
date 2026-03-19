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

## Slide 10: The Evolution: Tactical SDR to Neural Receiver
- **Key Message:** Project Opal Vanguard is a high-resiliency tactical transceiver, not just a lab experiment.
- **Visual Idea:** A high-level block diagram showing the evolution from a simple GNU Radio flowgraph to a multi-waveform (GFSK, DQPSK, CCSK, CSS) system.
- **Talking Points:**
    - The challenge was moving from idealized simulations to a field-ready transceiver.
    - **Key Specs:** 120-byte tactical blocks with 15-row matrix interleaving for error resiliency.
    - **Security:** AES-CTR crypto-sync and NRZ-I phase resilience to survive signal fading.
    - **The Physics Bottleneck:** Dealing with the USRP "Tag Paradox" (timing/scaling errors) and the CFO-induced "Donut" constellations that confuse standard AI models.

## Slide 11: The AI Solution: Breaking the Bottleneck
- **Key Message:** Gemini wasn't just writing boilerplate; it was solving complex signal processing logic.
- **Visual Idea:** A "Before vs. After" comparison of constellation diagrams (Donuts vs. Blobs) and a code snippet showing a NumPy vectorized operation.
- **Talking Points:**
    - **Super-Vectorization:** Replacing thousands of nested Python loops with NumPy matrix-matrix multiplications (`np.dot`), reducing CPU overhead by 90%.
    - **FFT-Lock Frequency Estimation:** Using AI-assisted DSP code to lock onto a 50kHz pilot, transforming unreadable "donuts" into mod-distinguishable "blobs."
    - **Threaded Offload:** Decoupling the fast syncword search from heavy FEC/CCSK math to allow for real-time 2.0 Msps operation.

## Slide 12: Vanguard Data Factory (VDF) & Specter's Edge
- **Key Message:** Training on real-world "dirty" data is the only way to reach mission-ready status.
- **Visual Idea:** A photo or graphic of the "Hardware Trinity": 3x USRPs (TX, RX, and Adversary) working in sync.
- **Talking Points:**
    - **VDF:** An automated pipeline for industrial-scale data harvesting.
    - **Mission: Specter's Edge:** A "Mega-Harvest" of 250,000+ snapshots of real-world hardware data.
    - This diversity (sweeping gains, drift levels, and offsets) ensures the model doesn't just learn a lab environment—it learns the "Reality of the Wire."

## Slide 13: Impact & Results
- **Key Message:** We achieved Level 9 "Deep Shadow" and stabilized the entire tactical baseline.
- **Visual Idea:** A 100% pass mark for the 18-point regression suite.
- **Talking Points:**
    - **Level 9 Realized:** Chirp Spread Spectrum (CSS) is now operational and ultra-resilient.
    - **Efficiency:** The time to generate a full mission dataset and refine a model has dropped from months to hours.
    - **Status:** Level 7 OFDM Master and Level 9 CSS Master status officially achieved.

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
