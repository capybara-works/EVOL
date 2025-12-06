"""
Unit tests for database models.
"""
import pytest
from datetime import datetime
from evol.db.models import Run, CIRun, Artifact


class TestRunModel:
    """Test cases for Run model."""
    
    def test_create_run(self, test_db):
        """Test creating a Run instance."""
        run = Run(
            run_id="test-run-123",
            kind="ci",
            repo_id="test/repo",
            commit_sha="abc123def456",
            started_at=datetime.utcnow(),
            status="success"
        )
        
        test_db.add(run)
        test_db.commit()
        
        assert run.run_id == "test-run-123"
        assert run.kind == "ci"
        assert run.status == "success"
    
    def test_run_relationships(self, test_db):
        """Test Run model relationships."""
        run = Run(
            run_id="test-run-456",
            kind="ci",
            status="success"
        )
        
        test_db.add(run)
        test_db.commit()
        
        # Verify the run was created
        queried_run = test_db.query(Run).filter_by(run_id="test-run-456").first()
        assert queried_run is not None
        assert queried_run.run_id == "test-run-456"


class TestCIRunModel:
    """Test cases for CIRun model."""
    
    def test_create_ci_run(self, test_db):
        """Test creating a CIRun instance."""
        # First create a parent Run
        run = Run(
            run_id="parent-run-123",
            kind="ci",
            status="success"
        )
        test_db.add(run)
        test_db.commit()
        
        # Create CIRun with actual fields from model
        ci_run = CIRun(
            run_id="parent-run-123",
            trigger="push",
            duration_seconds=120.5,
            default_branch="main",
            tag_count=5,
            branch_count=10
        )
        
        test_db.add(ci_run)
        test_db.commit()
        
        assert ci_run.run_id == "parent-run-123"
        assert ci_run.trigger == "push"
        assert ci_run.duration_seconds == 120.5


class TestArtifactModel:
    """Test cases for Artifact model."""
    
    def test_create_artifact(self, test_db):
        """Test creating an Artifact instance."""
        # Create parent Run
        run = Run(
            run_id="run-with-artifact",
            kind="ci",
            status="success"
        )
        test_db.add(run)
        test_db.commit()
        
        # Create Artifact with actual fields from model
        artifact = Artifact(
            artifact_id="artifact-123",
            run_id="run-with-artifact",
            name="test-artifact.zip",
            file_type="binary",  # Correct field name
            size_bytes=1024
        )
        
        test_db.add(artifact)
        test_db.commit()
        
        assert artifact.artifact_id == "artifact-123"
        assert artifact.name == "test-artifact.zip"
        assert artifact.size_bytes == 1024
