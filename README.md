# Hackathon Multiverse

An AI-driven hackathon project that evolves NFT sales strategies by optimizing the **system prompts** given to large language model (LLM) agents. The platform explores, evaluates, and visualizes how different instructions influence conversations with skeptical crypto investors, helping teams iterate on go-to-market messaging in real time.

---

## Table of Contents
1. [High-Level Architecture](#high-level-architecture)
2. [Key Capabilities](#key-capabilities)
3. [System Overview](#system-overview)
4. [Quick Start](#quick-start)
5. [Running with Docker](#running-with-docker)
6. [Developer Tooling & Scripts](#developer-tooling--scripts)
7. [API Surface](#api-surface)
8. [Testing](#testing)
9. [Project Structure](#project-structure)
10. [License](#license)

---

## High-Level Architecture
- **Backend API (FastAPI)** – exposes REST + WebSocket endpoints for seeding prompts, streaming graph updates, and tuning scoring weights.
- **Parallel Worker** – evolves system prompts using evolutionary search, tracks token budgets, and persists node statistics.
- **Redis** – shared state store for prompt nodes, evaluation metrics, and scheduling queues.
- **Visualization Server** – lightweight Python server that renders a matrix-style, real-time view of the prompt landscape at `http://localhost:3000`.
- **Scripts** – bootstrap datasets, run demos, and analyze exploration trajectories.


---

## Key Capabilities
- 🧬 **System Prompt Evolution** – generates variations of root instructions, tests them across scenarios, and prioritizes high performers.
- 🧠 **Meta-Learning Mindset** – optimizes "how to think" instructions instead of individual conversation turns.
- 📈 **Multi-Metric Scoring** – combines engagement, trust, objection handling, and purchase likelihood into aggregate scores.
- 🛡️ **Safety & Budget Guards** – moderation checks and configurable spending limits for LLM usage.
- 📊 **Live Visualization** – watch prompt effectiveness evolve on a 2D semantic map with drill-down conversation samples.

---

## System Overview
1. **Seed** the system with an initial system prompt (or auto-generate defaults).
2. **Worker** pulls prompts from the frontier, mutates them, and spawns evaluation conversations with plateau detection.
3. **Evaluator** aggregates metrics and updates node performance plus token usage costs.
4. **Scheduler** re-prioritizes the frontier so the best-performing prompts get iterated first.
5. **Visualization** consumes the API/WebSocket feed to render the evolving prompt multiverse.

For a detailed engineering breakdown, see [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) and [INTEGRATION_COMPLETE.md](INTEGRATION_COMPLETE.md).

---

## Quick Start
### Prerequisites
- Python **3.11+**
- A running **Redis 7** instance
- `OPENAI_API_KEY` set in your environment (for live LLM usage)
- Recommended: a dedicated virtual environment (`python -m venv .venv`)

### Installation
```bash
# Clone repo and install dependencies
pip install -r requirements.txt

# Activate virtual environment if using one
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\activate  # Windows PowerShell
```

### Launch Sequence (Five-Terminal Flow)
1. **Redis Server**
   ```bash
   redis-server
   ```

2. **Backend API**
   ```bash
   uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
   ```

3. **Visualization UI**
   ```bash
   python frontend/server.py
   # Open http://localhost:3000 in a browser
   ```

4. **Seed Data & Start Worker**
   ```bash
   redis-cli flushall                # optional reset
   python scripts/dev_seed.py        # seeds baseline system prompts
   python -m backend.worker.parallel_worker
   ```

5. **(Optional) Live Terminal Monitor**
   ```bash
   python -m visualization.live_monitor
   ```

Within a few minutes you will see prompts, scores, and sample conversations streaming into the UI.

---

## Running with Docker
Prefer containers? Use the provided `docker-compose.yml`:

```bash
docker compose up --build
```

This starts Redis, the FastAPI service, and the worker. After the stack is healthy, seed an initial prompt:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"prompt": "You are a pragmatic blockchain educator focused on building trust."}' \
  http://localhost:8000/seed
```

You can still run `frontend/server.py` locally to view the visualization while the backend stack runs in Docker.

---

## Developer Tooling & Scripts
| Script | Purpose |
| ------ | ------- |
| `scripts/dev_seed.py` | Populate Redis with starter system prompts. |
| `scripts/e2e_demo.py` | Spin up a fast three-node exploration demo. |
| `scripts/long_run_demo.py` | Launch a 100-node parallel exploration to observe long-term trends. |
| `scripts/exploration_analyzer.py` | Post-process stored prompts to surface insights. |

Useful utilities:
- `visualization/live_monitor.py` – ASCII dashboard for quick terminal monitoring.
- `backend/core/evaluation.py` – centralized scoring logic and prompt comparisons.

---

## API Surface
The FastAPI application exposes the following notable endpoints:

| Method & Path | Description |
| ------------- | ----------- |
| `POST /seed` | Create a new root system prompt (auto-generates one if body is empty). |
| `GET /graph` | Retrieve all nodes with XY coordinates, scores, and lineage for visualization. |
| `GET /system_prompt/{node_id}` | Fetch full system prompt text plus aggregated metrics. |
| `GET /conversation_samples/{node_id}` | Inspect evaluation conversations generated for a node. |
| `POST /focus_zone` | Boost or seed prompts inside a user-defined polygon on the map. |
| `GET /settings` / `PATCH /settings` | Read or adjust runtime weighting parameters. |

See [`backend/api/routes.py`](backend/api/routes.py) for full request/response models.

---

## Testing
Run the full automated suite:
```bash
pytest
```

Focused integration tests:
```bash
pytest tests/test_system_prompt_optimization_integration.py -v
pytest tests/test_end_to_end_system_prompt.py -v
```

Tests cover cost tracking, moderation controls, worker scheduling, and full prompt evolution flows.

---

## Project Structure
```
backend/                # FastAPI app, worker orchestration, scoring, data stores
frontend/               # Visualization web server & assets
visualization/          # Terminal dashboards and supporting assets
scripts/                # Demos, seeding, analysis helpers
tests/                  # Unit + integration test suites
docker-compose.yml      # Containerized stack definition
```

---

## License
[MIT](https://opensource.org/licenses/MIT)


