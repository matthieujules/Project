# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a hackathon project implementing an AI-powered prompt exploration system using MCTS-inspired algorithms and multi-agent orchestration. The system explores prompt variations, evaluates them, and builds a tree structure visualized in 2D space.

## Architecture

The system consists of:
- **FastAPI backend** with WebSocket support for real-time updates
- **Redis** for node storage, frontier priority queue, and pub/sub messaging
- **Worker process** that continuously processes nodes from the frontier
- **Three stub agents** (mutator, persona, critic) ready for AI implementation

Data flows through: Frontier → Worker → Agents → New Nodes → Priority Calculation → Back to Frontier

## Essential Commands

### Running the Application
```bash
# Start all services (preferred method)
docker compose up

# Run tests
docker compose run test

# Local development (requires Redis running)
python -m backend.api.main  # API server on port 8000
python -m backend.worker.worker  # Worker process
python scripts/dev_seed.py  # Seed initial data
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_frontier.py

# Tests auto-clear Redis before/after each test via conftest.py
```

### Linting and Type Checking
The project doesn't have explicit lint/typecheck commands configured. When implementing new features, ensure code follows existing patterns and type hints.

## Key Implementation Details

### Priority Calculation Formula
Priority = `S + λ_trend*ΔS - λ_sim*similarity - λ_depth*depth`

Where:
- S = current node score
- ΔS = score improvement from parent
- similarity = max similarity to top-k nodes
- depth = node depth in tree

### Agent Implementations (Currently Stubs)
- `backend/agents/mutator.py`: Returns 3 variations by adding prefixes
- `backend/agents/persona.py`: Returns "SimPutin replies to: {prompt}"
- `backend/agents/critic.py`: Returns random score between 0-1

### Focus Zone Behavior
- **Explore mode**: Seeds new depth-1 node if zone is empty
- **Extend mode**: Boosts priority of all nodes within polygon

### Environment Configuration
Set via environment variables or `.env` file:
- `REDIS_URL` (default: redis://localhost:6379/0)
- `LAMBDA_TREND` (default: 0.3)
- `LAMBDA_SIM` (default: 0.2)
- `LAMBDA_DEPTH` (default: 0.05)

## API Endpoints
- `GET /settings`: Current lambda values
- `PATCH /settings`: Update lambda values at runtime
- `POST /focus_zone`: Boost/seed nodes in polygon area
- `WebSocket /ws`: Real-time graph updates

## Testing Patterns
- Tests use `@pytest.mark.asyncio` for async functions
- Integration tests assume API server runs on localhost:8000
- Use `subprocess.run()` to execute dev_seed.py in tests
- WebSocket tests use httpx.AsyncClient

## Next Steps for Real Implementation
The stub agents in `backend/agents/` need real implementations:
1. **Mutator**: Integrate LLM for intelligent prompt variations
2. **Persona**: Add actual AI model responses
3. **Critic**: Implement sophisticated scoring mechanism

Embeddings are currently stubbed using hash-based vectors. Replace with real embedding model in `backend/core/embeddings.py`.