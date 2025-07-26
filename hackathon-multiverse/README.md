# Hackathon Multiverse - System Prompt Optimization

AI-powered system prompt optimization framework using evolutionary algorithms and multi-agent orchestration. The system evolves optimal instructions (system prompts) for LLM agents to achieve specific goals.

## Complete System Startup Guide

### Prerequisites

- Python 3.11+ with virtual environment
- Redis server installed
- OpenAI API key set in `.env` file

### Step-by-Step Launch Sequence

**Terminal 1: Start Redis Server**

```bash
redis-server
# Should show "Ready to accept connections"
```

**Terminal 2: Start Backend API**

```bash
cd /Users/matthieuhuss/AdventureX-Final/hackathon-multiverse
source .venv/bin/activate
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
```

**Terminal 3: Start Web Visualization**

```bash
cd /Users/matthieuhuss/AdventureX-Final/hackathon-multiverse
python frontend/server.py
# Visit http://localhost:3000 to see the visualization
```

**Terminal 4: Seed the System & Start Worker**

```bash
cd /Users/matthieuhuss/AdventureX-Final/hackathon-multiverse
source .venv/bin/activate

# Clear any old data and seed system prompts
redis-cli flushall
python scripts/dev_seed.py  # Seeds initial system prompts

# Start the parallel worker (evolves system prompts)
python -m backend.worker.parallel_worker
```

**Terminal 5: (Optional) Live Terminal Monitor**

```bash
cd /Users/matthieuhuss/AdventureX-Final/hackathon-multiverse
source .venv/bin/activate
python -m visualization.live_monitor
```

### What You'll See

1. **Web Interface (localhost:3000)**: Matrix-style real-time visualization showing:
   - System prompt evolution in 2D semantic space
   - Color-coded nodes by effectiveness (red=poor, green=effective)
   - Live statistics (total prompts tested, avg score, generations)
   - Real-time activity log of new system prompts being evolved
   - Clickable nodes to see system prompts and their test conversations

2. **Worker Terminal**: System prompt evolution logs like:

   ```
   🔄 Processing bea8a669... depth=2 system_prompt='You are a diplomatic negotiator...'
   📊 Parent performance: avg_score=0.600, samples=3
   🧬 Generated 3 system prompt variants
   📝 Testing system prompt across 3 scenarios
   ✅ Child AVG_SCORE=0.750 priority=0.694
   📝 System prompt: 'You are an empathetic negotiator who builds trust...'
   📊 Results: 3 conversations, 33.3% success, 4.5 avg turns
   ```

3. **Terminal Monitor**: ASCII dashboard with evolution progress and real-time stats

### Quick Docker Alternative

**Start basic stack (without visualization)**

```bash
docker compose up --build
```

**Seed a root node**

```bash
curl -X POST localhost:8000/seed -d '{"prompt": "How can we achieve lasting peace?"}' -H "Content-Type: application/json"
```

## For UI Developers

The backend provides a simple REST + WebSocket API:

1. **GET /graph** - Get all nodes for initial canvas rendering
2. **POST /seed** - Start exploration with a root prompt
3. **POST /focus_zone** - Boost/seed nodes in a polygon area
4. **WebSocket /ws** - Real-time updates as new nodes are created

**Example UI Integration:**

1. `GET /graph` once → draw initial points
2. Open WebSocket and incrementally add nodes
3. `POST /focus_zone` or `/seed` when user interacts

## Demo & Testing

**Quick demo (3 nodes):**

```bash
python scripts/e2e_demo.py
```

**100-node PARALLEL exploration with blazing speed:**

```bash
# Make sure system is running (see Complete System Startup Guide above)
# Then run analysis script:
python scripts/long_run_demo.py
```

**Analyze exploration patterns:**

```bash
python scripts/exploration_analyzer.py
```

**Run integration test:**

```bash
pytest tests/test_roundtrip.py -v
```

The long-run demo is perfect for observing AI exploration patterns over time with detailed agent logs and statistics.

## What You'll Observe

- **System Prompt Evolution**: AI discovers optimal instructions for achieving goals
- **Meta-Learning**: System learns "how to think" rather than "what to say"
- **Live Evolution**: Watch system prompts evolve in real-time semantic space
- **Plateau Detection**: Conversations stop naturally when improvement plateaus
- **Multi-Scenario Testing**: Each system prompt tested across multiple conversation scenarios
- **Effectiveness Scoring**: Prompts evaluated based on average conversation performance
- **Generational Improvement**: Track how system prompts improve over generations
- **Tree Structure**: Parent-child relationships showing evolution lineage
- **Priority-Based Selection**: Best-performing prompts prioritized for further evolution
- **Comprehensive Metrics**: Success rates, efficiency scores, consistency measurements
- **Interactive Exploration**: Click nodes to see system prompts and sample conversations

## Key Features

### System Prompt Optimization Framework

This system implements a meta-learning framework that evolves optimal instructions for LLM agents:

- **System Prompt Evolution**: Discovers effective instructions through evolutionary algorithms
- **Target Persona**: The LLM agent to influence (e.g., Putin persona)
- **Objective Function**: Scores conversation effectiveness toward goal
- **Plateau Detection**: Natural conversation termination when improvement plateaus
- **Multi-Scenario Testing**: Each prompt tested across diverse conversation scenarios
- **Priority System**: MCTS-inspired selection balances exploitation vs exploration

### Real-Time Visualization

- **Matrix-style interface** showing system prompt evolution in 2D space
- **Color-coded nodes** by effectiveness (red=poor, orange=moderate, green=effective)
- **Live activity feed** tracking new system prompt discoveries
- **Interactive nodes** click to view system prompts and test conversations
- **WebSocket integration** for real-time updates as prompts evolve
- **Terminal monitor** with ASCII charts showing evolution progress

License: MIT
