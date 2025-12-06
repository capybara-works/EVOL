import os
import time
import httpx
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from evol.db.models import Run, CIRun, Artifact, LogMeta, CodeMetricSnapshot

GITHUB_API_BASE = "https://api.github.com"

class GitHubCollector:
    def __init__(self, db: Session, project: str, token: str):
        self.db = db
        self.owner, self.repo = project.split("/")
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "EVOL-Collector/1.0"
        }
        self.client = httpx.Client(base_url=GITHUB_API_BASE, headers=self.headers, timeout=30.0)

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Any:
        retries = 3
        backoff = 1.0
        
        for attempt in range(retries):
            try:
                response = self.client.request(method, endpoint, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code in (403, 429, 500, 502, 503, 504):
                    # Rate limited or server error
                    pass
                else:
                    raise e
            except httpx.RequestError:
                pass
            
            if attempt < retries - 1:
                time.sleep(backoff)
                backoff *= 2.0
        
        raise Exception(f"Failed to fetch {endpoint} after {retries} attempts")

    def sync_runs(self, since: Optional[datetime] = None):
        # Fetch workflow runs
        endpoint = f"/repos/{self.owner}/{self.repo}/actions/runs"
        params = {"per_page": 100}
        if since:
            params["created"] = f">{since.isoformat()}"

        # Pagination handling (simplified for v1, just fetching first page or iterating)
        # In a real scenario, we'd loop through pages.
        # For v1, let's implement basic pagination loop.
        
        page = 1
        while True:
            params["page"] = page
            data = self._request("GET", endpoint, params=params)
            runs = data.get("workflow_runs", [])
            
            if not runs:
                break
                
            for run_data in runs:
                self._process_run(run_data)
            
            if len(runs) < 100:
                break
            page += 1

    def _process_run(self, data: Dict[str, Any]):
        run_id = str(data["id"])
        
        # Check if exists
        existing = self.db.query(Run).filter(Run.external_ci_id == run_id).first()
        if existing:
            return # Skip or update? Spec says append-only, but maybe we update status?
                   # Spec says "Incremental ingestion only". If it exists, we assume it's done or we skip.
                   # Let's skip for now to be safe and simple.

        # Create Run
        run = Run(
            kind="ci",
            repo_id=f"{self.owner}/{self.repo}",
            commit_sha=data["head_sha"],
            started_at=datetime.fromisoformat(data["run_started_at"].replace("Z", "+00:00")),
            ended_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")), # Best approximation
            status=data["conclusion"] or "unknown",
            external_ci_id=run_id,
            description=data["name"]
        )
        self.db.add(run)
        self.db.flush() # Get run.run_id

        # Create CIRun
        ci_run = CIRun(
            run_id=run.run_id,
            trigger=data["event"],
            duration_seconds=(run.ended_at - run.started_at).total_seconds() if run.ended_at and run.started_at else 0,
            default_branch=data["head_branch"], # Approximation
            # tag_count and branch_count would require separate API calls, skipping for efficiency in v1 unless critical
        )
        self.db.add(ci_run)

        # Process Artifacts
        artifacts_url = data["artifacts_url"] # This is a full URL, need to parse or use just the path if using base_url
        # artifacts_url usually looks like https://api.github.com/repos/owner/repo/actions/runs/ID/artifacts
        # We can just request it directly.
        self._process_artifacts(run.run_id, artifacts_url)

        # Process Logs
        # logs_url = data["logs_url"] # This redirects to a zip.
        # Spec says: LogMeta: has_log, size_bytes, URL ONLY (NO CONTENT INGESTION)
        log_meta = LogMeta(
            run_id=run.run_id,
            has_log=True, # Assume yes if run exists
            url=data.get("logs_url")
        )
        self.db.add(log_meta)
        
        # Process Metrics (LOC/Size)
        self._process_metrics(run.run_id, data["head_sha"])

        self.db.commit()

    def _process_metrics(self, run_id: str, commit_sha: str):
        try:
            # Fetch tree recursively
            # /repos/{owner}/{repo}/git/trees/{sha}?recursive=1
            endpoint = f"/repos/{self.owner}/{self.repo}/git/trees/{commit_sha}"
            data = self._request("GET", endpoint, params={"recursive": "1"})
            
            if data.get("truncated"):
                print(f"Warning: Tree for {commit_sha} is truncated. Metrics may be incomplete.")

            tree = data.get("tree", [])
            
            total_size = 0
            by_dir = {}
            by_lang = {} # Extension based

            for item in tree:
                if item["type"] != "blob":
                    continue
                
                size = item.get("size", 0)
                path = item["path"]
                
                total_size += size
                
                # Directory breakdown (top level)
                parts = path.split("/")
                if len(parts) > 1:
                    top_dir = parts[0]
                    by_dir[top_dir] = by_dir.get(top_dir, 0) + size
                else:
                    by_dir["."] = by_dir.get(".", 0) + size
                
                # Language breakdown (extension)
                ext = os.path.splitext(path)[1].lower()
                if not ext:
                    ext = "no_extension"
                by_lang[ext] = by_lang.get(ext, 0) + size

            metrics = CodeMetricSnapshot(
                run_id=run_id,
                total_loc=total_size, # Using size in bytes as proxy for "LOC" in v1
                loc_by_dir=by_dir,
                loc_by_lang=by_lang
            )
            self.db.add(metrics)


        except Exception as e:
            print(f"Failed to process metrics for run {run_id}: {e}")

    def _process_artifacts(self, run_id: str, url: str):
        # The url is absolute, so we use a new request or override base
        # httpx client with base_url might be tricky with absolute url.
        # client.get(url) works if url is absolute.
        
        try:
            data = self._request("GET", url)
            artifacts = data.get("artifacts", [])
            
            for art in artifacts:
                # Ingest artifact metadata
                artifact = Artifact(
                    run_id=run_id,
                    name=art["name"],
                    file_type=os.path.splitext(art["name"])[1] or "unknown",
                    size_bytes=art["size_in_bytes"],
                    url=art["archive_download_url"],
                    created_at=datetime.fromisoformat(art["created_at"].replace("Z", "+00:00"))
                )
                self.db.add(artifact)
                
                # Spec: "Artifacts MAY be downloaded temporarily for disassembly."
                # We need to download if it's an ELF and we want disassembly.
                # For now, just storing metadata. Disassembly logic will be separate or called here.
                # Let's keep it separate or integrate?
                # "Triggered when ELF artifact present."
                # We should probably download here if it looks like an ELF.
                
        except Exception as e:
            print(f"Failed to process artifacts for run {run_id}: {e}")

    def download_artifact(self, url: str, target_path: str):
        with self.client.stream("GET", url) as response:
            response.raise_for_status()
            with open(target_path, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)

    def close(self):
        self.client.close()
