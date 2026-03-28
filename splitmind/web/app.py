"""
SplitMind Web Application - FastAPI-based web interface.
"""

from typing import Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from datetime import datetime
import uuid
from pathlib import Path

from splitmind.core.engine import SplitMindEngine, ExecutionResult
from splitmind.core.splitter import TaskSplitter
from splitmind.core.privacy import PrivacyHandler
from splitmind.providers.openai_provider import OpenAIProvider
from splitmind.providers.anthropic_provider import AnthropicProvider
from splitmind.providers.kimi_provider import KimiProvider
from splitmind.providers.local_provider import LocalProvider
from splitmind.config import settings


app = FastAPI(
    title="SplitMind",
    description="Privacy-preserving multi-agent task orchestration system",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskRequest(BaseModel):
    task: str
    context: Optional[str] = None
    strategy: str = "auto"
    execution_mode: str = "hybrid"
    providers: Optional[List[str]] = None
    enable_privacy: bool = True


class AnalyzeRequest(BaseModel):
    text: str


class PreviewRequest(BaseModel):
    task: str
    context: Optional[str] = None
    strategy: str = "auto"


def get_engine():
    providers = []
    
    if settings.openai_api_key:
        providers.append(OpenAIProvider(api_key=settings.openai_api_key))
    if settings.anthropic_api_key:
        providers.append(AnthropicProvider(api_key=settings.anthropic_api_key))
    if settings.kimi_api_key:
        providers.append(KimiProvider(api_key=settings.kimi_api_key))
    
    providers.append(LocalProvider())
    
    return SplitMindEngine(providers=providers)


execution_history: dict = {}


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=get_index_html())


@app.get("/api/providers")
async def list_providers():
    engine = get_engine()
    status = engine._registry.get_provider_status()
    return {"providers": status}


@app.post("/api/analyze")
async def analyze_text(request: AnalyzeRequest):
    handler = PrivacyHandler()
    report = handler.generate_report(request.text)
    
    return {
        "risk_level": report.risk_level,
        "total_detected": report.total_items_detected,
        "items_by_type": report.items_by_type,
        "redacted_text": report.redacted_text,
    }


@app.post("/api/preview")
async def preview_split(request: PreviewRequest):
    engine = get_engine()
    preview = engine.preview_split(
        task=request.task,
        context=request.context,
        strategy=request.strategy,
    )
    return preview


@app.post("/api/execute")
async def execute_task(request: TaskRequest):
    engine = get_engine()
    engine.config.enable_privacy_protection = request.enable_privacy
    
    # Set execution mode
    from splitmind.core.engine import ExecutionMode
    try:
        engine.config.execution_mode = ExecutionMode(request.execution_mode)
    except ValueError:
        engine.config.execution_mode = ExecutionMode.HYBRID
    
    result = await engine.execute(
        task=request.task,
        context=request.context,
        split_strategy=request.strategy,
        providers=request.providers,
    )
    
    execution_id = str(uuid.uuid4())
    execution_history[execution_id] = {
        "result": result,
        "timestamp": datetime.now().isoformat(),
    }
    
    return {
        "execution_id": execution_id,
        "success": result.success,
        "final_result": result.final_result,
        "execution_time": result.execution_time,
        "privacy_report": result.privacy_report,
        "split_result": {
            "task_type": result.split_result.task_type.value if result.split_result else None,
            "split_strategy": result.split_result.split_strategy if result.split_result else None,
            "total_subtasks": len(result.split_result.subtasks) if result.split_result else 0,
        } if result.split_result else None,
        "aggregated_result": {
            "strategy": result.aggregated_result.aggregation_strategy.value if result.aggregated_result else None,
            "providers_used": result.aggregated_result.providers_used if result.aggregated_result else [],
            "confidence": result.aggregated_result.confidence_score if result.aggregated_result else None,
        } if result.aggregated_result else None,
    }


@app.get("/api/execution/{execution_id}")
async def get_execution(execution_id: str):
    if execution_id not in execution_history:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return execution_history[execution_id]


@app.get("/api/history")
async def get_history():
    return {
        "executions": [
            {
                "id": eid,
                "timestamp": data["timestamp"],
                "success": data["result"].success,
            }
            for eid, data in execution_history.items()
        ]
    }


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


def get_index_html():
    # Read the HTML file from the same directory
    html_path = Path(__file__).parent / "index.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    else:
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SplitMind - Privacy-Preserving AI Orchestration</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f0f0f0;
            min-height: 100vh;
            color: #333;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            text-align: center;
        }
        h1 {
            font-size: 2rem;
            color: #0066cc;
            margin-bottom: 20px;
        }
        p {
            font-size: 1.1rem;
            margin-bottom: 30px;
        }
        .btn {
            background: #0066cc;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
        }
        .btn:hover {
            background: #0052a3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 SplitMind</h1>
        <p>Privacy-preserving multi-agent task orchestration</p>
        <p>HTML file not found. Please ensure index.html is in the same directory.</p>
        <a href="/api/health"><button class="btn">Check Health</button></a>
    </div>
</body>
</html>
"""

# Serve static files
app.mount("/static", StaticFiles(directory=Path(__file__).parent), name="static")
