import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, Boolean, JSON, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Run(Base):
    __tablename__ = "runs"

    run_id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    kind: Mapped[str] = mapped_column(String, index=True) # ci | device | future
    repo_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    commit_sha: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, index=True, nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String) # success | failure | cancelled | unknown
    external_ci_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    external_device_session_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    ci_run: Mapped[Optional["CIRun"]] = relationship("CIRun", back_populates="run", uselist=False)
    device_run: Mapped[Optional["DeviceRun"]] = relationship("DeviceRun", back_populates="run", uselist=False)
    artifacts: Mapped[List["Artifact"]] = relationship("Artifact", back_populates="run")
    log_meta: Mapped[Optional["LogMeta"]] = relationship("LogMeta", back_populates="run", uselist=False)
    code_metrics: Mapped[Optional["CodeMetricSnapshot"]] = relationship("CodeMetricSnapshot", back_populates="run", uselist=False)

class CIRun(Base):
    __tablename__ = "ci_runs"

    run_id: Mapped[str] = mapped_column(String, ForeignKey("runs.run_id"), primary_key=True)
    trigger: Mapped[Optional[str]] = mapped_column(String, nullable=True) # push, pull_request, schedule
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Repo metadata snapshot
    default_branch: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tag_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    branch_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    run: Mapped["Run"] = relationship("Run", back_populates="ci_run")

class DeviceRun(Base):
    __tablename__ = "device_runs"

    run_id: Mapped[str] = mapped_column(String, ForeignKey("runs.run_id"), primary_key=True)
    device_model: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    device_serial: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    interface_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    run: Mapped["Run"] = relationship("Run", back_populates="device_run")
    signals: Mapped[List["SignalStream"]] = relationship("SignalStream", back_populates="device_run")

class Artifact(Base):
    __tablename__ = "artifacts"

    artifact_id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    run_id: Mapped[str] = mapped_column(String, ForeignKey("runs.run_id"))
    name: Mapped[str] = mapped_column(String)
    file_type: Mapped[Optional[str]] = mapped_column(String, nullable=True) # inferred via extension
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Download URL
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow)
    
    run: Mapped["Run"] = relationship("Run", back_populates="artifacts")
    disasm: Mapped[Optional["BinaryDisasm"]] = relationship("BinaryDisasm", back_populates="artifact", uselist=False)

class BinaryDisasm(Base):
    __tablename__ = "binary_disasm"

    artifact_id: Mapped[str] = mapped_column(String, ForeignKey("artifacts.artifact_id"), primary_key=True)
    disasm_text: Mapped[str] = mapped_column(Text)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    tool_version: Mapped[str] = mapped_column(String) # objdump version

    artifact: Mapped["Artifact"] = relationship("Artifact", back_populates="disasm")

class LogMeta(Base):
    __tablename__ = "log_meta"

    run_id: Mapped[str] = mapped_column(String, ForeignKey("runs.run_id"), primary_key=True)
    has_log: Mapped[bool] = mapped_column(Boolean, default=False)
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    run: Mapped["Run"] = relationship("Run", back_populates="log_meta")

class CodeMetricSnapshot(Base):
    __tablename__ = "code_metrics"

    run_id: Mapped[str] = mapped_column(String, ForeignKey("runs.run_id"), primary_key=True)
    total_loc: Mapped[int] = mapped_column(Integer, default=0)
    loc_by_dir: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    loc_by_lang: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    run: Mapped["Run"] = relationship("Run", back_populates="code_metrics")

class SignalStream(Base):
    __tablename__ = "signal_streams"

    signal_id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    device_run_id: Mapped[str] = mapped_column(String, ForeignKey("device_runs.run_id"))
    mime_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    url_or_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    device_run: Mapped["DeviceRun"] = relationship("DeviceRun", back_populates="signals")
