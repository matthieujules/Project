# Hackathon Multiverse

AI-powered prompt exploration system using MCTS and multi-agent orchestration.

## Quick Start

**Start stack**

```bash
docker compose up --build
```

**Seed a root node**

```bash
curl -X POST localhost:8000/seed -d '"Will AI reduce wars?"' -H "Content-Type: application/json"
```

**Live stream updates**

```bash
# Using websocat (install with: cargo install websocat)
websocat ws://localhost:8000/ws

# Or using any WebSocket client
```

**Get graph snapshot**

```bash
curl http://localhost:8000/graph
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

**Run end-to-end demo:**
```bash
python scripts/e2e_demo.py
```

This seeds a node, listens for WebSocket updates, and snapshots the final graph. Perfect for demonstrating the live exploration process.

**Run integration test:**
```bash
pytest tests/test_roundtrip.py -v
```

Verifies the complete API → Worker → WebSocket flow works correctly.

## What You'll Observe

- **Live exploration**: Watch nodes appear in real-time as AI explores different angles
- **Spatial positioning**: Nodes positioned in 2D space based on semantic similarity  
- **Tree structure**: Parent-child relationships as exploration deepens
- **Priority-based expansion**: Higher-scoring nodes get processed first
- **Agent costs**: Token usage and costs tracked in logs

License: MIT