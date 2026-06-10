# Transformer Internals — Interactive Course

A self-contained, offline-first interactive course teaching how LLMs actually work — from tokenization through next-token prediction.

## Quick Start

Open `index.html` in any modern browser. No build step, no server needed.

```bash
# Or serve locally:
cd hermes/transformer-course
python3 -m http.server 8080
# Visit http://localhost:8080
```

## What's Inside

9 modules covering the complete transformer pipeline:

| # | Module | Interactive Demo |
|---|--------|-----------------|
| 1 | **Tokenization** | Type text → watch subword splitting in real-time |
| 2 | **Embeddings** | Click-to-explore semantic space + vector arithmetic visualization |
| 3 | **Positional Encoding** | Animated sine/cosine waves + scramble test |
| 4 | **Attention** | Attention heatmap + step-by-step Q·K score computation |
| 5 | **Multi-Head Attention** | Parallel head visualizations showing different relationship types |
| 6 | **Feed-Forward Network** | Signal flow diagram: expand → activate → compress |
| 7 | **Residual Stream** | Information highway with skip connections |
| 8 | **Next-Token Prediction** | Temperature slider + live probability distribution + sampling |
| 9 | **Architecture vs Weights** | GPT-4 / LLaMA 3 / Mistral comparison table |

Each module includes:
- Concept explanation (based on Kato's "How LLMs Actually Work")
- Interactive canvas demo
- Quiz with instant feedback and explanations
- Progress tracking via localStorage

## Tech Stack

- **Vanilla HTML/CSS/JS** — zero dependencies, no build step
- **Canvas API** for all visualizations
- **localStorage** for progress persistence
- Dark theme matching Hermes aesthetic

## File Structure

```
transformer-course/
├── index.html      # Main app (CSS + module markup)
├── js/app.js       # All interactive logic + canvas demos
└── README.md       # This file
```

## Browser Support

Chrome, Firefox, Safari, Edge — any browser with Canvas 2D support.
