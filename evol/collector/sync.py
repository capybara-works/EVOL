import os
import typer
import shutil
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from evol.db.database import get_db, engine, Base
from evol.db.models import Artifact, BinaryDisasm
from evol.collector.github import GitHubCollector
from evol.collector.device import DeviceCollector
from evol.collector.disasm import DisasmCollector

app = typer.Typer()

@app.command()
def sync(
    project: Optional[str] = typer.Option(None, help="GitHub project (owner/repo)"),
    since: Optional[datetime] = typer.Option(None, help="Sync since timestamp"),
    include_disasm: bool = typer.Option(False, help="Enable disassembly of ELF artifacts"),
    import_device: Optional[str] = typer.Option(None, help="Import device telemetry dump"),
    retain_binaries: bool = typer.Option(False, help="Retain downloaded binary artifacts"),
):
    """
    EVOL Collector Sync
    """
    # Ensure DB tables exist (for v1 simplicity, usually handled by alembic)
    Base.metadata.create_all(bind=engine)
    
    db = next(get_db())
    
    # 1. Device Import
    if import_device:
        typer.echo(f"Importing device dump: {import_device}")
        collector = DeviceCollector(db)
        try:
            run_id = collector.import_session(import_device)
            typer.echo(f"Device run imported: {run_id}")
        except Exception as e:
            typer.echo(f"Device import failed: {e}", err=True)

    # 2. GitHub Sync
    if project:
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            typer.echo("GITHUB_TOKEN not found in environment", err=True)
            raise typer.Exit(code=1)
            
        typer.echo(f"Syncing GitHub project: {project}")
        gh_collector = GitHubCollector(db, project, token)
        try:
            gh_collector.sync_runs(since=since)
            typer.echo("GitHub sync complete")
        except Exception as e:
            typer.echo(f"GitHub sync failed: {e}", err=True)
        
        # 3. Disassembly (only if project sync happened or we want to process existing)
        # Spec says "Triggered when ELF artifact present."
        # We should iterate over artifacts that don't have disassembly yet if include_disasm is True.
        if include_disasm:
            process_disassembly(db, gh_collector, retain_binaries)
            
        gh_collector.close()

def process_disassembly(db: Session, gh_collector: GitHubCollector, retain_binaries: bool):
    disasm_tool = DisasmCollector()
    if not disasm_tool.is_available():
        typer.echo("objdump not found, skipping disassembly", err=True)
        return

    # Find artifacts without disassembly that look like ELF
    # For v1, we just check extension or try all? Spec says "ELF artifact".
    # We'll check for no extension or .elf, .so, .o, or just try.
    # Let's filter by file_type or name.
    # And check if BinaryDisasm exists.
    
    artifacts = db.query(Artifact).outerjoin(BinaryDisasm).filter(BinaryDisasm.artifact_id == None).all()
    
    for artifact in artifacts:
        # Simple heuristic for ELF candidates
        if not artifact.name.endswith((".elf", ".so", "bin")): # bin might be raw binary
             # Maybe check file header? For now, extension based.
             # If extension is missing, maybe?
             continue
             
        typer.echo(f"Processing artifact for disassembly: {artifact.name}")
        
        # Download
        temp_path = f"temp_{artifact.artifact_id}_{artifact.name}"
        try:
            if not artifact.url:
                typer.echo(f"No URL for artifact {artifact.name}, skipping", err=True)
                continue
                
            gh_collector.download_artifact(artifact.url, temp_path)
            
            # Disassemble
            disasm_text, tool_version = disasm_tool.disassemble(temp_path)
            
            # Store
            disasm = BinaryDisasm(
                artifact_id=artifact.artifact_id,
                disasm_text=disasm_text,
                tool_version=tool_version
            )
            db.add(disasm)
            db.commit()
            typer.echo(f"Disassembly stored for {artifact.name}")
            
        except Exception as e:
            typer.echo(f"Failed to process {artifact.name}: {e}", err=True)
        finally:
            if not retain_binaries and os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == "__main__":
    app()
