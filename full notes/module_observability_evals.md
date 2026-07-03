# Observability & Evals

AI/ML Study Notes — Rudra Dudhat
Date: 2026-07-04

---

## 1. Why Observability Exists

You deploy a service. It's running — no crashes, server's up. Then either a
user says "it's slow," or worse, nobody says anything and your metrics just
quietly get worse.

You look at the server. It's fine on the surface. But something is wrong
underneath.

This is the exact problem observability solves: **you need to understand what
your system is doing from the outside, without directly inspecting its
internals in real time.**

The term comes from control theory — a system is "observable" if you can
determine its internal state purely from its outputs. Applied to software:
can you figure out *why* your system behaved a certain way, just from the data
it emits, without SSHing in and guessing?

If your answer is "I'd have to log into the box and grep files" — your system
isn't observable.

---

## 2. The Three Pillars

Not just "three types of data." Each one answers a fundamentally different
question.

### Metrics — "What's happening right now, in numbers?"

A metric is a number measured over time. CPU at 73%. 4,200 requests/sec.
Error rate 0.8%. p99 latency 340ms.

Metrics are cheap because you don't store every data point — you store
aggregates (avg, p50, p99, count) over a time window.

- **Good for:** alerting and dashboards. "If error rate > 5% for 3 minutes →
  page someone."
- **Bad for:** telling you *why*. Error rate is 5% — which errors, which
  users, which code path? Metrics don't know.

### Logs — "What exactly happened, at this moment?"

A timestamped record of one event, usually structured JSON:

```json
{"time": "14:32:01", "level": "ERROR", "user_id": 42, "msg": "payment failed", "reason": "card_declined"}
```

Logs are expensive — every event writes a line, and at scale that's millions
of lines/minute to store and search.

- **Good for:** debugging one specific incident — search by timestamp +
  user_id, find exactly what happened.
- **Bad for:** following one request across 5 microservices. You'd have to
  manually correlate logs across services by timestamp. Painful.

### Traces — "How did this one request travel through my system?"

A trace records one request's full journey across every service it touched,
with timing per step.

User hits "buy now":
1. API gateway (2ms)
2. Auth service (8ms)
3. Order service (45ms)
   - calls Inventory (12ms)
   - calls Payment (280ms) ← the actual problem
   - writes to DB (5ms)

Without traces: you see p99 latency = 340ms, no idea which part is slow.
With traces: you see the full waterfall — Payment took 280ms because Stripe
was slow that day.

Each individual step (API gateway's piece, Order service's piece) is called a
**span**. All spans from one request share a **trace ID**, which is how
they're linked together into that waterfall view.

- **Good for:** latency diagnosis in distributed systems.
- **Bad for:** trends and aggregates — that's what metrics are for.

### The Mental Model

| Pillar  | Question it answers      | Good for                       | Bad for                        |
|---------|---------------------------|----------------------------------|---------------------------------|
| Metrics | Is something wrong?      | Alerting, dashboards           | Knowing why                    |
| Logs    | What exactly happened?   | Debugging one incident         | Cross-service request flow     |
| Traces  | Where did the time go?   | Latency diagnosis, distributed | Trends/aggregates              |

You need all three because they answer different questions. A system with
only logs and no traces is half-blind in distributed setups. A system with
only metrics can tell you *that* something broke, never *what*.

---

## 3. Microservices — The Prerequisite

### What a service is

A service is just a **running process that listens on a port and responds to
requests.** A FastAPI app running on `uvicorn main:app --port 8000` is a
service.

### Monolith first

Before microservices, everything ran as one process — a **monolith**. One
codebase, one deployment, e.g. `users.py`, `products.py`, `orders.py`,
`payments.py` all imported into one `main.py`.

Fine at small scale. Problems appear at scale:
- A bug in payments crashes the *entire* app — unrelated features go down too.
- Deploying a notifications fix requires redeploying everything.
- Product catalog gets 100× the traffic of payments, but they're the same
  process — can't scale independently.
- Can't use a different language/stack for one piece.

### What a microservice actually is

Pull one piece out of the monolith, make it its own process with its own
port and its own database:

```
users-service/     → port 8001
products-service/  → port 8002
orders-service/    → port 8003
payments-service/  → port 8004
```

Now payments crashing doesn't take down products. Deploying notifications
only redeploys notifications. Scale product-service to 20 instances while
payments stays at 2.

### Services talking to each other

```python
# users_service/main.py  (port 8001)
from fastapi import FastAPI, HTTPException
app = FastAPI()
fake_users_db = {1: {"id": 1, "name": "Rudra", "email": "rudra@altagic.com"}}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = fake_users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

```python
# orders_service/main.py  (port 8002)
from fastapi import FastAPI, HTTPException
import httpx
app = FastAPI()
fake_orders_db = {99: {"id": 99, "user_id": 1, "product": "Laptop", "amount": 80000}}

@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    order = fake_orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:8001/users/{order['user_id']}")
        user = response.json()
    return {**order, "placed_by": user["name"], "email": user["email"]}
```

Two separate processes, two ports, talking over plain HTTP. That's
microservices.

### The new problems distribution introduces

In a monolith: `user = get_user(42)` is a function call. Never fails (barring
a bug), takes nanoseconds.

In microservices: `await client.get("http://users-service/users/42")` is now
a **network call** — can fail with timeouts, 503s, slow responses. This is
exactly why reliability patterns (circuit breakers, retries, timeouts — see
SD-07 notes) exist.

### Why this matters for observability

One user request to `GET /orders/99` now touches 3 separate processes with 3
separate log files, possibly on 3 separate machines. Metrics alone can't tell
you which one is slow. Logs alone require manual correlation across files.

This is exactly why **traces** exist — they attach one trace ID to the
request at the entrypoint and pass it through every downstream call, so all
logs and timings link back into one waterfall.

---

## 4. Context Propagation — How Trace IDs Actually Travel

### The core idea

Services share no memory. The only thing connecting them is the HTTP request
itself. So: **put the trace ID in the HTTP header.**

- **Trace ID** — identifies the entire request journey end-to-end. Same value
  across every service.
- **Span ID** — identifies *this specific service's* piece of work. Each
  service generates its own.

```
Gateway:        trace_id=abc123  span_id=span_001
  → calls Orders:  trace_id=abc123  parent_span_id=span_001  span_id=span_002
      → calls Users: trace_id=abc123  parent_span_id=span_002  span_id=span_003
```

The span tree (`span_001 → span_002 → span_003`) is what a tracing tool
renders as a waterfall diagram, all linked by `trace_id=abc123`.

### W3C Trace Context — the actual header

Industry standard used by OpenTelemetry, one HTTP header:

```
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
             ^   ^                                  ^                 ^
          version  trace_id                    parent_span_id      flags (01=sampled)
```

### Manual implementation (to see it's not magic)

**Gateway — generates trace ID, injects header:**

```python
import uuid, httpx
from fastapi import FastAPI
app = FastAPI()

@app.get("/buy/{order_id}")
async def buy(order_id: int):
    trace_id = uuid.uuid4().hex
    span_id = uuid.uuid4().hex[:16]
    traceparent = f"00-{trace_id}-{span_id}-01"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8002/orders/{order_id}",
            headers={"traceparent": traceparent}
        )
    return response.json()
```

**Orders Service — extracts incoming trace, creates own span, re-injects:**

```python
from fastapi import FastAPI, Request
import uuid, httpx
app = FastAPI()

@app.get("/orders/{order_id}")
async def get_order(order_id: int, request: Request):
    incoming = request.headers.get("traceparent", "")
    trace_id = incoming.split("-")[1] if len(incoming.split("-")) >= 2 else uuid.uuid4().hex
    our_span_id = uuid.uuid4().hex[:16]
    outgoing = f"00-{trace_id}-{our_span_id}-01"

    print(f"[SPAN] service=orders trace={trace_id} span={our_span_id}")

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            "http://localhost:8001/users/1",
            headers={"traceparent": outgoing}
        )
    return {"order_id": order_id, "user": user_response.json()}
```

Same `trace_id`, different `span_id`s per service — this is exactly how a
tracing backend groups spans into one waterfall.

### OpenTelemetry automates this

Manually extracting/injecting `traceparent` on every HTTP call is what every
team used to hand-write. OpenTelemetry (OTel) is the standard SDK that:

1. **Auto-instruments** HTTP clients/servers — inject/extract happens
   automatically.
2. **Standardises the data format** so any backend (Jaeger, Langfuse,
   Datadog, Honeycomb) can consume the spans.
3. **Provides a Collector** — a sidecar process that receives spans from your
   app and forwards them to whatever backend you choose.

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

provider = TracerProvider()
trace.set_tracer_provider(provider)
FastAPIInstrumentor.instrument_app(app)   # auto-extracts incoming traceparent
HTTPXClientInstrumentor().instrument()    # auto-injects outgoing traceparent
```

Route code stays clean — no manual header handling anywhere:

```python
@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    async with httpx.AsyncClient() as client:
        user = await client.get("http://localhost:8001/users/1")
    return {"order_id": order_id, "user": user.json()}
```

---

## 5. Where OTel Breaks for LLMs

A normal OTel HTTP span captures: duration, URL, status code. Fine for a REST
call.

An LLM call is fundamentally richer:

```python
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    temperature=0.2,
    max_tokens=500
)
```

Auto-instrumented as a generic HTTP call, you only get duration + status
code. **Missing:** which model, prompt/completion token counts, the actual
prompt and response content, temperature, why it stopped (`finish_reason`),
and the dollar cost.

### `gen_ai.*` Semantic Conventions

The (evolving) OTel spec for LLM spans, followed loosely by Langfuse/Arize/
Portkey:

```python
{
  "name": "llm.chat",
  "gen_ai.system": "openai",
  "gen_ai.request.model": "gpt-4o",
  "gen_ai.request.temperature": 0.2,
  "gen_ai.request.max_tokens": 500,
  "gen_ai.usage.prompt_tokens": 847,
  "gen_ai.usage.completion_tokens": 312,
  "gen_ai.usage.total_tokens": 1159,
  "gen_ai.response.finish_reasons": ["stop"],
  "events": [
    {"name": "gen_ai.content.prompt",     "body": {...}},
    {"name": "gen_ai.content.completion", "body": {...}}
  ]
}
```

Content goes in **span events**, not attributes — too large/unbounded for
attributes.

### Agents make this much harder

One user message can trigger a full ReAct-style loop:

```
[root] handle_user_message          7000ms
  ├── [llm]  llm_call_1 (decide to search)     800ms
  ├── [tool] search_flights                   2100ms
  ├── [llm]  llm_call_2 (compare prices)        600ms
  ├── [tool] get_price_details                  400ms
  ├── [llm]  llm_call_3 (confirm booking)        700ms
  ├── [tool] book_flight                       1800ms
  └── [llm]  llm_call_4 (generate confirmation)  500ms
```

Without this trace tree, "it took 7 seconds" tells you nothing about which
LLM call or which tool was the bottleneck.

---

## 6. Code Review — `traced_llm_call` (Broken Version)

```python
def traced_llm_call(messages: list, model: str = "gpt-4o") -> str:
    with tracer.start_as_current_span("llm.chat") as span:
        start = time.time()
        response = client.chat.completions.create(model=model, messages=messages)
        duration = time.time() - start
        span.set_attribute("gen_ai.system", "openai")
        span.set_attribute("gen_ai.request.model", model)
        span.set_attribute("gen_ai.usage.total_tokens", response.usage.total_tokens)
        span.set_attribute("duration_ms", duration * 1000)
        return response.choices[0].message.content
```

### Bugs found

1. **No input validation** — empty `messages` list is never checked; OpenAI
   throws a cryptic API error.
2. **No model validation** — a bad model string fires the API call anyway;
   the span ends with no useful diagnostic info.
3. **No retry** — transient 429/5xx errors kill the whole call. Needs
   exponential backoff (`tenacity`/`backoff`), retrying only on 429/5xx, never
   4xx.
4. **`temperature`/`max_tokens` never passed to the API call, and never
   recorded** — the model silently runs on defaults and you don't even know
   it.
5. **`prompt_tokens`/`completion_tokens` not recorded separately** — only
   `total_tokens` is captured, so cost can't be calculated (input and output
   tokens are priced differently, e.g. gpt-4o: $2.50/1M in vs $10/1M out).
6. **No exception handling on the span** — if the API call throws, the
   exception just propagates; the span exits with status `UNSET`, not
   `ERROR`. Looks like a successful-but-empty span in the dashboard.
7. **Prompt/response content never captured** — token counts are recorded but
   the actual content is thrown away, so you can't debug *why* an answer was
   bad or feed it into an eval later.
8. **Manual timing is redundant and non-standard** — OTel already times the
   span automatically (start of `with` block to end). The custom
   `duration_ms` attribute duplicates this and isn't a standard field
   tracing backends recognize.

### Fixed version

```python
import tenacity
from opentelemetry import trace

VALID_MODELS = {"gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"}

@tenacity.retry(
    wait=tenacity.wait_exponential(multiplier=1, min=1, max=10),
    stop=tenacity.stop_after_attempt(3),
    reraise=True
)
def _call_openai(model, messages, temperature, max_tokens):
    return client.chat.completions.create(
        model=model, messages=messages,
        temperature=temperature, max_tokens=max_tokens
    )

def traced_llm_call(messages: list, model: str = "gpt-4o",
                     temperature: float = 0.2, max_tokens: int = 500) -> str:
    if not messages:
        raise ValueError("messages cannot be empty")
    if model not in VALID_MODELS:
        raise ValueError(f"Unknown model '{model}'. Valid: {VALID_MODELS}")

    with tracer.start_as_current_span("gen_ai.chat") as span:
        span.set_attribute("gen_ai.system", "openai")
        span.set_attribute("gen_ai.request.model", model)
        span.set_attribute("gen_ai.request.temperature", temperature)
        span.set_attribute("gen_ai.request.max_tokens", max_tokens)
        span.add_event("gen_ai.content.prompt", {"content": str(messages)})

        try:
            response = _call_openai(model, messages, temperature, max_tokens)
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.StatusCode.ERROR, str(e))
            raise

        span.set_attribute("gen_ai.usage.prompt_tokens", response.usage.prompt_tokens)
        span.set_attribute("gen_ai.usage.completion_tokens", response.usage.completion_tokens)
        span.set_attribute("gen_ai.usage.total_tokens", response.usage.total_tokens)
        span.set_attribute("gen_ai.response.finish_reason", response.choices[0].finish_reason)

        content = response.choices[0].message.content
        span.add_event("gen_ai.content.completion", {"content": content})
        span.set_status(trace.StatusCode.OK)
        return content
```

### The pattern to internalize

```
validate inputs                      (before span — no point tracing invalid calls)
open span
  record what you're SENDING         (request attributes)
  try:
    make the call
  except:
    record exception + set ERROR status
    re-raise
  record what you GOT BACK           (response attributes)
  set OK status
return result
```

This is exactly what Langfuse's SDK, Portkey's proxy, and Arize Phoenix
implement under the hood for every LLM call they trace.

---

## 7. Code Review — `run_eval_suite` (Broken Version)

Conceptual version reviewed: a function that loops over `test_cases`, calls
an LLM to generate, calls a second LLM as judge, averages scores, and
compares to a hardcoded `0.8` threshold.

### Bugs found

1. **No test case schema validation** — missing keys crash mid-suite with a
   raw `KeyError`. Should validate upfront:
   ```python
   required_keys = {"input", "expected"}
   for i, case in enumerate(test_cases):
       if not required_keys.issubset(case.keys()):
           raise ValueError(f"Test case {i} missing keys: {required_keys - case.keys()}")
   ```
2. **No observability inside the suite** — no logging, so a failure gives you
   zero visibility into which case broke or why.
3. **No retry configured** — one transient API error kills the whole suite
   run.
4. **No per-case isolation** — one case's exception propagates and aborts all
   remaining cases. Every case needs its own try/except so the suite reports
   partial results instead of crashing.
5. **Division by zero** — `avg_score = sum(results) / len(results)` crashes
   if every case failed and `results` is empty. Guard: return `None`/failure
   marker instead.
6. **Hardcoded `0.8` threshold** — no documentation of where the number came
   from; should be configurable and derived from a baseline run against
   human-labelled data.
7. **Loose judge prompt with no output contract** — prompt says "return a
   float between 0 and 1" but the model may return prose like "I'd say
   about 0.8," which crashes a bare `float()` parse. Needs enforced JSON
   output + a negative constraint ("respond with ONLY valid JSON, no other
   text").
8. **Judge model weaker than generator model** — e.g. generating with
   `gpt-4o`, judging with `gpt-3.5-turbo`. A weaker model can't reliably
   evaluate a stronger model's output. Use an equal-or-stronger judge, ideally
   from a **different model family** to avoid self-preference bias.
9. **No semantic pre-check before the expensive LLM judge** — cases with an
   obvious cosine-similarity match/mismatch don't need a full LLM judge call;
   only the ambiguous middle range does. Saves cost and latency.
10. **Reference-based eval used for open-ended questions** — comparing actual
    output to one fixed "expected" string only works for single-right-answer
    factual questions (`2+2=4`). For open-ended questions (e.g. "summarise
    quantum computing"), a perfect answer with different wording scores
    low. Needs a **rubric-based judge** instead: "does this answer meet these
    criteria?" not "is this similar to expected?"
11. **Sequential API calls — O(n) latency** — 100 cases × 1.5s each = 2.5
    minutes. Should run concurrently via `asyncio.gather`.

### Fixed version

```python
import json, asyncio, logging
from openai import AsyncOpenAI
import tenacity

logger = logging.getLogger("eval-suite")
client = AsyncOpenAI()

def validate_test_cases(test_cases: list[dict]):
    if not test_cases:
        raise ValueError("test_cases is empty")
    for i, case in enumerate(test_cases):
        missing = {"input", "expected"} - case.keys()
        if missing:
            raise ValueError(f"Case {i} missing: {missing}")

@tenacity.retry(wait=tenacity.wait_exponential(min=1, max=8),
                stop=tenacity.stop_after_attempt(3), reraise=True)
async def generate(prompt: str) -> str:
    r = await client.chat.completions.create(
        model="gpt-4o", messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content

@tenacity.retry(wait=tenacity.wait_exponential(min=1, max=8),
                stop=tenacity.stop_after_attempt(3), reraise=True)
async def judge(question: str, answer: str, criteria: str) -> float:
    prompt = f"""You are an expert evaluator. Score the answer strictly on:
{criteria}

Question: {question}
Answer: {answer}

Respond with ONLY valid JSON: {{"score": <float 0.0-1.0>, "reasoning": "<one sentence>"}}
Do not include any other text."""

    r = await client.chat.completions.create(
        model="claude-sonnet-4-6",   # different family than generator = no self-preference bias
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    try:
        data = json.loads(r.choices[0].message.content)
        return float(data["score"])
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.error(f"Judge parse failed: {e} | raw: {r.choices[0].message.content}")
        return 0.0

async def evaluate_case(case: dict) -> dict:
    try:
        output = await generate(case["input"])
        if case.get("type") == "factual":
            if output.strip().lower() == case["expected"].strip().lower():
                return {"case": case["input"], "score": 1.0, "method": "exact_match"}
            criteria = f"Does the answer match the expected answer: '{case['expected']}'?"
        else:
            criteria = "Is the answer accurate, complete, and clearly written?"
        score = await judge(case["input"], output, criteria)
        logger.info(f"Case scored {score:.2f}: {case['input'][:50]}")
        return {"case": case["input"], "score": score, "output": output, "method": "llm_judge"}
    except Exception as e:
        logger.error(f"Case failed: {case['input'][:50]} | {e}")
        return {"case": case["input"], "score": None, "error": str(e)}

async def run_eval_suite(test_cases: list[dict], pass_threshold: float = 0.75) -> dict:
    validate_test_cases(test_cases)
    results = await asyncio.gather(*[evaluate_case(c) for c in test_cases])
    scored = [r["score"] for r in results if r["score"] is not None]
    failed = [r for r in results if r["score"] is None]

    if not scored:
        return {"avg_score": None, "passed": False, "error": "all cases failed", "details": results}

    avg = sum(scored) / len(scored)
    logger.info(f"Suite complete: avg={avg:.2f}, failed={len(failed)}/{len(test_cases)}")
    return {
        "avg_score": round(avg, 3), "passed": avg >= pass_threshold,
        "pass_threshold": pass_threshold, "n_scored": len(scored),
        "n_failed": len(failed), "details": results
    }
```

### The pattern to internalize

```
validate inputs
run cases concurrently (not serially)
isolate failures per case (one bad case ≠ suite abort)
deterministic check first (cheap gate — exact match, regex)
LLM judge only for the ambiguous middle
judge model ≠ generator model (different family preferred)
structured judge output (JSON, not raw float)
configurable threshold (not hardcoded)
log everything
```

This is what RAGAS, DeepEval, and Braintrust implement under the hood.

---

## 8. Eval Pipelines in CI/CD

### Offline vs online evals

| | Offline | Online |
|---|---|---|
| When | Pre-deploy | Post-deploy |
| Data | Curated test set | Real user traffic |
| Catches | Regressions on known cases | Distribution shift, unimagined edge cases |
| Latency | Doesn't affect users | Must run async — can't slow the response |
| Cost | You control it | Proportional to traffic |

You need both. Offline catches obvious regressions. Online catches the cases
your test set never covered — which is most of production traffic.

### The regression problem

Scenario: a prompt for summarising support tickets gets tweaked from "Be
concise" to "Be thorough and detailed." No eval run — team eyeballs 3
examples, looks fine, ships it.

Result: summaries balloon 4× in length. A downstream parser that extracts
ticket category from sentence 1 now breaks because the category is buried in
paragraph 3. Support gets flooded with misrouted tickets. Two days lost
tracing it back to one prompt line.

**Root cause: no automated check that the prompt's *behaviour* changed.**
This is prompt regression — exactly as damaging as code regression, and most
teams have zero testing for it.

### CI/CD pipeline (GitHub Actions)

```yaml
# .github/workflows/eval.yml
name: Prompt Regression Eval
on:
  pull_request:
    paths:
      - 'prompts/**'
      - 'src/llm/**'
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run eval suite
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: python -m pytest evals/ -v --tb=short
      - name: Comment results on PR
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const results = JSON.parse(fs.readFileSync('eval_results.json'));
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              body: `## Eval Results\nScore: ${results.avg_score} (threshold: ${results.threshold})\n${results.passed ? '✅ Passed' : '❌ Failed — do not merge'}`
            });
```

```python
# evals/test_summarisation.py
import pytest, json
from pathlib import Path
from your_app.llm import summarise_ticket

GOLDEN_DATASET = json.loads(Path("evals/datasets/summarisation_v3.json").read_text())

@pytest.mark.asyncio
async def test_summarisation_quality():
    results = await run_eval_suite(GOLDEN_DATASET, pass_threshold=0.80)
    Path("eval_results.json").write_text(json.dumps({
        "avg_score": results["avg_score"], "threshold": 0.80,
        "passed": results["passed"], "n_cases": len(GOLDEN_DATASET)
    }))
    assert results["passed"], f"Eval failed: avg_score={results['avg_score']:.3f} < 0.80"

@pytest.mark.asyncio
async def test_output_is_always_under_100_words():
    """deterministic gate — runs first, cheap"""
    for case in GOLDEN_DATASET:
        output = await summarise_ticket(case["input"])
        assert len(output.split()) <= 100, f"Too long for: {case['input'][:50]}"
```

### Dataset management — keeping it fresh

Golden datasets go stale by design — new product features mean new traffic
patterns not represented in a dataset written months earlier. Two failure
modes result: evals pass while prod is broken (new case types uncovered), or
eval score drops on old cases that are no longer representative.

**Fix — harvest real production failures into the dataset:**

```python
async def harvest_eval_cases_from_prod(n: int = 20):
    """
    Pull recent prod traces from Langfuse.
    Filter for thumbs-down (explicit signal) or LLM-judge score < 0.6 (implicit).
    Append to the eval dataset for the next CI run.
    """
    langfuse = Langfuse()
    bad_traces = langfuse.fetch_traces(tags=["thumbs_down"], limit=n // 2)
    low_scored = langfuse.fetch_traces(filter={"score_lt": 0.6, "score_name": "quality"}, limit=n // 2)

    new_cases = [{
        "input": t.input, "expected": None, "type": "open_ended",
        "source": "prod_harvest", "harvested_at": t.timestamp
    } for t in bad_traces + low_scored]

    existing = json.loads(Path("evals/datasets/summarisation_v3.json").read_text())
    merged = deduplicate(existing + new_cases)
    Path("evals/datasets/summarisation_v3.json").write_text(json.dumps(merged, indent=2))
```

**The flywheel:** prod traffic surfaces edge cases → harvested into dataset →
CI catches them next time → prod quality improves → repeat.

### Where diffprompt fits

The eval pipeline above catches *quality regression* (score drops).
`diffprompt` catches *behavioural divergence* — the output distribution
shifted even when quality *looks* the same on the eval score.

Example: a prompt change yields equally high-quality answers but in a
different format. Eval score: still 0.85 (passes). Downstream parser breaks
anyway because it depended on the old format. `diffprompt` would flag the
distribution shift even though the quality gate passed.

```
PR opened → prompt changed
  → diffprompt: "did output distribution change?" → flag for human review
  → eval suite: "did quality drop?" → hard block on merge
```

diffprompt = early warning. Evals = hard gate. They're complementary, not
redundant.

### Online evals in production

Score every response without blocking the user response:

```python
@app.post("/summarise")
async def summarise(request: SummariseRequest):
    output = await summarise_ticket(request.ticket)
    background_tasks.add_task(score_in_background, request.ticket, output)
    return {"summary": output}   # user gets this immediately

async def score_in_background(input: str, output: str):
    score = await judge(input, output, criteria="Is this summary accurate and concise?")
    langfuse.score(trace_id=current_trace_id(), name="quality", value=score)
    await check_rolling_alert(score)

async def check_rolling_alert(score: float):
    recent = await redis.lrange("recent_scores", 0, 9)
    await redis.lpush("recent_scores", score)
    await redis.ltrim("recent_scores", 0, 9)
    if len(recent) == 10:
        avg = sum(float(s) for s in recent) / 10
        if avg < 0.65:
            await alert_slack(f"⚠️ Quality degraded: rolling avg = {avg:.2f}")
```

### The full observability + eval loop

```
Dev changes prompt
  → PR opened → GitHub Actions
      ├── diffprompt: output distribution shifted? (warn)
      └── eval suite: quality dropped? (block if yes)
  → Merged + deployed
      → Every prod request traced in Langfuse
      → Background eval scores each response
      → Rolling window alert if quality drops
      → Bad responses harvested into eval dataset weekly
      → Next PR gets a better dataset → tighter CI gate
```

---

## 9. Worked Example — Instrumenting a Real Agent

A realistic 5-step customer support agent used as the running example for
hands-on instrumentation practice (fictional store, but the shape matches
production agents):

```
handle_ticket(ticket, order_id)
  1. classify_ticket(ticket)              → category (RETURN/SHIPPING/PRODUCT/COMPLAINT/OTHER)
  2. search_knowledge_base(ticket)        → relevant KB articles
  3. get_order_status(order_id)           → order lookup
  4. generate_response(...)               → draft reply
  5. self_check_response(ticket, response)→ {approved, issues, confidence}
     → if not approved: retry generate_response once, re-check
```

As written with zero instrumentation, none of these are answerable:
- How long did classify vs generate take relative to each other?
- Token/cost usage across both self-check calls?
- Did the retried response actually improve after a failed self-check?
- Was the retrieved KB article even relevant to the ticket?
- At 500 runs/day with p99 = 8s, which step is the bottleneck?

### Layer 1 — Structured logging (the floor)

Not `print()`, not raw f-strings — structured JSON that a log aggregator
(Datadog, Loki, CloudWatch) can query:

```python
import logging, json, sys

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log = {"time": self.formatTime(record), "level": record.levelname,
               "logger": record.name, "message": record.getMessage()}
        for key, val in record.__dict__.items():
            if key not in ("msg", "args", "levelname", "levelno", "pathname",
                           "filename", "module", "exc_info", "exc_text",
                           "stack_info", "lineno", "funcName", "created",
                           "msecs", "relativeCreated", "thread", "threadName",
                           "processName", "process", "message", "taskName", "name"):
                log[key] = val
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        return json.dumps(log)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger("agent")
```

Applied to one step:

```python
def classify_ticket(ticket: str) -> str:
    start = time.time()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "Classify..."}, {"role": "user", "content": ticket}]
    )
    category = response.choices[0].message.content.strip()
    logger.info("ticket_classified", extra={
        "category": category,
        "duration_ms": round((time.time() - start) * 1000),
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "model": "gpt-4o-mini"
    })
    return category
```

Result — queryable, machine-readable events:

```json
{"time": "2026-06-28 14:32:01", "level": "INFO", "logger": "agent",
 "message": "ticket_classified", "category": "SHIPPING",
 "duration_ms": 312, "prompt_tokens": 87, "completion_tokens": 3, "model": "gpt-4o-mini"}
```

Now `category = "SHIPPING" AND duration_ms > 500` is a real query.

**Open question for the next instrumentation pass:** what fields are unique
to a self-check/judge step (`self_check_response`) versus a plain generation
step (`generate_response`)? A judge step's log should capture something a
plain generation step never needs to — worth reasoning through before
building Layer 2 (tracing) and Layer 3 (evals) on top of this agent.

---

## Summary — What This Module Covers

1. Why observability exists — control theory framing, "can you explain
   behavior from outputs alone?"
2. The three pillars and which question each answers (metrics/logs/traces)
3. Microservices from first principles — monolith problems, service-to-
   service HTTP calls, the new failure modes distribution introduces
4. Context propagation — trace_id/span_id, W3C `traceparent` header, manual
   implementation, then OpenTelemetry automating it
5. Why OTel's generic HTTP span model breaks for LLM calls, and the
   `gen_ai.*` semantic conventions that fix it
6. Full code review + fix of a broken LLM tracing wrapper (8 bugs)
7. Full code review + fix of a broken eval suite (11 bugs) — including the
   reference-based-vs-rubric-based eval distinction, judge model bias, and
   semantic pre-filtering before an expensive LLM judge call
8. CI/CD eval pipelines — offline vs online evals, the prompt regression
   problem, GitHub Actions wiring, dataset harvesting from production
   traffic, where diffprompt fits relative to eval suites, background
   scoring + rolling alerts in production
9. Started hands-on instrumentation of a realistic 5-step support agent,
   Layer 1 (structured logging) — Layer 2 (full OTel tracing) and Layer 3
   (per-step evals) are next
