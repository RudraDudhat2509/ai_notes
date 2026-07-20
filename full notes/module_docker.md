# Docker

AI/ML Study Notes — Rudra Dudhat
Date: 2026-07-15

---

## 1. What Docker Actually Is — the Problem It Solves

"It works on my machine" is the single most infuriating sentence in software
engineering. You build something, it runs perfectly on your laptop, you hand
it to a teammate or deploy it to a server, and it breaks — because your
laptop secretly has Python 3.11 installed, the server has 3.9, a system
library is a different version, an environment variable you forgot about is
set locally but not remotely.

**Docker's entire reason for existing:** package your application together
with its ENTIRE environment — exact OS libraries, exact language runtime,
exact dependencies — into one shippable unit that behaves identically
everywhere it runs.

---

## 2. Image vs Container — the Core Distinction

```
IMAGE                                   CONTAINER
(frozen, read-only blueprint)            (a RUNNING instance of that blueprint)

┌─────────────────────┐                 ┌─────────────────────┐
│   python:3.12-slim   │                 │  container #1        │
│   + your deps        │   docker run    │  (isolated, running) │
│   + your code        │ ─────────────►  └─────────────────────┘
│   + startup command   │                 ┌─────────────────────┐
│  (does nothing itself)│   docker run    │  container #2        │
└─────────────────────┘ ─────────────►  │  (isolated, running) │
                                          └─────────────────────┘
```

Same relationship as a Python **class** (the image — a spec, does nothing by
itself) and **objects instantiated from it** (containers — many independent,
isolated instances from one class definition). Running `docker run myapp`
three times gives you 3 independent containers, all built from the same 1
image — changes in one container never affect another, same as three
separate objects never sharing state just because they came from the same
class.

---

## 3. Layers — Why the Dockerfile Order Matters

An image isn't one blob — it's a **stack of layers**, each a diff from the
one below it. Docker **caches** each layer.

```dockerfile
FROM python:3.12-slim          # layer 1: base OS + Python runtime
WORKDIR /app                    # layer 2: working directory
COPY requirements.txt .         # layer 3: copy JUST this file
RUN pip install -r requirements.txt   # layer 4: install deps
COPY . .                        # layer 5: copy the rest of the code
CMD ["python", "app.py"]        # layer 6: what runs when a container starts
```

**Cache diagram — code-only change:**
```
FROM python:3.12-slim     [cached — unchanged]
WORKDIR /app               [cached — unchanged]
COPY requirements.txt .    [cached — file unchanged]
RUN pip install ...        [cached — SKIPPED, huge time save]
COPY . .                   [RE-RUNS — your code changed]
CMD [...]                  [RE-RUNS — always follows changed layers]
```

**Cache diagram — `requirements.txt` changes (new dependency added):**
```
FROM python:3.12-slim     [cached]
WORKDIR /app               [cached]
COPY requirements.txt .    [RE-RUNS — file content differs → cache invalidated HERE]
RUN pip install ...        [RE-RUNS — even though the COMMAND TEXT never changed]
COPY . .                   [RE-RUNS]
CMD [...]                  [RE-RUNS]
```

**The cascading rule:** the moment ONE layer's cache invalidates, EVERY layer
built on top of it (downstream in the Dockerfile) reruns automatically —
regardless of whether that later layer's own command changed. Each layer is
built on the filesystem state of the layer before it, so a changed
foundation forces everything stacked on it to rebuild too.

**Why the order in the Dockerfile is deliberate:** copy the slow-to-rebuild,
rarely-changing thing (`requirements.txt` → `pip install`) FIRST. Copy the
fast, frequently-changing thing (your actual code) LAST. If `COPY . .` came
before `pip install`, every single code edit would force a full dependency
reinstall — turning a 2-second rebuild into a 2-minute one.

---

## 4. Core Commands

| Command | What it does |
|---|---|
| `docker build -t myapp .` | Reads the Dockerfile in the current dir, builds an IMAGE, tags it `myapp` |
| `docker run myapp` | Starts a new CONTAINER from that image |
| `docker run -p 8000:8000 myapp` | Maps port 8000 on your real machine → port 8000 inside the container |
| `docker ps` | Lists currently RUNNING containers |
| `docker ps -a` | Lists ALL containers, including stopped ones |
| `docker stop <id>` | Stops a running container (does not delete it) |
| `docker images` | Lists all IMAGES built/pulled |

`-p 8000:8000` is not optional if you need to reach the container from
outside — containers are network-isolated by default, so without an
explicit port mapping, nothing outside the container can reach a port
inside it, even if the app is genuinely listening on it internally.

---

## 5. Volumes — Persisting Data Beyond a Container's Lifetime

By default, anything a container writes to its own filesystem disappears
the moment that container is deleted — containers are meant to be
disposable. A **volume** is storage that lives OUTSIDE the container,
surviving even if the container is destroyed and recreated.

```bash
docker run -v uploads_data:/app/uploads myapp
```

**Shape to memorize:** `docker run -v <volume_name>:<path_inside_container> <image_name>`
— three distinct pieces, in that exact order.

```
   YOUR MACHINE                          CONTAINER
┌───────────────────┐                 ┌───────────────────┐
│  volume:            │  mounted at    │  /app/uploads       │
│  uploads_data       │◄─────────────► │  (writes here go     │
│  (persists forever,  │                │   straight to the    │
│   independent of any │                │   volume outside)     │
│   container)          │                └───────────────────┘
└───────────────────┘
```

A second common use: mounting your LOCAL source code directly into a
running container during development, so edits on your machine show up
instantly inside the container without a rebuild:
```bash
docker run -v $(pwd):/app myproject
```

---

## 6. Environment Variables — Config Without Rebuilding

```bash
docker run -e SECRET_KEY="abc123" myapp
```

The app reads `os.environ["SECRET_KEY"]` at RUNTIME. The exact same image
can run against dev, staging, or production — just by changing what's
passed at `docker run` time, no rebuild required. This is exactly why
secrets/config never get hardcoded into a Dockerfile — they're injected at
container-start time instead.

Multiple flags combine freely in one command:
```bash
docker run -e SECRET_KEY="abc123" -v uploads_data:/app/uploads myapp
```

---

## 7. `docker-compose` — Running Multiple Containers as One System

A real system (like the Attribution Engine: the app + Postgres + Redis)
needs multiple containers running together, able to reach each other.
Writing separate `docker run` commands by hand, in the right order, with
manual networking, is painful. `docker-compose.yml` describes the whole
system declaratively.

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379
  redis:
    image: redis:7
```

```bash
docker-compose up
```

**Network diagram:**
```
                    docker-compose internal network
        ┌─────────────────────────────────────────────┐
        │                                                │
        │   ┌───────────┐         ┌───────────┐        │
port    │   │   app       │──────►│   redis     │        │
8000 ───┼──►│  container  │  "redis:6379"  │  container  │        │
        │   └───────────┘         └───────────┘        │
        │                                                │
        └─────────────────────────────────────────────┘
```

**The critical rule: the SERVICE NAME becomes the resolvable hostname.**
Because the Redis service is named `redis:` in the YAML, the `app`
container reaches it at hostname `redis` — NOT `localhost`. `localhost`
would be wrong here because each container is its own isolated little
machine; `app` and `redis` don't share a "localhost" with each other at
all. Docker Compose automatically makes every service name resolvable to
the others on its internal network — no manual IP configuration needed.

**YAML structure notes** (real bugs caught while practicing this):
- Indentation is STRUCTURAL in YAML, not cosmetic — everything belonging to
  a service must be indented beneath its service name, or YAML won't
  understand the nesting at all.
- `ports:` and `depends_on:` both take LIST syntax (`- "8000:8000"`, one
  item per line, dash-prefixed), not a bare value on the same line as the key.
- `depends_on` must reference the EXACT service name defined elsewhere in
  the same file — a mismatch (e.g. `depends_on: redis` when the service is
  actually named `db`) silently fails to establish the intended startup order.
- Environment variables that the APP needs (like `REDIS_URL`, to know how
  to reach Redis) belong under the `app` service, not under the service
  they're describing how to reach.

---

## 8. Quick Reference — the Full Picture

```
Dockerfile          →  docker build  →  IMAGE  →  docker run  →  CONTAINER(s)
(blueprint, layers)                    (frozen)                  (isolated, running)

docker-compose.yml  →  docker-compose up  →  multiple CONTAINERS on one
(multi-service spec)                          shared internal network,
                                               service names = hostnames
```

---

## Gate Questions — Verify Understanding

**Q1:** You run `docker run myapp` three times. How many containers exist
afterward, how many images, and are the containers independent of each other?
**A:** 3 containers, 1 image. Fully independent — same relationship as
instantiating a Python class three times: three separate objects, one
class definition, no shared state between instances.

**Q2:** You add a NEW package to `requirements.txt` and rebuild. What
happens to the `RUN pip install` layer, and why — even though the `pip
install` command text itself never changed?
**A:** It reruns. The `COPY requirements.txt .` layer right before it has a
content diff, invalidating its cache — and because of the cascading rule,
every layer downstream of an invalidated layer reruns too, regardless of
whether their own individual command changed.

**Q3:** In a `docker-compose.yml` with services `app` and `db` (Postgres),
what hostname does `app` use to reach `db` — and why is `localhost` wrong here?
**A:** The hostname is `db` — the service name itself, made automatically
resolvable by Docker Compose on the shared internal network. `localhost`
would point `app` at itself, not at the separate `db` container — each
container is its own isolated machine, they don't share a `localhost`.

**Q4:** Why do secrets/config get passed via `-e` at `docker run` time
instead of being written directly into the Dockerfile?
**A:** Values baked into the Dockerfile become part of the image itself —
fixed at build time, requiring a rebuild to change, and risking secrets
being baked into an image that might get pushed to a registry. Passing
config via `-e`/`environment:` at run time lets the exact same image run
identically across dev/staging/prod, config supplied fresh each time.

---

END OF MODULE — DOCKER
