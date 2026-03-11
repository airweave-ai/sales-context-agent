"""
FastAPI backend for the Sales Context Agent.

Generates pre-meeting briefs by searching across multiple sources
(Notion, Google Drive, GitHub) via Airweave. Features:
- LLM-powered query decomposition from briefing requests
- Airweave cross-source search with source filtering
- LLM-powered synthesis into structured account briefs
- Optional Slack posting of generated briefs
- Real-time pipeline progress via WebSocket
"""
import asyncio
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load environment variables first
load_dotenv()

# Import our modules
from config import get_config
from samples import (
    get_sample_briefing_request,
    get_sample_decomposed_queries,
    get_sample_search_results,
    get_sample_brief,
)
from pipeline import QueryDecomposer, ContextSearcher, BriefSynthesizer, BriefOutputHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Pydantic Models ---

class PipelineConfig(BaseModel):
    """Configuration for running the pipeline."""
    use_sample_data: bool = True
    briefing_request: Optional[Dict[str, Any]] = None
    post_to_slack: bool = False


class PipelineStep(BaseModel):
    """Represents a single step in the pipeline."""
    id: str
    name: str
    status: str  # "pending", "running", "completed", "error"
    data: Optional[Dict[str, Any]] = None
    reasoning: Optional[str] = None
    duration_ms: Optional[int] = None


class PipelineState(BaseModel):
    """Current state of the pipeline."""
    run_id: str
    status: str  # "idle", "running", "completed", "error"
    current_step: int
    steps: List[PipelineStep]
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


# --- WebSocket Connection Manager ---

class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(
            f"Client connected. Total connections: {len(self.active_connections)}"
        )

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(
            f"Client disconnected. Total connections: {len(self.active_connections)}"
        )

    async def broadcast(self, message: dict):
        """Send message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}")


manager = ConnectionManager()


# --- Pipeline Execution ---

async def run_pipeline(config: PipelineConfig) -> PipelineState:
    """Run the sales context agent pipeline with real-time updates."""
    run_id = f"run-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

    # Initialize pipeline state
    steps = [
        PipelineStep(
            id="briefing-request", name="Briefing Request", status="pending"
        ),
        PipelineStep(
            id="decomposition", name="Query Decomposition", status="pending"
        ),
        PipelineStep(
            id="source-search", name="Source Search", status="pending"
        ),
        PipelineStep(
            id="synthesis", name="Context Synthesis", status="pending"
        ),
        PipelineStep(
            id="brief-output", name="Brief Output", status="pending"
        ),
    ]

    state = PipelineState(
        run_id=run_id,
        status="running",
        current_step=0,
        steps=steps,
        started_at=datetime.now(timezone.utc).isoformat(),
    )

    # Broadcast initial state
    await manager.broadcast({
        "type": "pipeline_started",
        "state": state.model_dump(),
    })

    try:
        # Initialize pipeline components
        decomposer = QueryDecomposer()
        searcher = ContextSearcher()
        synthesizer = BriefSynthesizer()
        output_handler = BriefOutputHandler()

        # Determine briefing request (always use sample if none provided)
        if config.briefing_request:
            briefing_request = config.briefing_request
        else:
            briefing_request = get_sample_briefing_request()

        # Step 1: Briefing Request
        state.current_step = 0
        state.steps[0].status = "running"
        await manager.broadcast({
            "type": "step_started",
            "step_id": "briefing-request",
            "state": state.model_dump(),
        })

        start_time = datetime.now(timezone.utc)

        state.steps[0].data = {
            "briefing_request": briefing_request,
        }
        await manager.broadcast({
            "type": "step_data_ready",
            "step_id": "briefing-request",
            "state": state.model_dump(),
        })
        await asyncio.sleep(1.5)

        state.steps[0].status = "completed"
        state.steps[0].duration_ms = int(
            (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        )
        await manager.broadcast({
            "type": "step_completed",
            "step_id": "briefing-request",
            "state": state.model_dump(),
        })
        await asyncio.sleep(0.3)

        # Step 2: Query Decomposition
        state.current_step = 1
        state.steps[1].status = "running"
        await manager.broadcast({
            "type": "step_started",
            "step_id": "decomposition",
            "state": state.model_dump(),
        })

        start_time = datetime.now(timezone.utc)

        if config.use_sample_data:
            queries = get_sample_decomposed_queries()
        else:
            queries = await decomposer.decompose(briefing_request)

        state.steps[1].data = {
            "query_count": len(queries),
            "queries": queries,
        }
        state.steps[1].reasoning = decomposer.last_reasoning
        await manager.broadcast({
            "type": "step_data_ready",
            "step_id": "decomposition",
            "state": state.model_dump(),
        })
        await asyncio.sleep(1.5)

        state.steps[1].status = "completed"
        state.steps[1].duration_ms = int(
            (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        )
        await manager.broadcast({
            "type": "step_completed",
            "step_id": "decomposition",
            "state": state.model_dump(),
        })
        await asyncio.sleep(0.3)

        # Step 3: Source Search
        state.current_step = 2
        state.steps[2].status = "running"
        await manager.broadcast({
            "type": "step_started",
            "step_id": "source-search",
            "state": state.model_dump(),
        })

        start_time = datetime.now(timezone.utc)

        if config.use_sample_data:
            search_results = get_sample_search_results()
        else:
            search_results = await searcher.search(queries)

        # Group results by source for display
        results_by_source: Dict[str, list] = {}
        for result in search_results:
            source = result.get("source_name", "unknown")
            if source not in results_by_source:
                results_by_source[source] = []
            results_by_source[source].append(result)

        state.steps[2].data = {
            "result_count": len(search_results),
            "results": search_results,
            "results_by_source": results_by_source,
            "sources_searched": list(results_by_source.keys()),
        }
        await manager.broadcast({
            "type": "step_data_ready",
            "step_id": "source-search",
            "state": state.model_dump(),
        })
        await asyncio.sleep(1.5)

        state.steps[2].status = "completed"
        state.steps[2].duration_ms = int(
            (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        )
        await manager.broadcast({
            "type": "step_completed",
            "step_id": "source-search",
            "state": state.model_dump(),
        })
        await asyncio.sleep(0.3)

        # Step 4: Context Synthesis
        state.current_step = 3
        state.steps[3].status = "running"
        await manager.broadcast({
            "type": "step_started",
            "step_id": "synthesis",
            "state": state.model_dump(),
        })

        start_time = datetime.now(timezone.utc)

        if config.use_sample_data:
            brief = get_sample_brief()
        else:
            brief = await synthesizer.synthesize(briefing_request, search_results)

        state.steps[3].data = {
            "brief": brief,
            "section_count": len(brief.get("sections", [])),
        }
        await manager.broadcast({
            "type": "step_data_ready",
            "step_id": "synthesis",
            "state": state.model_dump(),
        })
        await asyncio.sleep(1.5)

        state.steps[3].status = "completed"
        state.steps[3].duration_ms = int(
            (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        )
        await manager.broadcast({
            "type": "step_completed",
            "step_id": "synthesis",
            "state": state.model_dump(),
        })
        await asyncio.sleep(0.3)

        # Step 5: Brief Output
        state.current_step = 4
        state.steps[4].status = "running"
        await manager.broadcast({
            "type": "step_started",
            "step_id": "brief-output",
            "state": state.model_dump(),
        })

        start_time = datetime.now(timezone.utc)

        output = await output_handler.output(
            brief=brief,
            post_to_slack=config.post_to_slack,
        )

        state.steps[4].data = {
            "output": output,
            "markdown": brief.get("markdown", ""),
        }
        await manager.broadcast({
            "type": "step_data_ready",
            "step_id": "brief-output",
            "state": state.model_dump(),
        })
        await asyncio.sleep(0.5)

        state.steps[4].status = "completed"
        state.steps[4].duration_ms = int(
            (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        )
        await manager.broadcast({
            "type": "step_completed",
            "step_id": "brief-output",
            "state": state.model_dump(),
        })

        # Pipeline complete
        state.status = "completed"
        state.completed_at = datetime.now(timezone.utc).isoformat()
        await manager.broadcast({
            "type": "pipeline_completed",
            "state": state.model_dump(),
        })

    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        state.status = "error"
        if state.current_step < len(state.steps):
            state.steps[state.current_step].status = "error"
        await manager.broadcast({
            "type": "pipeline_error",
            "error": str(e),
            "state": state.model_dump(),
        })

    return state


# --- FastAPI App ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Sales Context Agent...")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Sales Context Agent",
    description="Pre-meeting briefs powered by Airweave cross-source search",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Sales Context Agent",
        "version": "1.0.0",
    }


@app.get("/api/config")
async def get_app_config():
    """Get current configuration status."""
    config = get_config()

    return {
        "airweave_configured": config.airweave.is_configured,
        "openai_configured": bool(config.llm.openai_api_key),
        "anthropic_configured": bool(config.llm.anthropic_api_key),
        "llm_provider": config.llm.provider,
        "airweave": {
            "configured": config.airweave.is_configured,
            "collection_id": (
                config.airweave.collection_id[:8] + "..."
                if config.airweave.collection_id
                else None
            ),
        },
        "llm": {
            "configured": config.llm.is_configured,
            "provider": config.llm.provider,
            "model": config.llm.model,
        },
        "integrations": {
            "slack": {
                "enabled": config.slack.enabled,
                "configured": config.slack.is_configured,
                "mode": "live" if config.slack.is_configured else "preview",
            },
        },
    }


@app.get("/api/samples")
async def get_samples():
    """Get sample briefing data."""
    return {
        "briefing_request": get_sample_briefing_request(),
        "decomposed_queries": get_sample_decomposed_queries(),
        "search_results": get_sample_search_results(),
        "brief": get_sample_brief(),
    }


@app.post("/api/run")
async def run_briefing(config: PipelineConfig):
    """Start a pipeline run."""
    asyncio.create_task(run_pipeline(config))
    return {
        "status": "started",
        "message": "Pipeline started. Connect to WebSocket for updates.",
    }


@app.websocket("/ws/pipeline")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time pipeline updates.

    Messages sent:
    - pipeline_started: Pipeline execution has begun
    - step_started: A step has started processing
    - step_data_ready: Step has data available (still running)
    - step_completed: A step has finished
    - pipeline_completed: All steps finished successfully
    - pipeline_error: An error occurred
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "run":
                config = PipelineConfig(**message.get("config", {}))
                asyncio.create_task(run_pipeline(config))
            elif message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
