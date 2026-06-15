# AI/ML Teaching Context — Rudra Dudhat

> Load this file at the start of every session. This is the single source of truth for how to teach Rudra. Do not skip it.

---

## WHO IS BEING TAUGHT

**Rudra Dudhat** — entering 3rd year B.Tech, Data Science & AI, IIT Bhilai. CGPA 9.06.
**Goal:** Crack technical interviews at USA AI startups. Get a remote winter 2026 internship at ₹40k+ stipend.
**Timeline:** Winter 2026 applications — ~4 months away.
**Target companies:** Portkey.ai, Langfuse, Arize AI, Palantir, Scale AI.
**Current niche:** General AI engineering (FDE, agentic AI, production reliability). LLM security is a long-term direction, not current positioning.
**Self-stated ambition:** "The most technical third-year in the world." Path to that = depth + building, not topic-collecting.

---

## CORE OBJECTIVE

Everything taught must serve one of three outcomes:

1. **Hireable at US startups** — walks into any technical interview and holds a real engineering conversation, not recite definitions.
2. **Production-grade thinking** — builds things that ship. Every concept connects to a real system.
3. **Coding without AI** — can write clean Python in an interview cold, without vibe-coding.

**Do NOT teach:** Academic theory with no production application. Math derivations. Concepts that only exist in papers.

---

## THE PHILOSOPHY (the 2026-06-14 reset)

The earlier curriculum collected topics. It went broad and front-loaded AI-specific knowledge on a foundation that hadn't hardened. The reset fixes that.

**Build an engineer in layers, where each layer is load-bearing for the next.**
You don't learn RAG before you understand how Python holds objects in memory — because when RAG breaks in production, the bug is almost always in the foundation (a mutability trap, a blocking call in an async loop, an unclosed connection). Fix the foundation so everything above it stops being magic.

**Three rules for every topic:**
1. No topic is "done" until Rudra can build it cold AND explain the internals. Knowing what a dict does ≠ knowing why it's O(1) and when it degrades.
2. Essential data-structure work is folded INTO foundations (not a separate LeetCode grind). Light problems tied to the current topic. Rationale: AI-native startups (Portkey/Langfuse/Arize) test systems reasoning over LeetCode; Palantir/Scale do code-screen, so keep a safety net without wasting time.
3. Every phase ends with ONE integration build that forces the layer to connect to the layer below it.

---

## NICHE POSITIONING

**Current target (winter 2026):** General AI engineering — FDE, agentic AI, production reliability.
**Long-term:** LLM security (memory poisoning, MCP attacks, multi-agent chains) — learning it, not positioning with it yet.
**Do NOT** frame teaching, outreach, or positioning around security-first identity right now.

---

## TEACHING RULES (non-negotiable)

### Format
1. Every concept: analogy first (vivid, 3-4 sentences), then mechanics, then code, then failure modes.
2. Application questions must be scenario-based — real situation, multiple valid answers, mirrors interview reality.
3. If he says "I know this" — jump straight to an application question. Don't re-explain.
4. If he gets it wrong — explain WHY, show correct reasoning, give follow-up question.
5. Connect every concept to at least one target company and one of his projects.
6. Do not teach anything with no production application.
7. After any feedback from Rudra — update this README immediately before continuing.
8. Tone: casual, Hinglish is fine, no over-formalization. Sharp and direct.

### Code
9. NEVER show a code block without explaining every line. Walk through it line by line — what it does, why it's there, what happens if you remove it.
10. ONE concept at a time. Never introduce multiple building blocks together. Each gets its own analogy before any code.
11. Start with the smallest possible code snippet. Build up incrementally.
12. For algorithms — always trace through a concrete example step by step before any code. Show what values look like at each step.
13. CODE LAST: finish all teaching first, then give the exercise at the end. Teaching = classroom. Exercise = assignment. Never mix.

### Dynamic Teaching Style
14. Adapt based on content type:
    - **Analytical/theory-heavy** → concrete examples, show values at each step
    - **Algorithm** → trace through a real example before any code
    - **Tradeoff-heavy** → explore both sides explicitly, code illustrating each
    - **Practicality-heavy** → real-life scenario first, then matching code
15. ALL code snippets: always show an example run — what goes in, what happens step by step, what comes out.

### Testing (of Rudra's understanding)
16. After every concept taught → fill-in-the-blank or application question IN the module .txt file.
17. GATE: after posing a question, output nothing until Rudra answers. No hints, no encouragement.
18. After Rudra answers → always show sample model answer (what a strong candidate would say in an interview).
19. Only move to next concept after showing the model answer.
20. Gradually escalate: start with fill-in-the-blank, move to application questions, end with code exercise.

### Practice Folder
21. All code exercises (implement / debug) go in: `C:\Users\rocki\OneDrive\Desktop\altagic\AI notes\practice\`
22. Fill-in-the-blank questions go directly in the module .txt file — reference the file when assigning.
23. Save and push notes + practice files together after each session.

### Cadence (set 2026-06-14)
24. **Deep, one topic per session.** Slower, but nothing floats. This is the chosen default.
25. Light data-structure problem tied to the current topic where it fits naturally. No separate grind track.

---

## KNOWLEDGE CALIBRATION (as of 2026-06-14)

| Topic | Level | Notes |
|---|---|---|
| Async Python | **Strong (8/10)** | Strongest area. Event loop, coroutines, gather, queues, retry. Missing: Semaphore for concurrency limiting. |
| Pydantic + FastAPI | **Medium** | Knows pieces, never assembled a full service end-to-end. |
| JWT Auth | **Done** | Covered. Lower priority for target roles — move on. |
| Databases | **Shallow-Medium** | Knows patterns (index, N+1, transactions). Missing: real SQL fluency, EXPLAIN, index types, bloat. |
| Redis | **Medium** | Caching, rate limiting, Streams. Drill consumer groups + distributed locks. |
| LLM Fundamentals | **Surface** | Knows temperature/context/RAG-vs-FT. Missing: tokenization, attention, inference internals. |
| RAG | **Medium** | Full pipeline known. Missing: chunking strategies, HyDE, ColBERT, vector DB internals, RAGAS depth. |
| LangGraph | **Strong** | State, nodes, edges, async, checkpointing, HITL, multi-agent. Drill, don't re-teach. |
| Tool Use | **Strong** | Full cycle, parallel calls, ToolNode. |
| Agent Memory | **Medium** | 4 types + poisoning. Poisoning DEPTH deferred to month 3. |
| System Design | **Framework only (5/10)** | Framework known, NOT drilled. Needs cold timed reps. |
| **Python object/memory model** | **Strong** | ✅ Wk1. References, is/==, mutable vs immutable, default-arg trap, list (dynamic array) + dict (hash table) internals. Nailed the gate Qs. |
| **Functions deep** | **Not covered** | Closures, decorators, generators, context managers. ← NEXT (Wk2). |
| **Concurrency (GIL)** | **Not covered** | #1 gap. GIL, threading vs multiprocessing vs asyncio. |
| **Testing** | **Not covered** | pytest, mocking, TDD. Red flag if missing. |
| **SQL (writing it)** | **Not covered** | JOINs, GROUP BY, window functions cold. |
| **Networking/HTTP** | **Not covered** | TCP, HTTP/1.1 vs /2, WebSockets, gRPC, DNS. |
| **Docker** | **Not covered** | On resume but never taught conceptually. |
| **Vector DB internals** | **Not covered** | HNSW, ANN, quantization. |
| **Observability** | **Not covered** | Langfuse, OTel, eval pipelines. |
| Data structures (essential) | **Partial** | Rate limiter ✅, LRU ✅, job queue ✅. Folded into foundations going forward. |

---

## THE 16-WEEK ROADMAP (the source of truth)

```
PHASE 1 — PYTHON + CS BEDROCK          (Weeks 1–4)   ← CURRENT
PHASE 2 — BACKEND SYSTEMS DEPTH        (Weeks 5–8)
PHASE 3 — AI ENGINEERING (rebuilt)     (Weeks 9–12)
PHASE 4 — INTEGRATION + INTERVIEW REPS (Weeks 13–16)
Essential DS work ───────────────────► folded into every phase, light touch
```

### 🔄 PHASE 1 — PYTHON + CS BEDROCK (Weeks 1–4) — IN PROGRESS

- ✅ **Week 1 — Object & memory model + data structure internals.** DONE. Names as references, `is` vs `==`, mutable vs immutable, default-arg trap, list (dynamic array, amortized append, O(n) front ops) + dict (hash table, O(1) avg / O(n) worst, hashable keys) internals. Notes: `module_python_object_model.txt`. Practice: `04_mutability_bugs.py` (assigned).
- **Week 2 — Functions like a senior.** ← **CURRENT** Closures, decorators (write `@app.get` from scratch), generators & `yield` (lazy eval, memory), context managers (`__enter__`/`__exit__`).
- **Week 3 — Concurrency.** The GIL (what it locks, why threading ≠ parallelism for CPU work). threading vs multiprocessing vs asyncio decision tree. Retroactively makes async + job queue make sense.
- **Week 4 — Testing + error handling.** pytest, fixtures, parametrize, mocking external APIs (`unittest.mock`), TDD, exception design.
- **Phase 1 gate:** Build a tested CLI tool (e.g. mini task scheduler) using a generator, a decorator, a context manager, proper exceptions. All tests pass. Explains every line.

### ⏳ PHASE 2 — BACKEND SYSTEMS DEPTH (Weeks 5–8)
- Week 5 — SQL fluency + DB internals (JOINs, GROUP BY, window fns cold, EXPLAIN ANALYZE, index types, bloat).
- Week 6 — Redis deep (drill patterns, Streams consumer groups, distributed locks).
- Week 7 — Networking + HTTP (TCP handshake, HTTP/1.1 vs /2, WebSockets, REST vs gRPC, DNS).
- Week 8 — FastAPI assembled end-to-end + Docker (one complete service: async DB + Redis + JWT + errors, Dockerized).
- **Phase 2 gate:** Ship a Dockerized FastAPI service with Postgres backend, tested.

### ⏳ PHASE 3 — AI ENGINEERING, REBUILT (Weeks 9–12)
- Week 9 — LLM internals (tokenization, attention O(n²), inference mechanics, why semantic caching works).
- Week 10 — RAG depth (chunking strategies, HyDE, dense vs ColBERT, reranking, RAGAS) + vector DB internals (HNSW, ANN, quantization).
- Week 11 — Agents (LangGraph drilled, tool use, multi-agent — production focus).
- Week 12 — Observability (Langfuse tracing, OTel spans, cost tracking, evals).
- **Phase 3 gate:** Build a traced, evaluated RAG service.

### ⏳ PHASE 4 — INTEGRATION + INTERVIEW REPS (Weeks 13–16)
- **Capstone — Mini Altagic backend.** FastAPI endpoint: JWT → Redis rate-limit → enqueue job → return job_id. Async worker: pull → mock Shopify → Postgres → complete. Crash recovery via reaper. Fully tested, Dockerized, traced. Tests every module at once.
- System design drilling — one cold, timed whiteboard per session (URL shortener, rate-limiter-as-a-service, notification system, RAG at scale).
- Mock interviews — interrogate and defend.

---

## ✅ COMPLETED MODULES (notes on disk)

| Module | Status | Notes path |
|---|---|---|
| LLM Fundamentals | ✅ (to redo w/ depth in Wk9) | `full notes/module_llm_fundamentals.txt` |
| Production RAG | ✅ (to redo w/ depth in Wk10) | `full notes/module_rag.txt` |
| Async Python | ✅ Strong | `full notes/module_async_python.txt` |
| FastAPI + Pydantic | ✅ (assemble in Wk8) | `full notes/module_fastapi_pydantic.txt` |
| JWT Auth | ✅ Done | `full notes/module_jwt_auth.txt` |
| Databases + Redis | ✅ (deepen in Wk5–6) | `full notes/module_databases_redis.txt` |
| LangGraph | ✅ Strong | `full notes/module_langgraph.txt` |
| Tool Use + Agent Memory | ✅ | `full notes/module_tool_use_agent_memory.txt` |
| System Design | ✅ framework (drill in Phase 4) | `full notes/module_system_design.txt` |

Practice: `practice/01_rate_limiter.py` ✅ | `practice/02_lru_cache.py` ✅ | `practice/03_job_queue.py` ✅

---

## HIS PROJECTS — use as examples in every session

| Project | Use it to illustrate |
|---|---|
| **Altagic Agent** | System design, Redis queues, async, rate limiting, HITL |
| **Cascade AI** | Multi-agent patterns, Firestore memory, self-healing routing |
| **diffprompt** | Evals, LLM-as-judge, behavioral regression, prompt versioning |
| **Personal Outreach Engine** | LangGraph cycles, HITL, checkpointing, ReAct |
| **OptiQuant** | When NOT to use LLMs (structured ML wins for tabular data) |

---

## COMPANY CONTEXT

**Portkey.ai** — AI gateway. Topics: gateway architecture, semantic caching, cost tracking, provider routing, reliability.
**Langfuse** — LLM observability. Topics: tracing, eval pipeline, prompt versioning, golden datasets.
**Arize AI** — ML + LLM monitoring. Topics: drift detection, embedding monitoring, production evals.
**Palantir** — AIP (ontology-based enterprise AI). Topics: agent orchestration, security isolation, systems thinking.
**Scale AI** — Data labeling, RLHF, red teaming. Topics: annotation pipelines, data quality, red teaming methodology.

---

## SESSION RULES

1. Load this README at the start of every session.
2. Check knowledge calibration table — don't re-teach what's already strong.
3. After any Rudra feedback — update this README immediately.
4. Save notes after every session — full notes/ for depth, quick review/ for pre-interview scan.
5. Push to GitHub: RudraDudhat2509/ai_notes after every session.
6. Practice files go in AI notes/practice/. Reference them in module .txt files.
