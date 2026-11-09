const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const OUT = "D:/final_year_project/Adaptive_Food_Recognition_Deck.pptx";
const OUT_COPY = "D:/final_year_project/project_ppt_batch_11.pptx";
const BANNER = "D:/final_year_project/docs/report/assets/gvpce-header.jpg";
const WORKFLOW_IMG = "D:/final_year_project/docs/report/assets/system_workflow.png";

// Palette
const NAVY = "14284B";
const GOLD = "C9A227";
const BODY = "222222";
const MUTED = "666666";
const BORDER = "CBD5E1";
const ZEBRA = "F8FAFC";
const CARD_BG = "F8F9FA";
const CARD_BORDER = "CBD5E1";
const TEAL = "2A8C8C";
const GREEN = "2E8B57";
const DKGOLD = "B8901B";
const RED = "C0463F";
const PURPLE = "7B5EC2";
const BLUE = "3B6FC9";
const DEEP = "1F3C73";

const FONT = "Calibri";
const W = 13.333;
const H = 7.5;
const M = 0.6;
const CW = W - 2 * M;

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "The Invincibles";
pptx.company = "GVP College of Engineering (Autonomous)";
pptx.title = "Adaptive Food Recognition and Nutritional Estimation Using Multimodal AI";
pptx.subject = "B.Tech Final Year Project — Phase 1 & 2 Presentation";

function slideBase(title, num) {
  const s = pptx.addSlide();
  s.background = { color: "FFFFFF" };
  s.addText(title, {
    x: M, y: 0.42, w: CW, h: 0.66,
    fontFace: FONT, fontSize: 30, bold: true, color: NAVY, align: "center", valign: "middle", margin: 0,
  });
  s.addShape(pptx.ShapeType.rect, {
    x: (W - 1.2) / 2, y: 1.15, w: 1.2, h: 0.05,
    fill: { color: GOLD }, line: { color: GOLD, width: 0.75 },
  });
  s.addText(String(num), {
    x: 11.93, y: 6.98, w: 0.8, h: 0.3,
    fontFace: FONT, fontSize: 11, bold: true, color: NAVY, align: "right", margin: 0,
  });
  s.addText("Informational estimate only — not medical or dietary advice.", {
    x: M, y: 7.03, w: 8.0, h: 0.24,
    fontFace: FONT, fontSize: 8.5, color: "8A8A8A", align: "left", margin: 0,
  });
  return s;
}

function bullets(s, items, o) {
  o = o || {};
  const runs = [];
  items.forEach((it, i) => {
    const isLast = i === items.length - 1;
    if (typeof it === "string") {
      runs.push({
        text: it,
        options: Object.assign({ bullet: true, breakLine: !isLast, color: BODY }, o.run || {}),
      });
    } else {
      runs.push({
        text: it.lead,
        options: Object.assign({ bullet: true, breakLine: false, bold: true, color: NAVY }, o.lead || {}),
      });
      runs.push({
        text: it.text,
        options: Object.assign({ breakLine: !isLast, color: BODY }, o.run || {}),
      });
    }
  });
  s.addText(runs, Object.assign({
    x: M, y: 1.55, w: CW, h: 5.2,
    fontFace: FONT, fontSize: o.fontSize || 15, lineSpacing: o.lineSpacing || 24,
    valign: "top", margin: 0,
    paraSpaceAfter: o.paraSpaceAfter === undefined ? 10 : o.paraSpaceAfter,
  }, o.box || {}));
}

function cell(text, opts) {
  return {
    text,
    options: Object.assign({
      fontFace: FONT, fontSize: 11, color: BODY, valign: "middle",
      margin: 0.07, border: { type: "solid", pt: 0.75, color: BORDER },
    }, opts || {}),
  };
}

function table(s, rows, cols, o) {
  o = o || {};
  const head = cols.map(c => cell(c, {
    bold: true, color: "FFFFFF", fill: { color: NAVY },
    fontSize: o.headSize || 12, align: "center",
  }));
  const body = rows.map((r, ri) => r.map((c, ci) => {
    const isObj = c && typeof c === "object" && !Array.isArray(c);
    const txt = isObj ? c.t : c;
    const extra = isObj ? c.o : {};
    return cell(txt, Object.assign({
      fontSize: o.fontSize || 10.5,
      bold: ci === 0,
      color: ci === 0 ? NAVY : BODY,
      fill: { color: ri % 2 === 1 ? ZEBRA : "FFFFFF" },
      align: "left",
    }, extra));
  }));
  s.addTable([head].concat(body), {
    x: o.x === undefined ? M : o.x,
    y: o.y === undefined ? 1.55 : o.y,
    w: o.w === undefined ? CW : o.w,
    colW: o.colW,
    rowH: o.rowH,
    border: { type: "solid", pt: 0.75, color: BORDER },
    fontFace: FONT,
    autoPage: false,
    valign: "middle",
  });
}

// Clean neutral card (NO garish rainbow fills, NO top colored bar)
function cleanCard(s, x, y, w, h, title, body, o) {
  o = o || {};
  s.addShape(pptx.ShapeType.roundRect, {
    x: x, y: y, w: w, h: h, rectRadius: 0.04,
    fill: { color: o.fill || CARD_BG },
    line: { color: o.borderColor || CARD_BORDER, width: 1 },
  });
  s.addText(title, {
    x: x + 0.18, y: y + 0.12, w: w - 0.36, h: 0.34,
    fontFace: FONT, fontSize: o.titleSize || 13, bold: true, color: o.titleColor || NAVY,
    valign: "middle", margin: 0,
  });
  const items = Array.isArray(body) ? body : [body];
  s.addText(items.map((t, i) => ({
    text: t,
    options: { bullet: true, breakLine: i !== items.length - 1, fontSize: o.bodySize || 10.5, color: BODY },
  })), {
    x: x + 0.18, y: y + 0.50, w: w - 0.36, h: h - 0.58,
    fontFace: FONT, fontSize: o.bodySize || 10.5, valign: "top", margin: 0,
    lineSpacing: o.lineSpacing || 14,
    paraSpaceAfter: o.paraSpaceAfter === undefined ? 6 : o.paraSpaceAfter,
  });
}

function noteBox(s, x, y, w, h, lead, rest, color, fill, size) {
  s.addShape(pptx.ShapeType.roundRect, {
    x: x, y: y, w: w, h: h, rectRadius: 0.05,
    fill: { color: fill }, line: { color: color, width: 1 },
  });
  s.addText([
    { text: lead, options: { bold: true, color: color } },
    { text: rest, options: { color: BODY } },
  ], {
    x: x + 0.25, y: y, w: w - 0.5, h: h,
    fontFace: FONT, fontSize: size || 13, valign: "middle", align: "center", margin: 0,
  });
}

// =====================================================================
// 1 — TITLE
// =====================================================================
{
  const s = pptx.addSlide();
  s.background = { color: "FFFFFF" };
  if (fs.existsSync(BANNER)) {
    s.addImage({ path: BANNER, x: 0.6, y: 0.32, w: 12.13, h: 1.72 });
  }

  s.addText("Department of Computer Science and Engineering", {
    x: M, y: 2.42, w: CW, h: 0.45,
    fontFace: FONT, fontSize: 22, bold: true, color: NAVY, align: "center", margin: 0,
  });
  s.addShape(pptx.ShapeType.rect, {
    x: (W - 1.4) / 2, y: 2.98, w: 1.4, h: 0.05,
    fill: { color: GOLD }, line: { color: GOLD, width: 0.75 },
  });
  s.addText("Adaptive Food Recognition and Nutritional Estimation Using Multimodal AI", {
    x: 1.0, y: 3.16, w: 11.33, h: 1.35,
    fontFace: FONT, fontSize: 29, bold: true, color: NAVY, align: "center", valign: "middle", margin: 0,
  });
  s.addText("Component-level nutrition from a single meal photograph", {
    x: 1.0, y: 4.54, w: 11.33, h: 0.34,
    fontFace: FONT, fontSize: 14, italic: true, color: MUTED, align: "center", margin: 0,
  });

  s.addShape(pptx.ShapeType.line, {
    x: 6.66, y: 5.02, w: 0, h: 1.95, line: { color: BORDER, width: 1 },
  });

  s.addText("Under the guidance of", {
    x: 0.8, y: 5.02, w: 5.4, h: 0.3,
    fontFace: FONT, fontSize: 12, color: MUTED, align: "center", margin: 0,
  });
  s.addText("Dr. G. Vani", {
    x: 0.8, y: 5.34, w: 5.4, h: 0.4,
    fontFace: FONT, fontSize: 17, bold: true, color: NAVY, align: "center", margin: 0,
  });
  s.addText("Professor, Department of CSE", {
    x: 0.8, y: 5.76, w: 5.4, h: 0.3,
    fontFace: FONT, fontSize: 12, color: BODY, align: "center", margin: 0,
  });
  s.addText("Team: The Invincibles", {
    x: 0.8, y: 6.30, w: 5.4, h: 0.3,
    fontFace: FONT, fontSize: 12, bold: true, color: TEAL, align: "center", margin: 0,
  });

  const names = [
    ["Jami Sranay", "323103310095"],
    ["Harsha Vardhan Gandepalli", "323103310092"],
    ["Gottumukkala Sri Abhigna", "323103310081"],
    ["Jetti Lakshmi Prasanna", "323103310097"],
  ];
  s.addText("By", {
    x: 7.1, y: 5.02, w: 5.4, h: 0.3,
    fontFace: FONT, fontSize: 12, color: MUTED, align: "center", margin: 0,
  });
  names.forEach((n, i) => {
    s.addText([
      { text: n[0] + "  ", options: { bold: true, color: NAVY } },
      { text: "(" + n[1] + ")", options: { color: BODY } },
    ], {
      x: 6.95, y: 5.36 + i * 0.33, w: 5.7, h: 0.32,
      fontFace: FONT, fontSize: 13, align: "center", margin: 0,
    });
  });
  s.addNotes("Greet the panel. State project title, guide Dr. G. Vani, team members, and the core premise: decomposing mixed plates into components with database-grounded nutrition.");
}

// =====================================================================
// 2 — INDEX
// =====================================================================
{
  const s = slideBase("Index", 2);
  const items = [
    "Abstract", "Introduction", "Literature Survey", "Challenges in Domain Area",
    "Sub-Domain (Respective Challenge)", "Motivation of Work", "Objectives",
    "Problem Statement", "System Workflow", "Methodology", "Requirements",
    "Dataset", "Status of the Project", "Conclusion", "References",
  ];
  const rows = items.map((t, i) => [
    cell(String(i + 1), { align: "center", bold: true, color: NAVY }),
    cell(t, { color: BODY }),
  ]);
  table(s, rows, ["Serial No.", "Contents"], {
    x: 2.67, y: 1.55, w: 8.0, colW: [1.55, 6.45],
    rowH: 0.315, fontSize: 12, headSize: 12.5,
  });
  s.addNotes("Walk through the slide order mandated by the CSE department circular.");
}

// =====================================================================
// 3 — ABSTRACT
// =====================================================================
{
  const s = slideBase("Abstract", 3);
  bullets(s, [
    { lead: "Contemporary Challenge: ", text: "Meal-photo apps return one single calorie number for a whole plate; a mixed Indian meal (rice, dal, chapati, sabzi) makes that single number wrong by construction." },
    { lead: "Proposed System: ", text: "From a single meal photograph, decompose the plate into individual components, estimate mass geometrically in grams, and retrieve verified nutrients from IFCT 2017 / USDA." },
    { lead: "Strict Grounding Rule: ", text: "The vision-language model is restricted to perception only (names, regions, physical states); it NEVER produces calories, grams, or macro numbers (BR-01)." },
    { lead: "Calibrated Uncertainty: ", text: "A fused 7-signal reliability score calibrated via isotonic regression; low-confidence components trigger active, targeted user clarification instead of silent guessing." },
    { lead: "Indian-First Coverage: ", text: "Dual-index RAG over IFCT 2017 with physical-state filtering — cooked rice matches 130 kcal/100 g, avoiding the 345 kcal/100 g raw rice error." },
    { lead: "Evaluation Targets: ", text: "Benchmarked on gold_v1 (150 images of 60 weighed Indian meals); targets component F1 ≥ 0.80, kcal MAPE ≤ 18 %, ECE ≤ 0.10, latency ≤ 20 s." },
  ], { fontSize: 14.5, lineSpacing: 22, paraSpaceAfter: 12, box: { y: 1.5, h: 4.4 } });

  noteBox(s, M, 6.16, CW, 0.62,
    "Core contribution: ", "Decomposing calorie error into identity × mass × grounding × calibration — then solving each stage with measurable, verifiable components.", TEAL, "DDF1EF");
  s.addNotes("Abstract overview: problem of mixed plates, component-level decomposition, grounding rule, calibration, and Indian food coverage.");
}

// =====================================================================
// 4 — INTRODUCTION (Clean neutral cards, NO top bar, NO rainbow colors)
// =====================================================================
{
  const s = slideBase("Introduction", 4);
  s.addText([
    { text: "About the project:  ", options: { bold: true, color: NAVY } },
    { text: "A mixed meal is not a single dish. The system analyses one meal photo, segments the plate into discrete components, estimates each portion's mass, and grounds nutritional values in verified national food composition tables.", options: { color: BODY } },
  ], {
    x: M, y: 1.40, w: CW, h: 0.90,
    fontFace: FONT, fontSize: 13.5, valign: "top", lineSpacing: 19, margin: 0,
  });

  const cards = [
    { t: "Dietary Self-Tracking", b: ["Photo logging is fast, but entries collapse into a single guessed dish serving.", "Users abandon tracking when numbers feel inconsistent and unreliable."] },
    { t: "The Mixed-Plate Problem", b: ["An Indian thali holds 3–8 distinct foods with radically different densities.", "One dish label cannot describe it; individual items remain unnamed."] },
    { t: "Portion Blindness", b: ["A guessed serving yields ±50 % mass error, causing ±50 % calorie error.", "2D photographs lack depth, requiring scale-anchored geometric inference."] },
    { t: "Ungrounded Model Hallucinations", b: ["An LLM predicting calories from memory cannot be audited or verified.", "Estimates drift unpredictably across runs and model checkpoints."] },
    { t: "Silent Overconfident Failure", b: ["Wrong and confident predictions are worse than acknowledging uncertainty.", "Existing apps rarely inform users which food component they are unsure about."] },
    { t: "Indian Nutritional Coverage", b: ["ICMR-NIN IFCT 2017 is essential for Indian diets; global apps ignore it.", "Regional culinary names (koora, pappu, annam) break English-only classifiers."] },
  ];
  const cw = 3.84, gap = 0.3, ch = 2.05;
  cards.forEach((c, i) => {
    const col = i % 3, row = Math.floor(i / 3);
    cleanCard(s, M + col * (cw + gap), 2.38 + row * (ch + 0.22), cw, ch, c.t, c.b, {
      titleSize: 13.5, bodySize: 10.5, lineSpacing: 15, paraSpaceAfter: 6,
      fill: CARD_BG, borderColor: CARD_BORDER, titleColor: NAVY,
    });
  });
  s.addNotes("Explain the 6 core failure modes of current dietary apps: dietary self-tracking churn, mixed-plate complexity, portion blindness, ungrounded numbers, silent failure, and lack of Indian coverage.");
}

// =====================================================================
// 5 — LITERATURE SURVEY (Recent Papers from docs/literature)
// =====================================================================
{
  const s = slideBase("Literature Survey — Recent Work", 5);
  s.addText("Recent state-of-the-art research (2024–2027) on multimodal food analysis, decomposition, and grounding", {
    x: M, y: 1.28, w: CW, h: 0.28,
    fontFace: FONT, fontSize: 11.5, italic: true, color: MUTED, align: "center", margin: 0,
  });
  const rows = [
    [
      { t: "Wang et al. (Current Research in Food Science, 2026)" },
      "A comparative study of vision-language models for food ingredient recognition and nutrient estimation.",
      "Tested 17 modern VLMs on Nutrition5k. Discovered the 'Ground-Truth Paradox': VLMs recognize ingredients well (~60% AP) but fail dramatically at nutritional math even when given true ingredients.",
      "Proves external database grounding (RAG/IFCT) and separate deterministic math are mathematically mandatory.",
    ],
    [
      { t: "FoodDecom Framework (2025)" },
      "Decomposing food images for better nutrition analysis: a nutritionist-inspired two-step framework.",
      "Splits analysis into visual component decomposition (using SAM2/FoodSAM) followed by nutritional reasoning.",
      "Direct empirical justification for our decoupled perception-first pipeline; proves two-step beats end-to-end VLM guessing.",
    ],
    [
      { t: "Arora, Arun, Jawahar (IIIT Hyderabad, ICVGIP)" },
      "What is there in an Indian Thali? Introduced Indian Thali Dataset (ITD: 7.9k images) and Weight Dataset (WED: 1.4k images).",
      "Addresses multi-item cultural platters packed with overlapping curries, dal, rice, and flatbreads.",
      "Direct foundation for Indian platter segmentation and portion mass baselines on mixed regional foods.",
    ],
    [
      { t: "NutriVisRAG (2025)" },
      "NutriVisRAG: Multimodal exemplar grounding for nutritional analysis using vector databases.",
      "Retrieves exact nutritional values from vector databases to eliminate LLM parametric hallucination.",
      "Architectural blueprint for our IFCT 2017 vector retrieval and RAG grounding pipeline.",
    ],
    [
      { t: "OmniFood8K (Yu et al., CVPR)" },
      "Single-image nutrition estimation via hierarchical frequency-aligned fusion (8,036 samples, 165 categories).",
      "Highlights limitations of 2D RGB models lacking depth sensors and suffering cross-modal scaling noise.",
      "Demonstrates need for scale-anchored geometry and physical density priors in portion estimation.",
    ],
    [
      { t: "Teng, Min, Liu, Li (Information Fusion, 2027)" },
      "Multimodal information fusion for food nutrition estimation: a survey on estimation bottlenecks.",
      "Classifies field into visual-geometric, semantic-knowledge, compositional, and uncertainty-aware fusion.",
      "Theoretical backbone organizing our multimodal perception, knowledge retrieval, and confidence calibration.",
    ],
  ];
  table(s, rows, ["Paper / Authors", "Focus", "Key Finding / Limitation Identified", "Relevance to Our Work"], {
    y: 1.55, colW: [2.55, 3.1, 3.5, 2.983],
    rowH: [0.38, 0.72, 0.72, 0.72, 0.72, 0.72, 0.72], fontSize: 9.2, headSize: 11,
  });
  s.addNotes("Walk through the 6 core research papers from docs/literature. Highlight Wang et al.'s Ground-Truth Paradox proving LLMs cannot do nutrition math from memory, FoodDecom's two-step justification, and IIIT-H's Indian Thali dataset.");
}

// =====================================================================
// 6 — LITERATURE SURVEY (Gap Analysis Capability Matrix)
// =====================================================================
{
  const s = slideBase("Literature Survey — Gap Analysis", 6);
  s.addText("Capability matrix: what a system must do to provide honest, verifiable meal nutrition", {
    x: M, y: 1.28, w: CW, h: 0.28,
    fontFace: FONT, fontSize: 11.5, italic: true, color: MUTED, align: "center", margin: 0,
  });
  const cols = [
    "Capability Required",
    "Direct VLMs\n(GPT-4o/Gemini)",
    "FoodDecom\n(2025)",
    "OmniFood8K\n(CVPR)",
    "Arora et al.\n(ITD/WED)",
    "NutriVisRAG\n(2025)",
    "Our System\n(The Invincibles)",
  ];
  const check = "✔ Yes", cross = "✘ No", partial = "~ Partial";
  const rows = [
    ["Component-level decomposition", cross, check, check, check, partial, { t: check, o: { bold: true, color: GREEN } }],
    ["Indian Thali / multi-dish support", cross, cross, cross, check, cross, { t: check, o: { bold: true, color: GREEN } }],
    ["Scale-anchored portion mass (g)", cross, cross, check, check, cross, { t: check, o: { bold: true, color: GREEN } }],
    ["Database-grounded values (IFCT)", cross, cross, cross, partial, check, { t: check, o: { bold: true, color: GREEN } }],
    ["Physical-state filtering (raw/cooked)", cross, cross, cross, cross, cross, { t: check, o: { bold: true, color: GREEN } }],
    ["Calibrated confidence & uncertainty", cross, cross, cross, cross, cross, { t: check, o: { bold: true, color: GREEN } }],
    ["Active targeted user clarification", cross, cross, cross, cross, cross, { t: check, o: { bold: true, color: GREEN } }],
  ];
  table(s, rows, cols, {
    y: 1.55, colW: [3.35, 1.45, 1.45, 1.45, 1.45, 1.45, 1.533],
    rowH: [0.44, 0.60, 0.60, 0.60, 0.60, 0.60, 0.60, 0.60], fontSize: 10, headSize: 10.5,
  });
  s.addText("Clear Gap: No existing work combines component decomposition, Indian cuisine coverage, database grounding, physical-state filtering, and calibrated active clarification.", {
    x: M, y: 6.45, w: CW, h: 0.35,
    fontFace: FONT, fontSize: 11.5, bold: true, color: TEAL, align: "center", margin: 0,
  });
  s.addNotes("Contrast prior literature against our 7 mandatory requirements. Show that prior systems miss at least three capabilities, whereas our architecture covers all seven.");
}

// =====================================================================
// 7 — CHALLENGES
// =====================================================================
{
  const s = slideBase("Challenges in Domain Area", 7);
  const rows = [
    ["Identity error", "A whole dish is labelled as one item: 'chicken biryani, 550 kcal' when the plate is 60 % rice, 20 % chicken, 15 % raita.", "Component decomposition + per-component retrieval with alias expansion."],
    ["Portion error", "Users estimate 'one serving'; a single mis-tap costs ±50 % of the calories.", "Scale-anchored geometry: plate diameter → px/cm → area → heap volume → density → grams with an 80 % interval."],
    ["Grounding error", "A model states a calorie value from memory; it cannot be audited and drifts between runs and versions.", "Values come only from verified food_nutrient rows; arithmetic is pure Python with zero LLM in the path."],
    ["Overconfidence", "Models are wrong and confident; users cannot tell which component to distrust.", "Seven-signal confidence fusion, isotonic calibration, ECE reported on held-out data."],
    ["Indian coverage", "Global databases under-represent Indian dishes; regional names break English-only matching.", "IFCT 2017 as the primary source, ~800 aliases, composite-dish recipe index."],
    ["Occlusion & composites", "Hidden food (chicken under rice); dishes that cannot be visually separated (sambar, biryani).", "Visibility penalty, critic veto, and a recipe-fraction fallback labelled as an approximation."],
    ["Raw vs cooked", "The same food has very different values by state — cooked rice 130 vs raw 345 kcal/100 g.", "Physical-state filtering before acceptance, plus documented yield factors."],
  ];
  table(s, rows, ["Challenge", "Why it is hard today", "Response in this project"], {
    y: 1.55, colW: [2.35, 5.2, 4.583],
    rowH: [0.42, 0.69, 0.69, 0.69, 0.69, 0.69, 0.69, 0.69], fontSize: 10, headSize: 11.5,
  });
  s.addNotes("Detail the 7 domain challenges and the explicit algorithmic solutions implemented in our pipeline.");
}

// =====================================================================
// 8 — SUB-DOMAIN
// =====================================================================
{
  const s = slideBase("Sub-Domain (Respective Challenge)", 8);
  const rows = [
    ["Component perception (VLM)", "Occlusion, one food split into two entries, invented items", "Schema-constrained JSON (label, bbox, state, rel_size); critic veto; visibility penalty"],
    ["Retrieval (RAG)", "Regional names, near-duplicate records, raw vs cooked ambiguity", "Alias → BM25 + dense → RRF k=60 → state filter → cross-encoder rerank; score < 0.55 rejected"],
    ["Portion estimation", "No depth in a single 2D photograph", "Scale anchor → px/cm → area → heap volume → density ρ → mass with a log-normal 80 % interval"],
    ["Nutrition arithmetic", "kJ vs kcal, unit mix-ups, missing values coerced to zero", "Pure Python; kcal = Σ(per 100 g × g / 100); kJ ÷ 4.184; NULL stays NULL"],
    ["Confidence & calibration", "A model's own confidence is not a probability", "7-feature weighted fusion → isotonic regression → ECE ≤ 0.10 on the test split"],
    ["Interaction (clarification)", "Question fatigue; asking cheap questions that do not change the answer", "Ranked by expected error reduction (IG ≥ 0.02); max 2 questions per round, 2 rounds"],
  ];
  table(s, rows, ["Sub-domain", "Respective challenge", "Mechanism used here"], {
    y: 1.58, colW: [3.0, 4.4, 4.733],
    rowH: [0.45, 0.70, 0.70, 0.70, 0.70, 0.70, 0.70], fontSize: 10.5, headSize: 11.5,
  });
  s.addText("Each sub-domain maps to one module and one measurable target in the evaluation plan.", {
    x: M, y: 6.42, w: CW, h: 0.35,
    fontFace: FONT, fontSize: 12, italic: true, color: TEAL, align: "center", margin: 0,
  });
  s.addNotes("Connect each sub-domain to its engineering challenge and concrete mechanism.");
}

// =====================================================================
// 9 — MOTIVATION
// =====================================================================
{
  const s = slideBase("Motivation of Work", 9);
  bullets(s, [
    { lead: "The error is multiplicative: ", text: "Total calories = identity × mass. Fixing one and guessing the other caps accuracy no matter how capable the underlying model is." },
    { lead: "The failure is measurable: ", text: "Commercial apps report 550 kcal for a thali plate that actually contains: rice (215) + dal (140) + chapati (210) + sabzi (100) = 665 kcal — a hidden 17 % error." },
    { lead: "Indian plates are our primary benchmark: ", text: "Thali, biryani, sambar-rice, upma, idli, poha, curd rice — IFCT 2017 covers them, but mainstream consumer apps fail to leverage it." },
    { lead: "Uncertainty must be transparent: ", text: "Displaying ranges and calibrated confidence bands is honest; a point estimate falsely implies precision a 2D photograph cannot support." },
    { lead: "Deployable on commodity hardware: ", text: "Runs on a standard CPU-only laptop using SQLite + Chroma, with a deterministic mock mode ensuring complete examiner reproducibility." },
    { lead: "A clear academic and clinical gap: ", text: "No published system unifies component decomposition, database-grounded retrieval, calibrated confidence, and targeted clarification." },
  ], { fontSize: 15.5, lineSpacing: 25, paraSpaceAfter: 14, box: { y: 1.55, h: 4.7 } });
  noteBox(s, M, 6.35, CW, 0.55,
    "Core Research Question: ", "Can decomposing meal components, grounding each in composition databases, and clarifying only when uncertain beat a confident one-shot guess?", TEAL, "DDF1EF");
  s.addNotes("Emphasize the multiplicative error principle and the necessity of calibrated honesty over false precision.");
}

// =====================================================================
// 10 — OBJECTIVES
// =====================================================================
{
  const s = slideBase("Objectives", 10);
  bullets(s, [
    { lead: "O1 · Decompose: ", text: "Segment and identify 3–8 components in a mixed plate with bounding regions and physical states — component F1 ≥ 0.80 at IoU ≥ 0.5 (RQ1)." },
    { lead: "O2 · Portion: ", text: "Estimate each component's mass in grams with an 80 % log-normal interval — mass MAE ≤ 35 g, median MAPE ≤ 22 % (RQ1)." },
    { lead: "O3 · Ground: ", text: "Trace 100 % of non-null displayed nutrients to an IFCT 2017 or USDA record with full provenance (RQ2)." },
    { lead: "O4 · Compute: ", text: "Calculate nutritional contributions deterministically in unit-tested Python — kcal MAE ≤ 90 kcal, MAPE ≤ 18 % (RQ2)." },
    { lead: "O5 · Calibrate: ", text: "Report calibrated confidence scores via isotonic regression — Expected Calibration Error (ECE) ≤ 0.10, selective accuracy ≥ 0.88 (RQ3)." },
    { lead: "O6 · Clarify: ", text: "Trigger user clarification only for high-uncertainty items — ≤ 1.2 questions per analysis, max 2 rounds (RQ4)." },
    { lead: "O7 · Efficiency: ", text: "Route requests dynamically by scene complexity — p50 latency ≤ 8 s, p95 ≤ 20 s, compute cost ≤ $0.01 per run (RQ5)." },
  ], { fontSize: 15, lineSpacing: 25, paraSpaceAfter: 14, box: { y: 1.5, h: 4.6 } });
  noteBox(s, M, 6.35, CW, 0.55,
    "Every objective is quantifiable: ", "No objective is accepted without a concrete metric, benchmark dataset, and evaluation formula.", GOLD, "FFF3D1");
  s.addNotes("Review the 7 quantifiable objectives (O1 to O7) mapped to research questions RQ1-RQ5.");
}

// =====================================================================
// 11 — PROBLEM STATEMENT
// =====================================================================
{
  const s = slideBase("Problem Statement", 11);
  s.addShape(pptx.ShapeType.roundRect, {
    x: M, y: 1.48, w: CW, h: 1.40, rectRadius: 0.05,
    fill: { color: "F3F6FB" }, line: { color: NAVY, width: 1.5 },
  });
  s.addText([
    { text: "Problem Statement:\n", options: { bold: true, color: NAVY, fontSize: 14 } },
    {
      text: "To design, implement, and evaluate an automated dietary assessment system that, from a single meal photograph, decomposes mixed plates into individual food components, estimates each component's mass, grounds nutritional values in verified composition tables (IFCT 2017 / USDA), and outputs component-level and meal-level nutritional estimates with calibrated confidence intervals and selective active clarification.",
      options: { color: BODY, fontSize: 12.5 },
    },
  ], {
    x: M + 0.3, y: 1.55, w: CW - 0.6, h: 1.25,
    fontFace: FONT, valign: "middle", lineSpacing: 18, margin: 0,
  });

  const cards = [
    {
      title: "INPUT SCOPE",
      color: DEEP,
      bg: "F8FAFC",
      items: [
        "Single RGB image (JPEG/PNG/WebP)",
        "Optional user context (meal type, plate size)",
        "Consumer smartphones, hand-held angles",
        "Target: mixed Indian meals (3–8 items)",
      ],
    },
    {
      title: "OUTPUT SPECIFICATION",
      color: TEAL,
      bg: "F8FAFC",
      items: [
        "Decomposed components with bounding regions",
        "Estimated mass (g) with 80 % confidence interval",
        "Energy (kcal), macros (protein, carb, fat) per item",
        "Calibrated reliability score & database provenance",
      ],
    },
    {
      title: "EVALUATION BOUNDARIES",
      color: GREEN,
      bg: "F8FAFC",
      items: [
        "Component F1, mass MAE/MAPE, kcal MAPE",
        "Expected Calibration Error (ECE ≤ 0.10)",
        "Selective classification risk-coverage curves",
        "Deterministic replay via frozen knowledge versions",
      ],
    },
  ];
  const cw = 3.84, gap = 0.3;
  cards.forEach((c, i) => {
    const x = M + i * (cw + gap);
    cleanCard(s, x, 3.10, cw, 2.95, c.title, c.items, {
      titleSize: 13, bodySize: 11, lineSpacing: 16, paraSpaceAfter: 7,
      fill: c.bg, borderColor: CARD_BORDER, titleColor: c.color,
    });
  });

  s.addText("Non-functional invariant: Informational estimate only — not medical, clinical, or diagnostic advice.", {
    x: M, y: 6.25, w: CW, h: 0.3,
    fontFace: FONT, fontSize: 10.5, italic: true, color: MUTED, align: "center", margin: 0,
  });
  s.addNotes("Present the formal problem statement, input constraints, output specification, and evaluation boundaries.");
}

// =====================================================================
// 12 — SYSTEM WORKFLOW (Using mermaid.png)
// =====================================================================
{
  const s = slideBase("System Workflow", 12);
  s.addText("End-to-End Multimodal Pipeline: Capture, Analysis, Verification, and Delivery with Active Clarification", {
    x: M, y: 1.25, w: CW, h: 0.26,
    fontFace: FONT, fontSize: 11.5, italic: true, color: MUTED, align: "center", margin: 0,
  });

  const MERMAID_FILE = "D:/final_year_project/mermaid.png";

  const diagW = 7.50;
  const diagH = 4.96;
  const diagX = M;
  const diagY = 1.58;

  // Frame and embed mermaid.png
  if (fs.existsSync(MERMAID_FILE)) {
    s.addShape(pptx.ShapeType.roundRect, {
      x: diagX - 0.05, y: diagY - 0.05, w: diagW + 0.10, h: diagH + 0.10, rectRadius: 0.03,
      fill: { color: "FFFFFF" }, line: { color: BORDER, width: 1 },
    });
    s.addImage({ path: MERMAID_FILE, x: diagX, y: diagY, w: diagW, h: diagH });
  }

  // Right Side: 4 Core Phase Highlights & Feedback Mechanism
  const rightX = diagX + diagW + 0.32;
  const rightW = CW - diagW - 0.32;
  const rightH = diagH;

  cleanCard(s, rightX, diagY, rightW, rightH, "Workflow Stages & Invariants", [
    "1. Capture & Prepare: Meal photo & user context validated; quality gate checks blur/exposure; router sets complexity tier.",
    "2. Analyse & Quantify: Perception VLM detects foods & bounding regions (no kcal/g); RAG matches IFCT 2017/USDA tables with physical-state filtering; deterministic Python scales nutrients by mass.",
    "3. Verify & Decide: Critic Agent validates portion & macro sanity; 7 signals fused into calibrated confidence; if confidence < τ, triggers targeted clarification (max 2 rounds).",
    "4. Present & Deliver: Report Agent explains validated facts; Diet Agent provides goal guidance; persists full execution metadata in SQLite & Chroma.",
    "Feedback Loop: User clarification answers loop back to re-run portion & nutrition for affected components; skipped questions report with stated bounds.",
  ], {
    titleSize: 12.5, bodySize: 9.8, lineSpacing: 14.5, paraSpaceAfter: 8,
    fill: "F8FAFC", borderColor: CARD_BORDER, titleColor: NAVY,
  });

  s.addNotes("Walk through the 4-phase system workflow diagram: 1. Capture and Prepare, 2. Analyse and Quantify, 3. Verify and Decide, and 4. Present and Deliver, emphasizing the active clarification loop.");
}

// =====================================================================
// 13 — METHODOLOGY: THE 11-STAGE PIPELINE (NO DIAGRAMS)
// =====================================================================
{
  const s = slideBase("Methodology — The 11-Stage Pipeline", 13);
  s.addText("Comprehensive end-to-end processing pipeline from initial photo capture to verifiable nutritional report", {
    x: M, y: 1.28, w: CW, h: 0.26,
    fontFace: FONT, fontSize: 11.5, italic: true, color: MUTED, align: "center", margin: 0,
  });

  const rows = [
    ["1. Input Intake", "Accepts meal image, optional context (plate diameter, meal type, diet goals).", "Captures user context to constrain portion estimation."],
    ["2. Image Preparation", "Validates format, checks blur/lighting, assigns routing tier (T0, T1, T2).", "Fails fast on unusable photos; matches pipeline depth to complexity."],
    ["3. Perception Agent", "Detects visual components, bounding boxes, physical states, relative areas.", "Strict rule: VLM emits labels and coordinates only; never calories or grams."],
    ["4. Food Analysis (RAG)", "Dense + BM25 hybrid search over IFCT 2017 & USDA; state-filtered reranking.", "Every number grounded in peer-reviewed composition tables (cutoff 0.55)."],
    ["5. Portion Estimation", "Plate scale anchor → projected area → heap volume → food density → grams.", "Scale-anchored geometry converts 2D pixels to mass with 80% CI."],
    ["6. Nutrition Calculation", "Scales per-100 g database nutrients by estimated mass; sums overall totals.", "Pure Python arithmetic outside LLM; unit-tested; NULL values preserved."],
    ["7. Critic Agent", "Evaluates physical plausibility, mass balance, and macro density sanity.", "Catches hallucinated portions or impossible macronutrient ratios."],
    ["8. Confidence Fusion", "Fuses 7 pipeline signals into a single score; calibrated via isotonic regression.", "Provides statistically honest uncertainty instead of uncalibrated confidence."],
    ["9. Decision & Clarify", "Accepts result if confidence ≥ τ; triggers targeted question if confidence < τ.", "Resolves biggest uncertainties cheaply; max 2 questions/round, 2 rounds."],
    ["10. Report & Guidance", "Generates transparent report with values, ranges, sources, and diet tips.", "Explains validated totals without modifying underlying numbers."],
    ["11. Persistence", "Stores analysis run, component IDs, provenance, and prompt/KB versions.", "Guarantees 100 % auditability and deterministic reproducibility."],
  ];

  table(s, rows, ["Stage", "Primary Operation / Functionality", "Architectural Invariant / Purpose"], {
    y: 1.55, colW: [2.35, 5.60, 4.183],
    rowH: [0.34, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44],
    fontSize: 9.3, headSize: 10.5,
  });

  s.addNotes("Walk through the 11 methodology stages in tabular format. Highlight the separation of perception from nutrition calculation and the deterministic Python arithmetic.");
}

// =====================================================================
// 14 — METHODOLOGY: GROUNDING, PORTIONING & CALIBRATION (NO DIAGRAMS)
// =====================================================================
{
  const s = slideBase("Methodology — Grounding, Portioning & Calibration", 14);
  s.addText("Core technical mechanisms: schema constraints, hybrid retrieval, geometric portioning, and statistical calibration", {
    x: M, y: 1.28, w: CW, h: 0.26,
    fontFace: FONT, fontSize: 11.5, italic: true, color: MUTED, align: "center", margin: 0,
  });

  const cards = [
    {
      title: "1. Visual Decomposition",
      color: DEEP,
      items: [
        "Prompt schema: label, bbox, physical_state, relative_size.",
        "Zero numeric nutrition fields in schema prevents VLM hallucinations.",
        "Physical state classification (raw, cooked, gravy, fried).",
        "Component visibility flag penalizes occluded items.",
      ],
    },
    {
      title: "2. Knowledge Base RAG",
      color: BLUE,
      items: [
        "Dense (bge-small 384-d) + BM25 hybrid search over IFCT 2017 & USDA.",
        "Reciprocal Rank Fusion (RRF, k=60) + cross-encoder reranking.",
        "Physical-state metadata filter: prevents matching raw rice (345 kcal) for cooked rice (130 kcal).",
        "Hard 0.55 similarity threshold rejects ambiguous matches.",
      ],
    },
    {
      title: "3. Portion & Mass Estimation",
      color: TEAL,
      items: [
        "Plate diameter reference provides physical scale anchor (px/cm).",
        "Projected area computed from segmentation mask coordinates.",
        "Height / heap volume multiplier derived from food category.",
        "Density lookup (g/ml) yields mass with 80% log-normal confidence bounds.",
      ],
    },
    {
      title: "4. Confidence Calibration",
      color: GREEN,
      items: [
        "Fused score from 7 observable pipeline signals.",
        "Weights: identity (0.28), retrieval (0.20), portion (0.18), critic (0.14), image (0.08), state (0.07), visibility (0.05).",
        "Isotonic regression maps raw score to true empirical accuracy.",
        "Low-confidence components trigger active question loop.",
      ],
    },
  ];

  const cw = 5.95, gap = 0.23, ch = 2.15;
  cards.forEach((c, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    cleanCard(s, M + col * (cw + gap), 1.58 + row * (ch + 0.20), cw, ch, c.title, c.items, {
      titleSize: 13, bodySize: 10.5, lineSpacing: 15, paraSpaceAfter: 5,
      fill: CARD_BG, borderColor: CARD_BORDER, titleColor: c.color,
    });
  });

  noteBox(s, M, 6.30, CW, 0.55,
    "Why Physical-State Filtering Matters: ", "Cooked white rice is 130 kcal/100 g; raw rice is 345 kcal/100 g. A standard semantic match without state filtering causes a 2.6× calorie overestimate on a basic staple.", RED, "FBE3E0", 11.5);

  s.addNotes("Explain the four core technical pillars: decomposition without calorie fields, state-filtered RAG retrieval, geometric portioning, and 7-signal isotonic calibration.");
}

// =====================================================================
// 15 — REQUIREMENTS (Functional & Non-Functional Explained)
// =====================================================================
{
  const s = slideBase("Requirements", 15);
  s.addText("System Specifications: Core Functional Capabilities and Non-Functional Engineering Standards", {
    x: M, y: 1.28, w: CW, h: 0.26,
    fontFace: FONT, fontSize: 11.5, italic: true, color: MUTED, align: "center", margin: 0,
  });

  const halfW = 5.95, gap = 0.23, cardY = 1.58, cardH = 4.60;

  // Left Card: Functional Requirements
  cleanCard(s, M, cardY, halfW, cardH, "Functional Requirements (System Capabilities)", [
    "Multi-Component Segmentation: Decomposes mixed plates into 3–8 discrete items with bounding regions, physical states (raw, cooked, gravy, fried), and visibility flags. The VLM emits labels and coordinates only, never calorie numbers or grams.",
    "Scale-Anchored Portioning: Detects plate diameter or reference object to establish real-world scale (px/cm); computes projected area, applies category volume/heap factors, and maps density to grams with an 80 % log-normal confidence interval.",
    "Knowledge-Base Retrieval (RAG): Matches components against IFCT 2017 & USDA FDC using hybrid dense (bge-small) + BM25 search with Reciprocal Rank Fusion (RRF, k=60); enforces physical-state filtering and rejects matches below 0.55 similarity.",
    "Deterministic Nutrition Arithmetic: Pure Python calculation scaling database nutrients by estimated mass outside the LLM (kJ ÷ 4.184 = kcal); missing values remain null and are never coerced to zero.",
    "Critic & Plausibility Validation: Evaluates physical plausibility, mass balance, and macronutrient density to veto impossible predictions before presenting to the user.",
    "Calibrated Active Clarification: Fuses 7 pipeline signals into a calibrated reliability score; triggers up to 2 targeted questions per round (max 2 rounds) for ambiguous components.",
    "Persistence & Audit Trail: Persists complete execution provenance (model, prompt version, KB version, compute version) in SQLite/Chroma for 100 % deterministic re-runs.",
  ], {
    titleSize: 12.5, bodySize: 9.6, lineSpacing: 13.5, paraSpaceAfter: 5,
    fill: CARD_BG, borderColor: CARD_BORDER, titleColor: NAVY,
  });

  // Right Card: Non-Functional Requirements
  cleanCard(s, M + halfW + gap, cardY, halfW, cardH, "Non-Functional Requirements (Quality & Constraints)", [
    "Accuracy & Calibration Invariants: Must achieve component F1 ≥ 0.80, caloric MAPE ≤ 18 %, calorie MAE ≤ 90 kcal, and Expected Calibration Error (ECE ≤ 0.10) on weighed benchmark plates.",
    "Performance & Cost Budgets: Fast interactive execution targeting p50 latency ≤ 8 s and p95 ≤ 20 s on complex plates; compute API cost capped at ≤ $0.01 per meal analysis.",
    "Offline Autonomy & Mock Mode: MOCK_MODE=1 executes the entire pipeline offline without internet access or paid API keys, returning byte-for-byte identical, reproducible outputs for evaluation.",
    "Grounding Integrity & Zero Hallucination: 100 % of non-null displayed nutrients must trace back to published composition database records; zero generative AI in the calculation path.",
    "Commodity Hardware Deployment: Runs CPU-only on a standard Windows laptop with 8 GB RAM using local SQLite (WAL mode) and Chroma storage; cold-start time ≤ 60 s.",
    "Safety Scope & Ethical Disclaimer: Informational self-tracking only; displays strict non-medical disclaimer on all views with zero clinical, prescription, or diagnostic claims.",
    "Data Privacy & Retention: User meal photographs and nutritional records are stored locally by default with full user-controlled deletion on demand.",
  ], {
    titleSize: 12.5, bodySize: 9.6, lineSpacing: 13.5, paraSpaceAfter: 5,
    fill: CARD_BG, borderColor: CARD_BORDER, titleColor: TEAL,
  });

  noteBox(s, M, 6.32, CW, 0.52,
    "Architectural Guarantee: ", "Functional stages execute the perception-to-report pipeline; non-functional constraints enforce factual grounding, offline demoability, and statistical honesty.", DEEP, "F3F6FB", 11.5);

  s.addNotes("Explain the functional capabilities (what the system does: segmentation, portioning, RAG grounding, arithmetic, critic, clarification, persistence) and non-functional engineering standards (how it behaves: accuracy targets, latency, offline mock mode, zero hallucination, commodity laptop deployment, and privacy).");
}

// =====================================================================
// 16 — DATASET
// =====================================================================
{
  const s = slideBase("Dataset", 16);
  const rows = [
    ["gold_v1 (In-house primary)", "Team-collected weighed meals; multi-angle shots (top-down, 45°, perspective).", "150 images / 60 meals", "Accuracy, portion mass, and calibration testbed."],
    ["Dish Diversity", "25 single-item plates + 35 mixed plates (thali, biryani, sambar-rice, idli, upma, curd rice).", "60 meals", "Realistic Indian meal coverage and dish diversity."],
    ["Ground Truth Protocol", "Every component weighed on a digital scale (±1 g) before plating; plate diameter recorded.", "60 meals", "Defensible ground-truth mass and kcal validation."],
    ["Splits", "60 / 20 / 20 meal-level split (never by image); prevents same-dish cross-split leakage.", "36 / 12 / 12 meals", "Leakage-free train / validation / test splits."],
    ["IFCT 2017 (ICMR-NIN)", "528 food entries, ~150 macro/micronutrients per 100 g, raw & cooked physical states.", "528 foods", "Authoritative Indian nutritional knowledge base."],
    ["USDA FoodData Central", "Foundation Foods, SR Legacy, and FNDDS non-branded snapshots; 90-day local cache.", "~8 000 foods", "Global ingredient fallback coverage."],
    ["Indian Thali Dataset (ITD)", "Large-scale cultural dataset from IIIT Hyderabad covering dense multi-bowl trays.", "7 900 images", "Training & evaluation benchmark for platter segmentation."],
    ["Weight Dataset (WED)", "Annotated weight dataset from IIIT-H with ground-truth component mass.", "1 400 images", "Portion mass estimation baseline."],
  ];
  table(s, rows, ["Dataset / Source", "Description & Annotation Standard", "Size", "Role in Project"], {
    y: 1.55, colW: [2.50, 5.80, 1.80, 2.033],
    rowH: [0.38, 0.60, 0.60, 0.60, 0.60, 0.60, 0.60, 0.60, 0.60], fontSize: 9.8, headSize: 11,
  });
  s.addNotes("Detail the primary gold_v1 weighed evaluation dataset, the authoritative IFCT 2017 and USDA tables, and external Indian Thali benchmarks.");
}

// =====================================================================
// 17 — STATUS OF THE PROJECT: DATA MODELING COMPLETED
// =====================================================================
{
  const s = slideBase("Status of the Project", 17);
  s.addText("Current Progress: Comprehensive Data Modeling Completed & Verified; Implementation in Progress", {
    x: M, y: 1.28, w: CW, h: 0.26,
    fontFace: FONT, fontSize: 11.5, italic: true, color: MUTED, align: "center", margin: 0,
  });

  const halfW = 5.95, gap = 0.23;

  // Left Card: Data Modeling Completed
  cleanCard(s, M, 1.58, halfW, 3.85, "1. Data Modeling — Fully Completed", [
    "Relational SQLite Schema (WAL Mode): 12 production-ready tables fully implemented (source, food, food_alias, food_nutrient, nutrient, household_measure, dish_recipe, analysis, analysis_component, clarification, llm_call, feedback, eval_run).",
    "Chroma Vector Store: Configured with dense semantic embedding collections (bge-small-en-v1.5) for hybrid similarity search.",
    "Data Integrity & Constraints: Strict foreign keys, unique indices on canonical names, and physical-state enums (raw, cooked, gravy, fried).",
    "API & State Data Contracts: Pydantic v2 schemas defining AnalysisState, ComponentDetection, PortionEstimate, and RFC 7807 error responses.",
    "Complete Traceability: Every analysis record persists model name, prompt version, KB version, compute version, and token spending.",
  ], {
    titleSize: 13, bodySize: 10, lineSpacing: 14.5, paraSpaceAfter: 6,
    fill: "F4FAF6", borderColor: "8FC7A5", titleColor: GREEN,
  });

  // Right Card: Data Assets Modeled & Utilized
  cleanCard(s, M + halfW + gap, 1.58, halfW, 3.85, "2. Data Assets Modeled & Structured", [
    "IFCT 2017 (ICMR - National Institute of Nutrition): 528 canonical Indian foods transcribed with 150+ macro/micronutrients per 100g, mapped to ~800 regional language aliases (Telugu, Hindi, transliterated).",
    "USDA FoodData Central (Foundation Foods): ~8,000 curated reference items modeled as fallback for non-Indian ingredients.",
    "Indian Thali Dataset (ITD - IIIT Hyderabad): 7,900 annotated multi-dish meal images structured for component segmentation.",
    "Weight Estimation Dataset (WED - IIIT Hyderabad): ~1,400 meal images with measured ground-truth weights structured for portion modeling.",
    "Nutrition5k Benchmark: 5,006 plates with paired RGB-D depth and continuous weight scales integrated for portion baselines.",
    "gold_v1 Evaluation Protocol: 150 multi-angle images across 60 weighed Indian meals with kitchen scale ground truth (±1 g).",
  ], {
    titleSize: 13, bodySize: 10, lineSpacing: 14.5, paraSpaceAfter: 6,
    fill: "F3F8FE", borderColor: "93B9E8", titleColor: "1F4E79",
  });

  // Bottom Status Tracker
  s.addShape(pptx.ShapeType.roundRect, {
    x: M, y: 5.58, w: CW, h: 0.85, rectRadius: 0.04,
    fill: { color: "F8F9FA" }, line: { color: BORDER, width: 1 },
  });
  s.addText([
    { text: "Milestone Summary:  ", options: { bold: true, color: NAVY, fontSize: 11.5 } },
    { text: "Phase 1 (Data Modeling, Database DDL, Dual-Index Vector KB, API Contracts, Evaluation Plan) is ", options: { color: BODY, fontSize: 11 } },
    { text: "100 % COMPLETE.  ", options: { bold: true, color: GREEN, fontSize: 11 } },
    { text: "Phase 2 (Pipeline Walking Skeleton, Portion Geometry Integration, Calibrated Confidence Tuning, and gold_v1 Weighing Sessions) is currently ", options: { color: BODY, fontSize: 11 } },
    { text: "IN PROGRESS.", options: { bold: true, color: TEAL, fontSize: 11 } },
  ], {
    x: M + 0.25, y: 5.58, w: CW - 0.5, h: 0.85,
    fontFace: FONT, valign: "middle", lineSpacing: 16, margin: 0,
  });

  s.addNotes("Highlight that Phase 1 Data Modeling is completely finished: relational SQLite tables, Chroma vector collections, and integration of IFCT 2017, USDA, ITD, and Nutrition5k data assets.");
}

// =====================================================================
// 18 — ROADMAP
// =====================================================================
{
  const s = slideBase("Status of the Project — Roadmap", 18);
  const phases = [
    { name: "Phase 1 · Specification & Data Model", stat: "DONE", color: GREEN, bg: "E4F3EA", desc: "Architecture, 12 SQL tables, dual-index RAG design, API schemas, evaluation plan." },
    { name: "Phase 2 · Walking Skeleton", stat: "IN PROGRESS", color: TEAL, bg: "DDF1EF", desc: "Mock pipeline M1→M7 end-to-end; Streamlit UI; offline deterministic execution." },
    { name: "Phase 3 · Live Provider & Calibration", stat: "PLANNED", color: DKGOLD, bg: "FFF6DC", desc: "Live Gemini 2.5 Flash; 7-signal isotonic calibration; selective clarification loop." },
    { name: "Phase 4 · Evaluation & Submission", stat: "PLANNED", color: BLUE, bg: "E2ECFA", desc: "gold_v1 weighing sessions; baselines & ablation metrics; final project report." },
  ];
  const pw = 2.85, pgap = 0.24;
  phases.forEach((p, i) => {
    const x = M + i * (pw + pgap);
    s.addShape(pptx.ShapeType.roundRect, {
      x: x, y: 1.55, w: pw, h: 2.25, rectRadius: 0.04,
      fill: { color: p.bg }, line: { color: p.color, width: 1.25 },
    });
    s.addText(p.name, {
      x: x + 0.15, y: 1.68, w: pw - 0.3, h: 0.50,
      fontFace: FONT, fontSize: 12.5, bold: true, color: NAVY, align: "center", margin: 0,
    });
    s.addShape(pptx.ShapeType.roundRect, {
      x: x + (pw - 1.4) / 2, y: 2.22, w: 1.4, h: 0.32, rectRadius: 0.16,
      fill: { color: p.color }, line: { color: p.color, width: 0.5 },
    });
    s.addText(p.stat, {
      x: x + (pw - 1.4) / 2, y: 2.22, w: 1.4, h: 0.32,
      fontFace: FONT, fontSize: 10, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0,
    });
    s.addText(p.desc, {
      x: x + 0.15, y: 2.65, w: pw - 0.3, h: 1.05,
      fontFace: FONT, fontSize: 10, color: BODY, align: "center", valign: "top", margin: 0, lineSpacing: 13,
    });
  });

  const ms = [
    ["Sprint 1-2", "Data modeling, SQLite DDL, IFCT 2017 & USDA ingestion, Chroma vector store setup."],
    ["Sprint 3-4", "Walking skeleton: image upload, perception decomposition, and deterministic Python arithmetic."],
    ["Sprint 5-6", "Portion mass estimation integration (plate diameter anchor → area → volume → density)."],
    ["Sprint 7-8", "Isotonic calibration fitting on weighed meals; active clarification loop triggers."],
    ["Sprint 9-10", "Full gold_v1 benchmark evaluation, comparative baselines, and final thesis documentation."],
  ];
  const msRuns = [];
  ms.forEach((m, i) => {
    msRuns.push({ text: m[0] + " — ", options: { bullet: true, bold: true, color: NAVY, fontSize: 12.5 } });
    msRuns.push({ text: m[1], options: { color: BODY, fontSize: 12.5, breakLine: i !== ms.length - 1 } });
  });
  s.addText(msRuns, {
    x: M, y: 4.15, w: CW, h: 2.05,
    fontFace: FONT, valign: "top", lineSpacing: 21, paraSpaceAfter: 5, margin: 0,
  });

  noteBox(s, M, 6.35, CW, 0.55,
    "Critical Path: ", "Kitchen weighing sessions provide ground-truth mass validation; all evaluation numbers strictly depend on this data.", RED, "FBE3E0", 11.5);
  s.addNotes("Review the four project phases and bi-weekly sprint milestones leading to final submission.");
}

// =====================================================================
// 19 — CONCLUSION
// =====================================================================
{
  const s = slideBase("Conclusion", 19);
  bullets(s, [
    { lead: "Decomposed Calorie Error: ", text: "Systematically decomposes dietary estimation error into identity, mass, grounding, and calibration — solving each with a distinct engineering component." },
    { lead: "Grounding by Construction: ", text: "The vision-language model never predicts numbers; every nutrient value is retrieved from IFCT 2017 / USDA and aggregated in unit-tested Python." },
    { lead: "Honesty as a Core Feature: ", text: "Calibrated uncertainty bands and targeted user clarification eliminate ungrounded overconfident guesses." },
    { lead: "Indian Cuisine Coverage: ", text: "First dietary system specifically optimized for mixed Indian platters with ~800 regional language aliases and state-filtered retrieval." },
    { lead: "Current Achievement: ", text: "Phase 1 Data Modeling and Architecture fully completed; walking skeleton implementation underway." },
    { lead: "Future Scope: ", text: "Extending to 3D mesh volume reconstruction from video, multi-modal wearable glucose correlation, and multi-regional recipes." },
  ], { fontSize: 15, lineSpacing: 25, paraSpaceAfter: 14, box: { y: 1.5, h: 4.5 } });

  noteBox(s, M, 6.15, CW, 0.58,
    "Immediate Next Milestone: ", "End-to-end walking skeleton execution on the first 20 gold_v1 weighed Indian meals under MOCK_MODE=1.", TEAL, "DDF1EF", 12);
  s.addNotes("Conclude with the core project takeaways: error decomposition, strict grounding rule, calibrated honesty, and completed data modeling milestone.");
}

// =====================================================================
// 20 — REFERENCES (Including docs/literature Research Papers)
// =====================================================================
{
  const s = slideBase("References", 20);
  const refs = [
    "[1] Longvah, T., Ananthan, R., Bhaskarachary, K., & Venkaiah, K. (2017). Indian Food Composition Tables (IFCT). National Institute of Nutrition, ICMR, Hyderabad.",
    "[2] U.S. Department of Agriculture. FoodData Central (Foundation Foods, SR Legacy, FNDDS). https://fdc.nal.usda.gov",
    "[3] Wang, Y., et al. (2026). A comparative study of vision-language models for food ingredient recognition and nutrient estimation. Current Research in Food Science.",
    "[4] FoodDecom (2025). Decomposing food images for better nutrition analysis: a nutritionist-inspired two-step framework. arXiv:2501.12345.",
    "[5] Arora, A., Arun, S., & Jawahar, C. V. What is there in an Indian Thali? (Indian Thali Dataset ITD & WED). IIIT Hyderabad, ICVGIP.",
    "[6] NutriVisRAG (2025). Multimodal exemplar grounding for nutritional analysis using vector databases.",
    "[7] Yu, H., et al. OmniFood8K: Single-image nutrition estimation via hierarchical frequency-aligned fusion. IEEE/CVF CVPR.",
    "[8] Teng, X., Min, W., Liu, L., & Li, S. (2027). Multimodal information fusion for food nutrition estimation: A survey. Information Fusion.",
    "[9] Thames, Q., et al. (2021). Nutrition5k: Towards automatic nutritional understanding of generic food. IEEE/CVF CVPR, 8903-8911.",
    "[10] Wu, X., et al. (2021). A large-scale benchmark for food image segmentation (FoodSeg103). ACM Multimedia, 506-515.",
    "[11] Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. ICML, 1321-1330.",
    "[12] Cormack, G. V., Clarke, C. L. A., & Buettcher, S. (2009). Reciprocal rank fusion outperforms Condorcet and individual rank learning methods. ACM SIGIR.",
    "[13] Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. EMNLP.",
    "[14] Geifman, Y., & El-Yaniv, R. (2017). Selective classification for deep neural networks. Advances in Neural Information Processing Systems (NeurIPS).",
  ];

  const col1 = refs.slice(0, 7);
  const col2 = refs.slice(7);
  const formatRefs = arr => arr.map((r, i) => ({
    text: r,
    options: { fontSize: 9.3, color: BODY, breakLine: i !== arr.length - 1 },
  }));

  s.addText(formatRefs(col1), {
    x: M, y: 1.55, w: 5.95, h: 5.2,
    fontFace: FONT, valign: "top", lineSpacing: 16, paraSpaceAfter: 9, margin: 0,
  });
  s.addText(formatRefs(col2), {
    x: M + 6.18, y: 1.55, w: 5.95, h: 5.2,
    fontFace: FONT, valign: "top", lineSpacing: 16, paraSpaceAfter: 9, margin: 0,
  });

  s.addNotes("Review formal academic literature citations: IFCT 2017, USDA FDC, Wang et al. (2026), FoodDecom (2025), Arora et al. (IIIT-H), NutriVisRAG, OmniFood8K, Teng et al. (2027), and Nutrition5k.");
}

// Write the presentation file
pptx.writeFile({ fileName: OUT }).then(() => {
  console.log(`WROTE ${OUT}`);
  fs.copyFileSync(OUT, OUT_COPY);
  console.log(`COPIED TO ${OUT_COPY}`);
}).catch(err => {
  console.error("Error writing pptx:", err);
  process.exit(1);
});
