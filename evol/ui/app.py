import os
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from evol.db.models import Run, Artifact
from evol.db.database import get_database_url
from evol.ui.auth import verify_credentials, get_auth_credentials

# App setup
app = FastAPI(title="EVOL Control Panel", version="1.1.0")

# Templates and static files
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Database connection
engine = create_engine(get_database_url(), connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

# Background task tracker
active_tasks: Dict[str, Dict] = {}


def get_optional_auth():
    """Return auth dependency only if authentication is configured."""
    if get_auth_credentials() is None:
        # No auth configured - return dummy dependency that always returns None
        return lambda: None
    # Auth configured - use verification
    return Depends(verify_credentials)


def get_db_stats() -> Dict:
    """Get database statistics."""
    session = SessionLocal()
    try:
        total_runs = session.query(func.count(Run.run_id)).scalar() or 0
        total_artifacts = session.query(func.count(Artifact.artifact_id)).scalar() or 0
        
        # Get last sync time
        last_run = session.query(Run).order_by(Run.started_at.desc()).first()
        last_sync = last_run.started_at if last_run else None
        
        # Get recent runs
        recent_runs = (
            session.query(Run)
            .order_by(Run.started_at.desc())
            .limit(5)
            .all()
        )
        
        return {
            "total_runs": total_runs,
            "total_artifacts": total_artifacts,
            "last_sync": last_sync,
            "recent_runs": recent_runs,
        }
    finally:
        session.close()


async def run_sync_task(project: str, include_disasm: bool = False):
    """Run sync task in background."""
    task_id = f"{project}_{datetime.now().timestamp()}"
    active_tasks[task_id] = {
        "project": project,
        "status": "running",
        "started_at": datetime.now(),
    }
    
    try:
        cmd = ["python", "-m", "evol.collector.sync", "--project", project]
        if include_disasm:
            cmd.append("--include-disasm")
        
        # Load env vars
        env = os.environ.copy()
        if os.path.exists(".env"):
            with open(".env") as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        env[key] = value
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        
        stdout, stderr = await process.communicate()
        
        active_tasks[task_id]["status"] = "completed" if process.returncode == 0 else "failed"
        active_tasks[task_id]["output"] = stdout.decode()
        active_tasks[task_id]["error"] = stderr.decode() if stderr else None
        
    except Exception as e:
        active_tasks[task_id]["status"] = "failed"
        active_tasks[task_id]["error"] = str(e)


@app.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: Optional[str] = Depends(get_optional_auth())
):
    """Main dashboard page with optional authentication."""
    stats = get_db_stats()
    
    # Check if Grafana is running
    grafana_running = False
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=evol-grafana", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
        )
        grafana_running = "evol-grafana" in result.stdout
    except:
        pass
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "stats": stats,
            "grafana_running": grafana_running,
            "active_tasks": active_tasks,
        },
    )


@app.post("/api/trigger-sync")
async def trigger_sync(
    background_tasks: BackgroundTasks,
    project: str,
    include_disasm: bool = False,
    user: Optional[str] = Depends(get_optional_auth())
):
    """Trigger a background sync task with optional authentication."""
    task_id = f"sync-{project.replace('/', '-')}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Store task info
    active_tasks[task_id] = {
        "status": "running",
        "project": project,
        "started_at": datetime.now(),
        "include_disasm": include_disasm
    }
    
    if not project:
        active_tasks[task_id]["status"] = "failed"
        active_tasks[task_id]["error"] = "Project parameter required"
        return JSONResponse({"error": "Project parameter required"}, status_code=400)
    
    # Check if GITHUB_TOKEN is set
    if not os.getenv("GITHUB_TOKEN"):
        active_tasks[task_id]["status"] = "failed"
        active_tasks[task_id]["error"] = "GITHUB_TOKEN not set in environment"
        return JSONResponse(
            {"error": "GITHUB_TOKEN not set in environment"},
            status_code=400,
        )
    
    # Run sync in background
    background_tasks.add_task(run_sync_background, project, include_disasm, task_id)
    
    return JSONResponse(
        {
            "status": "started",
            "project": project,
            "message": f"Sync started for {project}",
            "task_id": task_id,
        }
    )


@app.get("/api/status")
async def get_status():
    """Get system status."""
    stats = get_db_stats()
    
    return JSONResponse(
        {
            "database": {
                "total_runs": stats["total_runs"],
                "total_artifacts": stats["total_artifacts"],
                "last_sync": stats["last_sync"].isoformat() if stats["last_sync"] else None,
            },
            "active_tasks": len([t for t in active_tasks.values() if t["status"] == "running"]),
        }
    )


@app.get("/api/recent-syncs")
async def get_recent_syncs():
    """Get recent sync history."""
    stats = get_db_stats()
    
    syncs = []
    for run in stats["recent_runs"]:
        syncs.append(
            {
                "repo_id": run.repo_id,
                "status": run.status,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "kind": run.kind,
            }
        )
    
    return JSONResponse({"syncs": syncs})


@app.post("/api/open-grafana")
async def open_grafana():
    """Redirect to Grafana."""
    return RedirectResponse(url="http://localhost:3000", status_code=302)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
