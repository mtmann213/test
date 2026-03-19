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

## Slide 10: The Challenge: Custom DF-OFDM
- **Key Message:** Complex signals require complex solutions.
- **Visual Idea:** A messy spectrogram of a frequency-hopping signal.
- **Talking Points:**
    - Problem: Manual classification of DF-OFDM is slow and prone to phase errors.
    - Requirements: 120-byte stability frames, 500ms hopping.
    - The "Needle in the Haystack" problem in RF.

## Slide 11: The AI Solution: Neural Receivers
- **Key Message:** Replacing manual logic with learned patterns.
- **Visual Idea:** A flowgraph showing Signal -> Neural Receiver (TensorFlow/Sionna) -> Classified Data.
- **Talking Points:**
    - Using Gemini to build the C++ correlators for phase-inversion resilience.
    - Software-Defined Timing Scanner: Automatically aligning FFT windows.
    - AI isn't *guessing*; it's performing high-speed pattern matching.

## Slide 12: Impact & Results
- **Key Message:** Mission success at speed.
- **Visual Idea:** A chart showing "Time to Classification" dropping from weeks to days.
- **Talking Points:**
    - Real-world results: Level 7 OFDM Master achieved.
    - Reproducible, automated workflows that can be shared across the Wing.

---

## Phase 5: The Path Forward

## Slide 13: The Path to "S" (Secret)
- **Key Message:** Bringing AI into the secured space.
- **Visual Idea:** A secure vault door with a server rack inside.
- **Talking Points:**
    - **Capability Gaps:** Current manual workflows fail in classified environments due to lack of tools.
    - **Roadmap:** Deploying localized AI nodes (Ollama/Custom builds) in air-gapped spaces.
    - **Data Sovereignty:** Keeping our most sensitive data off the wire.

## Slide 14: Conclusion / Q&A
- **Key Message:** Start small, think disciplined, scale fast.
- **Talking Points:**
    - AI is ready for the Wing today.
    - Questions?
