# The December Plan — Evals & Observability Mastery

**Owner:** Rudra Dudhat · **Created:** 2026-07-04 · **Deadline:** internship offers by December 2026
**Time budget:** 10–15 hrs/week ≈ 220–320 total hours over 21 weeks (Jul 7 → Nov 29)
**Spine:** Evals + LLM Observability. **Differentiator layer:** agent security (eval-driven red teaming).
**Safety net:** 1 practical coding rep/week (Palantir/Scale screens — practical, not LeetCode).

---

## 0. The Thesis

AI-infra companies (Langfuse, Arize, Braintrust, Portkey) and FDE roles (Palantir, Scale,
OpenAI) do NOT interview like Big Tech. Research findings (July 2026):

- FDE interviews: 3-hour continuous practical sessions, live debugging, case studies,
  system design, deep interrogation of YOUR projects. Explicitly no LeetCode.
  Sources: [Exponent FDE guide](https://www.tryexponent.com/blog/forward-deployed-engineer-interview-the-definitive-2026-guide-fde),
  [Sundeep Teki FDE guide](https://www.sundeepteki.org/advice/the-definitive-guide-to-forward-deployed-engineer-interviews-in-2026),
  [first-person FDE interview account](https://medium.com/@bagheshri/i-interviewed-for-a-forward-deployed-ai-engineer-role-heres-what-no-one-tells-you-192929a7fe45)
- Take-homes of 4–8 hours are common. The winning move is having already done harder
  versions of the take-home in public.
- These companies hire on **proof-of-work**: merged OSS PRs, shipped artifacts, public
  case studies. Rudra already has the rarest asset — merged PRs in OTel, MLflow,
  LiteLLM, Kedro ×2, Strix. The plan weaponizes that.

**The bet:** in 5 months, one person cannot become "untouchable" at everything. He CAN
become the strongest third-year in the world at ONE thing — building evaluation systems
for AI agents — with the OSS receipts to prove it. Everything below serves that.

### Timeline reality (from research, not vibes)

Langfuse/Arize/Braintrust have **no formal winter internship programs** — rolling hiring,
Langfuse is Europe-centric (mandatory Berlin weeks). The realistic December paths:

1. Indian AI startups (Lyzr warm lead, similar cos) — recruit Oct–Nov for Dec start
2. Remote gigs/trials at small US AI startups via founder outreach on OSS proof
3. FDE-track junior roles — interviewed on proof-of-work

**Therefore: proof-of-work locks by OCT 11. Outreach runs Oct 12 → Nov 15.
Interviews Nov–Dec. December is when offers land, not when prep ends.**

---

## 1. The Anti-AI-Dependence Operating System

The higher goal: think and code without AI as a crutch. These are standing rules,
enforced every week, no exceptions:

1. **Division of labor.** Claude writes and maintains all notes — clerical work is what
   AI is for; that's using AI wisely. Rudra's thinking happens where it counts: the
   no-AI reps, predict-first, and explain-it-cold. The muscle is built in the doing,
   not the transcription.
2. **No-AI reps.** One timed exercise per week written cold in the editor — Copilot off,
   no Claude tab. AI is allowed only AFTER completion, as a reviewer. The rep list lives
   in `practice/` and mirrors real screens (LRU cache, rate limiter, worker pool,
   log parser, retry decorator, trace-tree builder...).
3. **Predict-first.** Before running any code or command, state the expected output out
   loud/in writing. Wrong prediction = the learning moment, dig in.
4. **Explain-it-cold.** End of each week: 5-minute verbal explanation of the week's core
   concept, interview-style, no notes. Claude interrogates like a skeptical senior.
5. **Debugging discipline** (from README): reproduce → read traceback bottom-up → ONE
   hypothesis → test that one thing → bisect. Never guess-and-poke. State the hypothesis
   before touching code.
6. **The parking lot.** Any new project/pivot idea goes into `PARKING_LOT.md` and is
   reviewed ONLY at phase gates. (The historical failure mode is mid-plan pivots —
   SD curriculum paused, multiple project pivots. The plan survives only if pivots are
   quarantined.)

---

## 2. Phase Plan

```
PHASE 1 — LOAD-BEARING FOUNDATIONS      Wk 1–4    Jul 7  – Aug 2
PHASE 2 — EVALS + OBSERVABILITY CORE    Wk 5–10   Aug 3  – Sep 13
PHASE 3 — SECURITY LAYER + OSS SPRINT   Wk 11–14  Sep 14 – Oct 11   ← proof-of-work gate
PHASE 4 — OUTREACH + INTERVIEW REPS     Wk 15–21  Oct 12 – Nov 29
```

One project threads through everything: **the Lab Rat** — a realistic support agent
(built Wk 4, modeled on the Altagic use case) that gets instrumented, traced, error-
analyzed, judged, gated in CI, attacked, and defended. By October it is a complete,
public case study: *"I built an agent and a full evaluation system around it, here is
every failure I found and how I measured the fixes."* That artifact is the interview.

### PHASE 1 — Load-Bearing Foundations (Wk 1–4)

Only the gaps that are load-bearing for the spine. Everything else stays cut.

- **Wk 1 — Testing.** pytest, fixtures, parametrize, mocking external APIs, property-based
  thinking. Taught THROUGH the evals lens: how do you test non-deterministic LLM code?
  (This is literally Level-1 evals per Hamel — assertions ARE unit tests for AI.)
  Rep: write a test suite for an untested module, cold.
  *Also this week, one evening, off-plan: ship the Brok launch (it's ready — merge PR,
  post the X launch). Finishing it honors the no-abandoned-projects rule; developing it
  further is parked.*
- **Wk 2 — Professional debugging.** The scientific method formalized: pdb/breakpoint(),
  reading stack traces, git bisect, bisecting a bug in unfamiliar code. Reps: 2 planted-bug
  hunts in code Rudra hasn't seen (this is EXACTLY the FDE live-debug interview).
- **Wk 3 — SQL fluency.** JOINs, GROUP BY, window functions written cold; EXPLAIN ANALYZE;
  index reasoning. Framed as the eval-analysis tool: error analysis = querying trace data.
  Rep: 10 queries against a trace-log dataset, timed.
- **Wk 4 — Docker + build the Lab Rat.** Docker fundamentals (images, layers, compose),
  then assemble the support agent: FastAPI + the 5-step agent loop + Postgres + Redis,
  containerized, OTel instrumentation from day one. This is the Phase 1 gate build.

**Phase 1 gate (Aug 2):** Lab Rat runs in Docker, has tests, emits traces. Rudra explains
every line cold and passes all 4 explain-it-cold interrogations.

### PHASE 2 — Evals + Observability Core (Wk 5–10)

The spine. Methodology = Hamel Husain + Shreya Shankar's critique-shadowing process
(the field's canonical curriculum — 4,500+ engineers trained), executed on the Lab Rat
with synthetic traffic. Primary sources, all free:
[Your AI Product Needs Evals](https://hamel.dev/evals) ·
[LLM-as-a-Judge complete guide](https://hamel.dev/llm-judge/) ·
[Field Guide to Rapidly Improving AI Products](https://hamel.dev/field-guide) ·
[Evals FAQ](https://hamel.dev/blog/posts/evals-faq/) ·
[Who Validates the Validators (Shankar et al.)](https://arxiv.org/abs/2404.12272) ·
[DeepLearning.AI × Arize: Evaluating AI Agents](https://www.deeplearning.ai/courses/evaluating-ai-agents) ·
[Eugene Yan: LLM evaluators survey](https://eugeneyan.com/writing/llm-evaluators/) ·
[AlignEval](https://aligneval.com/) ·
[Arize Recipe-Bot workflow (the Maven course homework, free)](https://arize.com/blog/ai-evals-maven-course-homework-the-recipe-bot-workflow/)

- **Wk 5 — Instrumentation deep.** OTel GenAI semantic conventions, spans/context
  propagation hands-on, Langfuse AND Arize Phoenix wired to the Lab Rat (knowing both
  tools = interview currency at both companies). Generate 200+ traces of synthetic
  user traffic (personas × scenarios × features grid, per Hamel's taxonomy).
- **Wk 6 — Error analysis.** THE skill, the highest-ROI activity in AI engineering.
  Open coding on 100+ real traces (free-text notes, no preconceived categories) →
  axial coding (build the failure taxonomy from the notes) → frequency counting →
  prioritized fix list. Build the custom data viewer (FastHTML/Streamlit, built in
  hours — Hamel: "the most important AI investment"). Rudra does the annotation
  HIMSELF — this cannot be delegated to AI, that's the point.
- **Wk 7 — LLM-as-judge via critique shadowing.** Binary pass/fail + written critiques
  (never 1–5 scales). Rudra = principal domain expert. Judge prompt built from his own
  few-shot critiques. Measure judge↔human agreement properly (precision/recall when
  classes are imbalanced, not raw agreement). Iterate to >85% alignment. Run his labels
  through AlignEval as a cross-check.
- **Wk 8 — Eval infrastructure.** Golden datasets with versioning, Level-1 assertion
  gates in CI (GitHub Actions), the dataset-harvesting flywheel (prod failures → eval
  set), regression gates on prompt changes. Connect diffprompt's behavioral-divergence
  idea as the early-warning layer alongside the quality gate.
- **Wk 9 — Online evals + RAG evals.** Background scoring, rolling alerts, cost/latency
  tracking. RAGAS internals (faithfulness, context precision/recall) — implement two
  metrics from scratch before using the library, so it's never magic.
- **Wk 10 — Consolidation buffer.** Life happens; at 10–15 hrs/wk a buffer is load-bearing.
  If on schedule: write case-study part 1 and start scouting OSS issues in
  Phoenix/Langfuse/OpenLLMetry/RAGAS from real friction hit in Wk 5–9 (the best PR
  source is "this annoyed me while using it").

**Phase 2 gate (Sep 13):** Full eval system live on the Lab Rat — viewer, taxonomy,
aligned judge with agreement metrics, CI gate, online scoring. Rudra can run the whole
loop and defend every design decision cold.

### PHASE 3 — Security Layer + OSS Sprint (Wk 11–14)

The differentiator: almost nobody entering evals also speaks attack surfaces; almost no
security person builds rigorous evals. The fusion — **eval-driven red teaming, attack
success rate as a measured metric** — is Rudra's unique positioning, and his garak/Strix
history already backs it.

- **Wk 11 — Attack the Lab Rat.** Prompt injection (direct + indirect), tool poisoning,
  memory poisoning, RAG retrieval poisoning. Each attack becomes an eval case; attack
  success rate becomes a tracked metric on the same dashboard.
- **Wk 12 — Systematic probing.** garak architecture applied: build a probe/detector
  harness for the Lab Rat. Finish the in-flight garak PR (#74 tag-injection) if still open.
- **Wk 13–14 — OSS sprint + publish.** Two targeted PRs in eval/obs repos (Phoenix,
  Langfuse, OpenLLMetry, RAGAS — from the Wk 10 friction list). Publish the flagship
  case study: repo + long-form write-up + X thread. Update resume + portfolio around it.

**Phase 3 gate — PROOF-OF-WORK LOCK (Oct 11):** public case study live, 2+ new PRs
merged/open, resume rebuilt. This gate does not slip; scope shrinks instead.

### PHASE 4 — Outreach + Interview Reps (Wk 15–21)

Prep and pipeline in parallel, ~half time each.

- **Outreach (from Oct 12):** Lyzr follow-up first. Then founder/eng-lead DMs at AI-infra
  startups with the case study + PR links (use the Personal Outreach Engine — dogfooding
  is itself a story). Target: 30+ quality touches by Nov 15. Public building on X continues.
- **Weekly interview reps:**
  - 1 × mock interview with Claude in FDE format — live-debug an unfamiliar system,
    design an eval pipeline under questioning, defend the case study against attack
  - 1 × timed cold system design from the AI-infra set: LLM gateway (Portkey), tracing
    backend at scale (Langfuse), eval platform (Braintrust), agent platform with
    isolation (Palantir), rate-limiter-as-a-service, RAG at scale
  - 1 × no-AI practical rep (the Palantir/Scale net, continued)
  - Once in Wk 16–17: a full 6-hour take-home simulation, reviewed brutally
- **Story bank:** STAR write-ups for every project (Altagic, diffprompt, case study, each
  OSS PR — especially the "how I navigated the maintainer review" stories).

**Phase 4 gate = the actual goal:** offers in hand by early December.

---

## 3. The Weekly Template (10–15 hrs)

| Block | Time | What |
|---|---|---|
| Deep session ×2 | 5–6 h | Teach → Rudra builds live (Claude never writes the solution) |
| Project build | 3–5 h | Solo work on the week's Lab Rat milestone |
| No-AI rep | 1–1.5 h | Timed, cold, editor only. AI review after. |
| Notes review | 15 min | Claude writes the notes; Rudra reads + flags gaps |
| Explain-it-cold | 15 min | Verbal, interrogated |

Phase 4 swaps the deep sessions for mocks/system design.

---

## 4. Success Metrics (checked at every phase gate)

1. Can rebuild the week's artifact cold, no AI, and explain every line — sampled randomly.
2. Passes explain-it-cold every week — 5 min verbal, interrogated, no notes open.
3. Lab Rat milestones on schedule (traces → viewer → judge → CI → attacks).
4. By Oct 11: public case study + 2 new OSS PRs + rebuilt resume.
5. By Nov 15: 30+ outreach touches, ≥5 conversations.
6. By early Dec: offer(s).

## 5. Risks — named honestly

- **The #1 risk is pivoting.** History: SD curriculum paused mid-way, multiple project
  pivots. Mitigation: the parking lot + phase-gate-only reviews. New shiny idea ≠ plan change.
- **10–15 hrs/wk is thin.** Hence: one spine, one artifact, buffers, and a gate that cuts
  scope instead of slipping dates.
- **Altagic/CCPS surges.** If a week collapses, the no-AI rep and notes survive (2.5 h);
  the project milestone shifts into the buffer. Never skip the reps — they're the compound
  interest.
- **Claude-dependence during the plan itself.** The operating system in §1 is the defense;
  if Rudra notices Claude writing code he should be writing, call it out — that's a
  standing instruction.
