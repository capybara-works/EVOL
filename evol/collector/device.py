import os
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from evol.db.models import Run, DeviceRun, SignalStream

class DeviceCollector:
    def __init__(self, db: Session):
        self.db = db

    def import_session(self, file_path: str, run_id: str = None):
        """
        Import a device session dump.
        If run_id is provided, attach to existing run.
        Otherwise, create a new Run(kind='device').
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Device dump file not found: {file_path}")

        file_stat = os.stat(file_path)
        
        if not run_id:
            # Create new Run
            run = Run(
                kind="device",
                started_at=datetime.utcnow(), # Approximation, ideally from file metadata
                status="success",
                description=f"Imported from {os.path.basename(file_path)}"
            )
            self.db.add(run)
            self.db.flush()
            run_id = run.run_id
        else:
            # Verify run exists
            run = self.db.query(Run).filter(Run.run_id == run_id).first()
            if not run:
                raise ValueError(f"Run {run_id} not found")

        # Create DeviceRun
        # In a real scenario, we'd parse the dump to get model/serial.
        # For v1, we'll use placeholders or extract if possible.
        # Assuming file name format or just generic.
        device_run = DeviceRun(
            run_id=run_id,
            device_model="unknown",
            device_serial="unknown",
            interface_type="file_import"
        )
        self.db.merge(device_run) # Merge in case it already exists (if attaching to existing run)

        # Create SignalStream
        # We store the reference to the file.
        # Spec: "SignalStream → metadata only (mime, size, URL/path reference)"
        signal = SignalStream(
            device_run_id=run_id,
            mime_type="application/octet-stream", # Generic
            size_bytes=file_stat.st_size,
            url_or_path=os.path.abspath(file_path)
        )
        self.db.add(signal)
        
        self.db.commit()
        return run_id
