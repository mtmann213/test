// ============================================================
// Transformer Internals — Interactive Course Engine
// ============================================================

const TOKEN_COLORS = [
  '#7c6aef','#34d399','#fbbf24','#f87171','#22d3ee',
  '#f472b6','#a78bfa','#6ee7b7','#fcd34d','#fca5a5',
  '#67e8f9','#c084fc','#86efac','#fde68a','#fecaca'
];

// ---- Mini BPE-style tokenizer (simplified) ----
const COMMON_WORDS = new Set([
  'the','a','an','is','are','was','were','be','been','being',
  'have','has','had','do','does','did','will','would','could',
  'should','may','might','shall','can','need','dare','ought',
  'used','to','of','in','for','on','with','at','by','from',
  'as','into','through','during','before','after','above',
  'below','between','out','off','over','under','again','further',
  'then','once','here','there','when','where','why','how',
  'all','both','each','few','more','most','other','some','such',
  'no','nor','not','only','own','same','so','than','too','very',
  'just','because','but','and','or','if','while','that','this',
  'these','those','i','me','my','we','our','you','your',
  'he','him','his','she','her','it','its','they','them','their',
  'what','which','who','whom','am','up','about','cat','dog',
  'sat','on','mat','ran','away','barked','at','the','strawberry',
  'running','token','ization','model','learn','text','data'
]);

function tokenize(text) {
  const tokens = [];
  // Simple word-level split with subword heuristics
  const words = text.toLowerCase().split(/\s+/);
  for (const word of words) {
    if (!word) continue;
    const clean = word.replace(/[^a-z]/g, '');
    if (COMMON_WORDS.has(clean)) {
      tokens.push({ text: clean, id: Math.abs(hashStr(clean)) % 10000 });
    } else if (clean.length > 4) {
      // Split into subword pieces
      const prefix = clean.slice(0, Math.ceil(clean.length * 0.6));
      const suffix = clean.slice(Math.ceil(clean.length * 0.6));
      tokens.push({ text: prefix, id: Math.abs(hashStr(prefix)) % 10000 });
      if (suffix) tokens.push({ text: '##' + suffix, id: Math.abs(hashStr(suffix)) % 10000 });
    } else {
      tokens.push({ text: clean || word, id: Math.abs(hashStr(word)) % 10000 });
    }
  }
  return tokens;
}

function hashStr(s) {
  let h = 0;
  for (let i = 0; i < s.length; i++) {
    h = ((h << 5) - h + s.charCodeAt(i)) | 0;
  }
  return h;
}

// ---- Navigation ----
let currentModule = 0;
const completedModules = new Set(JSON.parse(localStorage.getItem('tc_completed') || '[]'));

function initNav() {
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
      const mod = parseInt(item.dataset.module);
      switchModule(mod);
    });
    if (completedModules.has(parseInt(item.dataset.module))) {
      item.classList.add('completed');
    }
  });
  updateProgress();

  // Mobile menu toggle
  document.getElementById('menu-toggle').addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('open');
  });
}

function switchModule(idx) {
  currentModule = idx;
  document.querySelectorAll('.module').forEach(m => m.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById(`mod-${idx}`).classList.add('active');
  document.querySelector(`.nav-item[data-module="${idx}"]`).classList.add('active');

  // Close mobile menu
  document.getElementById('sidebar').classList.remove('open');

  // Initialize module-specific demos
  initModuleDemo(idx);
}

function markComplete(idx) {
  completedModules.add(idx);
  localStorage.setItem('tc_completed', JSON.stringify([...completedModules]));
  document.querySelector(`.nav-item[data-module="${idx}"]`).classList.add('completed');
  updateProgress();

  // Auto-advance if not last module
  if (idx < 8) {
    switchModule(idx + 1);
  }
}

function updateProgress() {
  const pct = (completedModules.size / 9) * 100;
  document.getElementById('progress-bar-fill').style.width = pct + '%';
}

// ---- Quiz System ----
const quizExplanations = [
  "Correct! LLMs see token IDs, not individual letters. 'Strawberry' might tokenize as ['straw', 'berry'] — the model never sees three separate R's.",
  "Right! Embeddings aren't designed by hand — they emerge during training because placing similar concepts near each other helps the model predict text better.",
  "Exactly! Without positional encodings, attention is permutation-invariant. The model would see both sentences as identical bags of tokens.",
  "Correct! Attention scores determine how much information one token should pull from another to build its next representation — it's about functional relevance, not surface similarity.",
  "Right! Multiple heads let the model learn different relationship types in parallel — syntax, semantics, coreference — giving richer representations than any single head could achieve alone.",
  "Correct! The FFN contains roughly 75% of transformer parameters. While attention mixes information between tokens, the FFN is where pattern recognition and knowledge storage happens.",
  "Exactly! Without residual connections, each layer would need to learn identity transformations just to pass signals through. With 30+ layers, gradients vanish or explode without them.",
  "Right! Higher temperature flattens the softmax distribution, making lower-probability tokens more likely. This increases randomness and creativity in outputs.",
  "Correct! The architecture is just the skeleton — all learned knowledge lives in the weights, which are shaped entirely by training data. Same chassis, different engines."
];

function checkQuiz(btn) {
  const quizArea = btn.closest('.quiz-area');
  const options = quizArea.querySelectorAll('.quiz-option');
  const fb = quizArea.querySelector('.quiz-feedback');
  const isCorrect = btn.dataset.correct === 'true';

  // Disable all options
  options.forEach(o => { o.style.pointerEvents = 'none'; });

  if (isCorrect) {
    btn.classList.add('correct');
    fb.className = 'quiz-feedback show correct-fb';
  } else {
    btn.classList.add('wrong');
    // Highlight the correct one
    options.forEach(o => {
      if (o.dataset.correct === 'true') o.classList.add('correct');
    });
    fb.className = 'quiz-feedback show wrong-fb';
  }

  const modIdx = parseInt(btn.closest('.module').id.split('-')[1]);
  fb.textContent = quizExplanations[modIdx];
}


// ============================================================
// MODULE DEMOS
// ============================================================

function initModuleDemo(idx) {
  // Delay to ensure module is visible in DOM before drawing canvases
  requestAnimationFrame(() => {
    switch (idx) {
      case 0: initTokenization(); break;
      case 1: initEmbeddings(); break;
      case 2: initPositional(); break;
      case 3: initAttention(); break;
      case 4: initMultiHead(); break;
      case 5: initFFN(); break;
      case 6: initResidual(); break;
      case 7: initDistribution(); updateDistribution(); break;
      case 8: break; // Table only, no canvas
    }
  });
}

// ---- Module 0: Tokenization ----
function initTokenization() {
  const input = document.getElementById('token-input');
  const output = document.getElementById('token-output');
  const strawDemo = document.getElementById('strawberry-demo');

  function renderTokens(tokens, container) {
    container.innerHTML = '';
    tokens.forEach((t, i) => {
      const chip = document.createElement('span');
      chip.className = 'token-chip';
      chip.style.background = TOKEN_COLORS[i % TOKEN_COLORS.length] + '22';
      chip.style.color = TOKEN_COLORS[i % TOKEN_COLORS.length];
      chip.style.border = `1px solid ${TOKEN_COLORS[i % TOKEN_COLORS.length]}44`;
      chip.textContent = t.text;
      chip.title = `Token ID: ${t.id}`;
      container.appendChild(chip);
    });
  }

  function update() {
    const tokens = tokenize(input.value);
    renderTokens(tokens, output);
  }

  input.removeEventListener('input', update);
  input.addEventListener('input', update);
  update();

  // Strawberry demo
  const strawTokens = tokenize('strawberry');
  renderTokens(strawTokens, strawDemo);
}

// ---- Module 1: Embeddings ----
const embeddingWords = [
  { word: 'king', x: 0.6, y: 0.3 },
  { word: 'queen', x: 0.55, y: 0.25 },
  { word: 'prince', x: 0.7, y: 0.35 },
  { word: 'man', x: 0.65, y: 0.6 },
  { word: 'woman', x: 0.5, y: 0.55 },
  { word: 'boy', x: 0.7, y: 0.65 },
  { word: 'girl', x: 0.55, y: 0.6 },
  { word: 'Paris', x: 0.2, y: 0.2 },
  { word: 'France', x: 0.18, y: 0.25 },
  { word: 'London', x: 0.3, y: 0.15 },
  { word: 'England', x: 0.28, y: 0.2 },
  { word: 'Berlin', x: 0.25, y: 0.3 },
  { word: 'Germany', x: 0.22, y: 0.35 },
  { word: 'dog', x: 0.75, y: 0.15 },
  { word: 'cat', x: 0.8, y: 0.2 },
  { word: 'puppy', x: 0.72, y: 0.12 },
  { word: 'kitten', x: 0.78, y: 0.18 },
  { word: 'happy', x: 0.4, y: 0.7 },
  { word: 'joyful', x: 0.38, y: 0.68 },
  { word: 'sad', x: 0.45, y: 0.8 },
  { word: 'run', x: 0.15, y: 0.7 },
  { word: 'sprint', x: 0.12, y: 0.68 },
  { word: 'walk', x: 0.18, y: 0.73 },
];

function initEmbeddings() {
  const canvas = document.getElementById('embedding-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  let selectedWord = null;

  function draw() {
    ctx.clearRect(0, 0, W, H);

    // Grid
    ctx.strokeStyle = '#1a1a26';
    for (let i = 0; i < W; i += 40) { ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, H); ctx.stroke(); }
    for (let i = 0; i < H; i += 40) { ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(W, i); ctx.stroke(); }

    // Draw connections from selected word to nearest neighbors
    if (selectedWord) {
      const sorted = [...embeddingWords].filter(w => w.word !== selectedWord.word)
        .map(w => ({ ...w, dist: Math.hypot(w.x - selectedWord.x, w.y - selectedWord.y) }))
        .sort((a, b) => a.dist - b.dist).slice(0, 5);

      sorted.forEach(n => {
        ctx.beginPath();
        ctx.moveTo(selectedWord.x * W, selectedWord.y * H);
        ctx.lineTo(n.x * W, n.y * H);
        ctx.strokeStyle = 'rgba(124, 106, 239, 0.3)';
        ctx.lineWidth = 1;
        ctx.stroke();
      });
    }

    // Draw points
    embeddingWords.forEach(w => {
      const isSelected = selectedWord && selectedWord.word === w.word;
      const r = isSelected ? 24 : 18;

      ctx.beginPath();
      ctx.arc(w.x * W, w.y * H, r, 0, Math.PI * 2);
      ctx.fillStyle = isSelected ? 'rgba(124, 106, 239, 0.3)' : 'rgba(52, 211, 153, 0.15)';
      ctx.fill();
      ctx.strokeStyle = isSelected ? '#7c6aef' : '#34d39944';
      ctx.lineWidth = isSelected ? 2 : 1;
      ctx.stroke();

      ctx.fillStyle = isSelected ? '#fff' : '#e4e4ef';
      ctx.font = `${isSelected ? 'bold ' : ''}11px Inter, sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(w.word, w.x * W, w.y * H);
    });

    // Labels
    ctx.fillStyle = '#8888a0';
    ctx.font = '12px Inter, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('Semantic similarity space (2D projection)', 16, 24);
    if (selectedWord) {
      ctx.fillStyle = '#7c6aef';
      ctx.fillText(`Selected: "${selectedWord.word}" — nearest neighbors highlighted`, 16, H - 16);
    } else {
      ctx.fillText('Click any word to see its nearest neighbors', 16, H - 16);
    }
  }

  canvas.onclick = (e) => {
    const rect = canvas.getBoundingClientRect();
    const scaleX = W / rect.width;
    const scaleY = H / rect.height;
    const mx = (e.clientX - rect.left) * scaleX;
    const my = (e.clientY - rect.top) * scaleY;

    let closest = null, minDist = Infinity;
    embeddingWords.forEach(w => {
      const d = Math.hypot(w.x * W - mx, w.y * H - my);
      if (d < 30 && d < minDist) { closest = w; minDist = d; }
    });

    selectedWord = closest;
    draw();
  };

  draw();

  // Vector arithmetic canvas
  const arithCanvas = document.getElementById('arithmetic-canvas');
  if (arithCanvas) {
    const ac = arithCanvas.getContext('2d');
    const aW = arithCanvas.width, aH = arithCanvas.height;

    // Toy 2D vectors for king-man+woman=queen demo
    const cx = aW / 2, cy = aH / 2;
    const vecs = {
      king:   { x: 80, y: -60 },
      man:    { x: 50, y: -30 },
      woman:  { x: -40, y: -20 },
      queen:  { x: 30, y: -70 }
    };

    // king - man + woman = (80-50-40, -60+30-20) = (-10, -50) ≈ queen(30,-70)
    const result = { x: vecs.king.x - vecs.man.x + vecs.woman.x, y: vecs.king.y - vecs.man.y + vecs.woman.y };

    function drawArrow(fromX, fromY, toX, toY, color, label) {
      const dx = toX - fromX, dy = toY - fromY;
      const angle = Math.atan2(dy, dx);
      const headLen = 10;

      ac.beginPath();
      ac.moveTo(fromX, cy + fromY);
      ac.lineTo(toX, cy + toY);
      ac.strokeStyle = color;
      ac.lineWidth = 2;
      ac.stroke();

      // Arrowhead
      ac.beginPath();
      ac.moveTo(toX, cy + toY);
      ac.lineTo(toX - headLen * Math.cos(angle - 0.4), cy + toY - headLen * Math.sin(angle - 0.4));
      ac.lineTo(toX - headLen * Math.cos(angle + 0.4), cy + toY - headLen * Math.sin(angle + 0.4));
      ac.closePath();
      ac.fillStyle = color;
      ac.fill();

      // Label
      const mx2 = (fromX + toX) / 2, my2 = (fromY + toY) / 2;
      ac.fillStyle = '#e4e4ef';
      ac.font = 'bold 13px Inter, sans-serif';
      ac.textAlign = 'center';
      ac.fillText(label, mx2, cy + my2 - 10);
    }

    // Origin line
    ac.strokeStyle = '#2a2a3a';
    ac.beginPath(); ac.moveTo(0, cy); ac.lineTo(aW, cy); ac.stroke();
    ac.beginPath(); ac.moveTo(cx, 0); ac.lineTo(cx, aH); ac.stroke();

    drawArrow(0, 0, vecs.king.x, vecs.king.y, '#fbbf24', 'king');
    drawArrow(0, 0, vecs.man.x, vecs.man.y, '#f87171', 'man');
    drawArrow(0, 0, vecs.woman.x, vecs.woman.y, '#f472b6', 'woman');

    // Result: king - man + woman (draw from queen position)
    drawArrow(vecs.queen.x, vecs.queen.y, result.x, result.y, '#34d399', `≈ queen`);

    // Queen actual
    ac.beginPath();
    ac.arc(vecs.queen.x, cy + vecs.queen.y, 6, 0, Math.PI * 2);
    ac.fillStyle = '#7c6aef';
    ac.fill();
    ac.fillStyle = '#7c6aef';
    ac.font = 'bold 14px Inter, sans-serif';
    ac.fillText('queen', vecs.queen.x + 20, cy + vecs.queen.y);

    // Result point
    ac.beginPath();
    ac.arc(result.x, cy + result.y, 6, 0, Math.PI * 2);
    ac.fillStyle = '#34d399';
    ac.fill();
    ac.fillStyle = '#34d399';
    ac.font = '12px Inter, sans-serif';
    ac.fillText(`result (${result.x}, ${result.y})`, result.x + 30, cy + result.y);

    // Equation
    ac.fillStyle = '#e4e4ef';
    ac.font = 'bold 16px JetBrains Mono, monospace';
    ac.textAlign = 'center';
    ac.fillText('king − man + woman ≈ queen', aW / 2, 30);

    // Labels
    ac.fillStyle = '#8888a0';
    ac.font = '12px Inter, sans-serif';
    ac.textAlign = 'left';
    ac.fillText('Vector arithmetic in embedding space (toy 2D)', 16, aH - 16);
  }
}

// ---- Module 2: Positional Encoding ----
function initPositional() {
  const canvas = document.getElementById('positional-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;

  function positionalEncoding(pos, dim) {
    const pe = [];
    for (let d = 0; d < dim; d++) {
      const angle = pos / Math.pow(10000, 2 * Math.floor(d / 2) / dim);
      pe.push(d % 2 === 0 ? Math.sin(angle) : Math.cos(angle));
    }
    return pe;
  }

  const numPositions = 20;
  const dimsToShow = 16;
  const padLeft = 40, padRight = 20, padTop = 30, padBottom = 30;
  const graphW = W - padLeft - padRight;
  const graphH = H - padTop - padBottom;

  ctx.clearRect(0, 0, W, H);

  // Title
  ctx.fillStyle = '#e4e4ef';
  ctx.font = 'bold 14px Inter, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('Sine/Cosine Positional Encodings', padLeft, 20);

  for (let d = 0; d < dimsToShow; d++) {
    const colorIdx = Math.floor(d / 4) % TOKEN_COLORS.length;
    const color = TOKEN_COLORS[colorIdx];

    ctx.beginPath();
    for (let p = 0; p <= numPositions * 10; p++) {
      const pos = p / 10;
      const pe = positionalEncoding(pos, dimsToShow);
      const x = padLeft + (pos / numPositions) * graphW;
      const y = padTop + (graphH / 2) - pe[d] * (graphH / 2.5);

      if (p === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.strokeStyle = color + '88';
    ctx.lineWidth = 1.5;
    ctx.stroke();
  }

  // Position markers
  for (let p = 0; p <= numPositions; p++) {
    const x = padLeft + (p / numPositions) * graphW;
    ctx.fillStyle = '#8888a0';
    ctx.font = '10px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(p.toString(), x, H - 8);
  }

  // Scramble demo
  const posDemo = document.getElementById('positional-demo');
  if (posDemo) renderPositionalTokens(posDemo, false);
}

function renderPositionalTokens(container, scrambled) {
  const words = ['The', 'cat', 'sat', 'on', 'the', 'mat'];
  const positions = scrambled ? [3, 1, 4, 0, 5, 2] : [0, 1, 2, 3, 4, 5];

  container.innerHTML = '';
  words.forEach((w, i) => {
    const chip = document.createElement('span');
    chip.className = 'token-chip';
    const pos = positions[i];
    chip.style.background = TOKEN_COLORS[pos % TOKEN_COLORS.length] + '22';
    chip.style.color = TOKEN_COLORS[pos % TOKEN_COLORS.length];
    chip.style.border = `1px solid ${TOKEN_COLORS[pos % TOKEN_COLORS.length]}44`;
    chip.textContent = `${w} [pos:${pos}]`;
    container.appendChild(chip);
  });

  const note = document.createElement('span');
  note.style.cssText = 'font-size:12px;color:var(--text-dim);margin-left:8px;';
  note.textContent = scrambled ? '(scrambled — positional encodings still mark original positions)' : '(original order)';
  container.appendChild(note);
}

function scrambleDemo() { renderPositionalTokens(document.getElementById('positional-demo'), true); }
function unscrambleDemo() { renderPositionalTokens(document.getElementById('positional-demo'), false); }

// ---- Module 3: Attention ----
function initAttention() {
  const canvas = document.getElementById('attention-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;

  const words = ['The', 'cat', 'sat', 'on', 'the', 'mat'];
  // Simulated attention pattern (row attends to columns)
  const attn = [
    [0.35, 0.20, 0.10, 0.10, 0.20, 0.05],  // The -> ...
    [0.05, 0.40, 0.25, 0.05, 0.05, 0.20],  // cat -> sat, mat
    [0.10, 0.30, 0.35, 0.10, 0.05, 0.10],  // sat -> cat
    [0.15, 0.10, 0.20, 0.35, 0.15, 0.05],  // on -> ...
    [0.35, 0.20, 0.10, 0.10, 0.20, 0.05],  // the -> ...
    [0.05, 0.25, 0.15, 0.05, 0.05, 0.45],  // mat -> cat, self
  ];

  const cellSize = Math.min(70, (W - 160) / words.length);
  const gridX = (W - cellSize * words.length) / 2;
  const gridY = 80;

  ctx.clearRect(0, 0, W, H);

  // Title
  ctx.fillStyle = '#e4e4ef';
  ctx.font = 'bold 14px Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('Attention Pattern: "The cat sat on the mat"', W / 2, 30);

  // Column labels (keys)
  ctx.font = '12px Inter, sans-serif';
  ctx.fillStyle = '#8888a0';
  words.forEach((w, i) => {
    ctx.textAlign = 'center';
    ctx.fillText(w, gridX + cellSize * i + cellSize / 2, gridY - 10);
  });

  // Row labels (queries)
  words.forEach((w, i) => {
    ctx.textAlign = 'right';
    ctx.fillStyle = '#8888a0';
    ctx.fillText(w, gridX - 10, gridY + cellSize * i + cellSize / 2 + 4);
  });

  // Heatmap cells
  for (let r = 0; r < words.length; r++) {
    for (let c = 0; c < words.length; c++) {
      const val = attn[r][c];
      const x = gridX + cellSize * c;
      const y = gridY + cellSize * r;

      // Color: low=dark, high=purple accent
      const intensity = Math.floor(val * 255);
      ctx.fillStyle = `rgba(124, 106, 239, ${val})`;
      ctx.beginPath();
      ctx.roundRect(x + 2, y + 2, cellSize - 4, cellSize - 4, 6);
      ctx.fill();

      // Value text
      if (cellSize > 50) {
        ctx.fillStyle = val > 0.3 ? '#fff' : '#8888a0';
        ctx.font = '11px JetBrains Mono, monospace';
        ctx.textAlign = 'center';
        ctx.fillText(val.toFixed(2), x + cellSize / 2, y + cellSize / 2 + 4);
      }
    }
  }

  // Legend
  const legendY = gridY + cellSize * words.length + 30;
  ctx.fillStyle = '#8888a0';
  ctx.font = '11px Inter, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('Each row sums to 1.0 (softmax). Darker = more attention.', gridX, legendY);

  // Step-by-step canvas
  const stepCanvas = document.getElementById('attn-step-canvas');
  if (stepCanvas) {
    drawAttentionStep(stepCanvas);
  }
}

function drawAttentionStep(canvas) {
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;

  // Toy Q/K vectors for demo
  const toyQ = [0.8, -0.3, 0.5, 0.1];
  const toyK = [0.6, -0.2, 0.4, 0.3];
  const dim = toyQ.length;

  ctx.clearRect(0, 0, W, H);

  // Title
  ctx.fillStyle = '#e4e4ef';
  ctx.font = 'bold 13px Inter, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('Dot product: Q · K', 20, 25);

  const startX = 60, startY = 50;
  let y = startY;

  // Draw vectors side by side
  for (let i = 0; i < dim; i++) {
    const colorQ = '#fbbf24';
    const colorK = '#f87171';

    ctx.fillStyle = colorQ;
    ctx.font = 'bold 14px JetBrains Mono, monospace';
    ctx.textAlign = 'right';
    ctx.fillText(toyQ[i].toFixed(1), startX - 10, y + 14);

    ctx.fillStyle = '#8888a0';
    ctx.textAlign = 'center';
    ctx.fillText('×', startX + 30, y + 14);

    ctx.fillStyle = colorK;
    ctx.textAlign = 'left';
    ctx.fillText(toyK[i].toFixed(1), startX + 50, y + 14);

    const product = toyQ[i] * toyK[i];
    ctx.fillStyle = '#34d399';
    ctx.textAlign = 'right';
    ctx.fillText(`= ${product.toFixed(2)}`, W / 2 - 20, y + 14);

    // Connecting line
    if (i < dim - 1) {
      ctx.strokeStyle = '#2a2a3a';
      ctx.beginPath();
      ctx.moveTo(startX - 20, y + 25);
      ctx.lineTo(W / 2 - 10, y + 25);
      ctx.stroke();
    }

    y += 40;
  }

  // Sum
  const sum = toyQ.reduce((a, b, i) => a + b * toyK[i], 0);
  ctx.strokeStyle = '#7c6aef';
  ctx.beginPath();
  ctx.moveTo(startX - 20, y - 5);
  ctx.lineTo(W / 2 - 10, y - 5);
  ctx.stroke();

  ctx.fillStyle = '#7c6aef';
  ctx.font = 'bold 16px JetBrains Mono, monospace';
  ctx.textAlign = 'right';
  ctx.fillText(`Σ = ${sum.toFixed(2)}`, W / 2 - 10, y + 15);

  // Scale factor
  const scaled = sum / Math.sqrt(dim);
  ctx.fillStyle = '#e4e4ef';
  ctx.font = '13px Inter, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText(`Scaled: ${sum.toFixed(2)} / √${dim} = ${scaled.toFixed(2)}`, W / 2 + 20, y + 15);

  // Explanation
  ctx.fillStyle = '#8888a0';
  ctx.font = '12px Inter, sans-serif';
  ctx.fillText('Higher dot product → higher attention score after softmax', 20, H - 20);
}

function computeAttention() {
  const stepCanvas = document.getElementById('attn-step-canvas');
  if (stepCanvas) drawAttentionStep(stepCanvas);
}

// ---- Module 4: Multi-Head Attention ----
function initMultiHead() {
  const canvas = document.getElementById('multihead-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;

  const words = ['The', 'dog', 'that', 'barked', 'at', 'the', 'cat', 'ran', 'away'];
  const heads = [
    { name: 'Head 1 — Syntax (subject-verb)', color: '#7c6aef', pattern: [[0,8],[1,7]] },
    { name: 'Head 2 — Coreference (pronoun→noun)', color: '#34d399', pattern: [[2,1],[4,5]] },
    { name: 'Head 3 — Local bigrams', color: '#fbbf24', pattern: [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],[7,8]] },
  ];

  ctx.clearRect(0, 0, W, H);

  // Title
  ctx.fillStyle = '#e4e4ef';
  ctx.font = 'bold 14px Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('Three Attention Heads on: "The dog that barked at the cat ran away"', W / 2, 25);

  const headH = (H - 60) / heads.length;

  heads.forEach((head, hi) => {
    const baseY = 45 + hi * headH;

    // Head label
    ctx.fillStyle = head.color;
    ctx.font = 'bold 12px Inter, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText(head.name, 20, baseY + 18);

    // Word positions
    const wordW = (W - 60) / words.length;
    words.forEach((w, wi) => {
      const x = 30 + wi * wordW;
      ctx.fillStyle = '#e4e4ef';
      ctx.font = '11px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(w, x + wordW / 2, baseY + headH - 8);
    });

    // Draw connections
    head.pattern.forEach(([from, to]) => {
      const x1 = 30 + from * wordW + wordW / 2;
      const x2 = 30 + to * wordW + wordW / 2;
      const midY = baseY + 25;

      ctx.beginPath();
      ctx.moveTo(x1, baseY + headH - 20);
      ctx.quadraticCurveTo((x1 + x2) / 2, midY, x2, baseY + headH - 20);
      ctx.strokeStyle = head.color + '88';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Dots at endpoints
      ctx.beginPath();
      ctx.arc(x1, baseY + headH - 20, 3, 0, Math.PI * 2);
      ctx.fillStyle = head.color;
      ctx.fill();
      ctx.beginPath();
      ctx.arc(x2, baseY + headH - 20, 3, 0, Math.PI * 2);
      ctx.fill();
    });

    // Separator
    if (hi < heads.length - 1) {
      ctx.strokeStyle = '#2a2a3a';
      ctx.beginPath();
      ctx.moveTo(20, baseY + headH);
      ctx.lineTo(W - 20, baseY + headH);
      ctx.stroke();
    }
  });
}

// ---- Module 5: Feed-Forward Network ----
function initFFN() {
  const canvas = document.getElementById('ffn-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;

  ctx.clearRect(0, 0, W, H);

  // Title
  ctx.fillStyle = '#e4e4ef';
  ctx.font = 'bold 14px Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('Feed-Forward Network: Expand → Activate → Compress', W / 2, 30);

  const layers = [
    { name: 'Input\n(d=4096)', x: 80, nodes: 5, color: '#7c6aef' },
    { name: 'Expand\n(d=16384)', x: W / 2 - 60, nodes: 9, color: '#fbbf24' },
    { name: 'SwiGLU\nactivate', x: W / 2 + 60, nodes: 9, color: '#34d399' },
    { name: 'Output\n(d=4096)', x: W - 80, nodes: 5, color: '#7c6aef' },
  ];

  const centerY = H / 2;

  layers.forEach(layer => {
    // Draw nodes
    for (let i = 0; i < layer.nodes; i++) {
      const y = centerY - ((layer.nodes - 1) * 25) / 2 + i * 25;

      ctx.beginPath();
      ctx.arc(layer.x, y, 8, 0, Math.PI * 2);
      ctx.fillStyle = layer.color + '33';
      ctx.fill();
      ctx.strokeStyle = layer.color;
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }

    // Label
    const lines = layer.name.split('\n');
    ctx.fillStyle = '#8888a0';
    ctx.font = '11px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(lines[0], layer.x, centerY + (layer.nodes * 25) / 2 + 20);
    if (lines[1]) {
      ctx.fillStyle = '#666680';
      ctx.font = '10px JetBrains Mono, monospace';
      ctx.fillText(lines[1], layer.x, centerY + (layer.nodes * 25) / 2 + 34);
    }
  });

  // Draw connections between layers
  for (let l = 0; l < layers.length - 1; l++) {
    const from = layers[l];
    const to = layers[l + 1];

    for (let i = 0; i < from.nodes; i++) {
      for (let j = 0; j < to.nodes; j++) {
        const fy = centerY - ((from.nodes - 1) * 25) / 2 + i * 25;
        const ty = centerY - ((to.nodes - 1) * 25) / 2 + j * 25;

        ctx.beginPath();
        ctx.moveTo(from.x, fy);
        ctx.lineTo(to.x, ty);
        ctx.strokeStyle = 'rgba(124, 106, 239, 0.08)';
        ctx.lineWidth = 0.5;
        ctx.stroke();
      }
    }

    // Arrow label
    const midX = (from.x + to.x) / 2;
    ctx.fillStyle = '#555570';
    ctx.font = '10px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('W', midX, centerY - 30);
  }

  // Bottom note
  ctx.fillStyle = '#8888a0';
  ctx.font = '12px Inter, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('~75% of model parameters live in FFN layers. Each position is processed independently but with the same weights.', 30, H - 20);
}

// ---- Module 6: Residual Stream ----
function initResidual() {
  const canvas = document.getElementById('residual-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;

  ctx.clearRect(0, 0, W, H);

  // Title
  ctx.fillStyle = '#e4e4ef';
  ctx.font = 'bold 14px Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('The Residual Stream — Information Highway', W / 2, 30);

  const centerX = W / 2;
  const blockW = 180, blockH = 50;
  const startY = 60;

  // Draw residual stream (main vertical line)
  ctx.strokeStyle = '#7c6aef';
  ctx.lineWidth = 4;
  ctx.setLineDash([]);
  ctx.beginPath();
  ctx.moveTo(centerX, startY - 20);
  ctx.lineTo(centerX, H - 30);
  ctx.stroke();

  // Label the stream
  ctx.save();
  ctx.translate(centerX + 16, H / 2);
  ctx.rotate(Math.PI / 2);
  ctx.fillStyle = '#7c6aef';
  ctx.font = 'bold 12px Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('RESIDUAL STREAM', 0, 0);
  ctx.restore();

  // Transformer blocks
  const blocks = [
    { label: 'Transformer Block 1', y: startY },
    { label: 'Transformer Block N', y: H - 120 },
  ];

  blocks.forEach(block => {
    // Attention sub-block
    ctx.fillStyle = '#7c6aef22';
    ctx.strokeStyle = '#7c6aef44';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(centerX - blockW / 2, block.y, blockW, blockH, 8);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#e4e4ef';
    ctx.font = '12px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Self-Attention', centerX, block.y + 22);

    // Layer norm label
    ctx.fillStyle = '#8888a0';
    ctx.font = '10px Inter, sans-serif';
    ctx.fillText('LayerNorm → Attention → Add & Norm', centerX, block.y + 40);

    // FFN sub-block
    const ffnY = block.y + blockH + 20;
    ctx.fillStyle = '#34d39922';
    ctx.strokeStyle = '#34d39944';
    ctx.beginPath();
    ctx.roundRect(centerX - blockW / 2, ffnY, blockW, blockH, 8);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#e4e4ef';
    ctx.font = '12px Inter, sans-serif';
    ctx.fillText('Feed-Forward Network', centerX, ffnY + 22);
    ctx.fillStyle = '#8888a0';
    ctx.font = '10px Inter, sans-serif';
    ctx.fillText('LayerNorm → FFN → Add & Norm', centerX, ffnY + 40);

    // Skip connection arrows (curved lines going around blocks)
    const skipX = centerX + blockW / 2 + 30;
    ctx.strokeStyle = '#fbbf2466';
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);

    // Around attention
    ctx.beginPath();
    ctx.moveTo(centerX, block.y - 5);
    ctx.lineTo(skipX + 10, block.y - 5);
    ctx.lineTo(skipX + 10, block.y + blockH + 5);
    ctx.lineTo(centerX, block.y + blockH + 5);
    ctx.stroke();

    // Around FFN
    ctx.beginPath();
    ctx.moveTo(centerX, ffnY - 5);
    ctx.lineTo(skipX + 10, ffnY - 5);
    ctx.lineTo(skipX + 10, ffnY + blockH + 5);
    ctx.lineTo(centerX, ffnY + blockH + 5);
    ctx.stroke();

    // Plus signs at merge points
    ctx.setLineDash([]);
    ctx.fillStyle = '#fbbf24';
    ctx.font = 'bold 16px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('+', centerX + blockW / 2 + 5, block.y + blockH + 10);
    ctx.fillText('+', centerX + blockW / 2 + 5, ffnY + blockH + 10);

    // Block label
    ctx.fillStyle = '#8888a0';
    ctx.font = '11px Inter, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText(block.label, centerX - blockW / 2 - 100, block.y + 30);

    // Dashed skip label
    ctx.fillStyle = '#fbbf2488';
    ctx.font = '10px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('skip', skipX + 10, block.y + blockH / 2);
  });

  // Bottom note
  ctx.fillStyle = '#8888a0';
  ctx.font = '12px Inter, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('Each block adds its contribution to the stream — never replaces it. This is why deep networks train.', 30, H - 10);
}

// ---- Module 7: Next-Token Prediction ----
const vocabTokens = [
  { token: 'the', prob: 0.35 },
  { token: 'cat', prob: 0.20 },
  { token: 'sat', prob: 0.15 },
  { token: 'dog', prob: 0.10 },
  { token: 'ran', prob: 0.08 },
  { token: 'mat', prob: 0.06 },
  { token: 'quick', prob: 0.03 },
  { token: 'lazy', prob: 0.02 },
  { token: 'blue', prob: 0.005 },
  { token: 'zzz', prob: 0.001 },
];

function softmax(logits, temperature) {
  const scaled = logits.map(l => l / temperature);
  const max = Math.max(...scaled);
  const exps = scaled.map(s => Math.exp(s - max));
  const sum = exps.reduce((a, b) => a + b, 0);
  return exps.map(e => e / sum);
}

function initDistribution() {
  // Just set up the canvas reference; updateDistribution draws it
}

function updateDistribution() {
  const slider = document.getElementById('temp-slider');
  if (!slider) return;
  const temp = parseFloat(slider.value);
  document.getElementById('temp-val').textContent = temp.toFixed(1);

  const canvas = document.getElementById('dist-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;

  // Generate logits from base probabilities
  const logits = vocabTokens.map(t => Math.log(t.prob + 0.001));
  const probs = softmax(logits, temp);

  ctx.clearRect(0, 0, W, H);

  // Title
  ctx.fillStyle = '#e4e4ef';
  ctx.font = 'bold 14px Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText(`Probability Distribution (temperature = ${temp.toFixed(1)})`, W / 2, 30);

  const barAreaH = H - 80;
  const maxProb = Math.max(...probs);
  const barW = (W - 60) / probs.length;

  vocabTokens.forEach((t, i) => {
    const p = probs[i];
    const barH = (p / maxProb) * barAreaH;
    const x = 30 + i * barW;
    const y = H - 40 - barH;

    // Bar
    ctx.fillStyle = `rgba(124, 106, 239, ${0.3 + p})`;
    ctx.beginPath();
    ctx.roundRect(x + 4, y, barW - 8, barH, [4, 4, 0, 0]);
    ctx.fill();

    // Token label
    ctx.fillStyle = '#e4e4ef';
    ctx.font = '11px JetBrains Mono, monospace';
    ctx.textAlign = 'center';
    ctx.fillText(t.token, x + barW / 2, H - 20);

    // Probability on top
    ctx.fillStyle = '#8888a0';
    ctx.font = '10px Inter, sans-serif';
    ctx.fillText((p * 100).toFixed(1) + '%', x + barW / 2, y - 6);
  });

  // Store probs for sampling
  canvas._probs = probs;
}

function sampleToken() {
  const canvas = document.getElementById('dist-canvas');
  if (!canvas || !canvas._probs) return;

  const probs = canvas._probs;
  let r = Math.random();
  let selected = -1;
  for (let i = 0; i < probs.length; i++) {
    r -= probs[i];
    if (r <= 0) { selected = i; break; }
  }
  if (selected === -1) selected = probs.length - 1;

  document.getElementById('sample-result').textContent = `→ "${vocabTokens[selected].token}"`;

  // Highlight bar
  const ctx = canvas.getContext('2d');
  updateDistribution();
}


// ============================================================
// INIT
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  initNav();
  initModuleDemo(0);
});
