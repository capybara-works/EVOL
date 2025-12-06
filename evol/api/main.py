from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from evol.db.database import get_db
from evol.db.models import Run, CIRun, DeviceRun, Artifact, LogMeta, CodeMetricSnapshot, SignalStream, BinaryDisasm

app = FastAPI(title="EVOL API", version="1.0.0")

# Pagination dependency
def pagination_params(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000)):
    return {"skip": skip, "limit": limit}

@app.get("/api/v1/projects")
def list_projects(db: Session = Depends(get_db)):
    # Distinct repo_ids from Runs
    projects = db.query(Run.repo_id).distinct().filter(Run.repo_id != None).all()
    return [p[0] for p in projects]

@app.get("/api/v1/runs")
def list_runs(
    repo_id: Optional[str] = None,
    kind: Optional[str] = None,
    pagination: dict = Depends(pagination_params),
    db: Session = Depends(get_db)
):
    query = db.query(Run)
    if repo_id:
        query = query.filter(Run.repo_id == repo_id)
    if kind:
        query = query.filter(Run.kind == kind)
    
    return query.offset(pagination["skip"]).limit(pagination["limit"]).all()

@app.get("/api/v1/ci-runs")
def list_ci_runs(
    repo_id: Optional[str] = None,
    pagination: dict = Depends(pagination_params),
    db: Session = Depends(get_db)
):
    query = db.query(CIRun).join(Run)
    if repo_id:
        query = query.filter(Run.repo_id == repo_id)
    
    return query.offset(pagination["skip"]).limit(pagination["limit"]).all()

@app.get("/api/v1/artifacts")
def list_artifacts(
    repo_id: Optional[str] = None,
    pagination: dict = Depends(pagination_params),
    db: Session = Depends(get_db)
):
    query = db.query(Artifact).join(Run)
    if repo_id:
        query = query.filter(Run.repo_id == repo_id)
        
    return query.offset(pagination["skip"]).limit(pagination["limit"]).all()

@app.get("/api/v1/metrics/loc")
def list_loc_metrics(
    repo_id: Optional[str] = None,
    pagination: dict = Depends(pagination_params),
    db: Session = Depends(get_db)
):
    query = db.query(CodeMetricSnapshot).join(Run)
    if repo_id:
        query = query.filter(Run.repo_id == repo_id)
        
    return query.offset(pagination["skip"]).limit(pagination["limit"]).all()

@app.get("/api/v1/logs")
def list_logs(
    repo_id: Optional[str] = None,
    pagination: dict = Depends(pagination_params),
    db: Session = Depends(get_db)
):
    query = db.query(LogMeta).join(Run)
    if repo_id:
        query = query.filter(Run.repo_id == repo_id)
        
    return query.offset(pagination["skip"]).limit(pagination["limit"]).all()

@app.get("/api/v1/device-runs")
def list_device_runs(
    device_id: Optional[str] = None, # Interpreted as serial or model? Spec says device_id.
                                     # DeviceRun has device_serial.
    pagination: dict = Depends(pagination_params),
    db: Session = Depends(get_db)
):
    query = db.query(DeviceRun)
    if device_id:
        query = query.filter(DeviceRun.device_serial == device_id)
        
    return query.offset(pagination["skip"]).limit(pagination["limit"]).all()

@app.get("/api/v1/signals")
def list_signals(
    device_run_id: Optional[str] = None,
    pagination: dict = Depends(pagination_params),
    db: Session = Depends(get_db)
):
    query = db.query(SignalStream)
    if device_run_id:
        query = query.filter(SignalStream.device_run_id == device_run_id)
        
    return query.offset(pagination["skip"]).limit(pagination["limit"]).all()

@app.get("/api/v1/disasm")
def get_disasm(
    artifact_id: str,
    db: Session = Depends(get_db)
):
    disasm = db.query(BinaryDisasm).filter(BinaryDisasm.artifact_id == artifact_id).first()
    if not disasm:
        raise HTTPException(status_code=404, detail="Disassembly not found")
    return disasm
