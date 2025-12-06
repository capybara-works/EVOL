"""
Unit tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient


class TestAPIEndpoints:
    """Test cases for API endpoints."""
    
    def test_list_runs_endpoint(self, api_client):
        """Test GET /api/v1/runs endpoint."""
        response = api_client.get("/api/v1/runs")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_list_runs_with_pagination(self, api_client):
        """Test pagination parameters."""
        response = api_client.get("/api/v1/runs?skip=0&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
    
    def test_list_runs_with_filter(self, api_client):
        """Test filtering by repo_id."""
        response = api_client.get("/api/v1/runs?repo_id=test/repo")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_list_artifacts_endpoint(self, api_client):
        """Test GET /api/v1/artifacts endpoint."""
        response = api_client.get("/api/v1/artifacts")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_list_ci_runs_endpoint(self, api_client):
        """Test GET /api/v1/ci-runs endpoint."""
        response = api_client.get("/api/v1/ci-runs")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_metrics_loc_endpoint(self, api_client):
        """Test GET /api/v1/metrics/loc endpoint."""
        response = api_client.get("/api/v1/metrics/loc")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "total" in data or isinstance(data, list)


class TestAPIPagination:
    """Test API pagination behavior."""
    
    def test_default_pagination(self, api_client):
        """Test default skip and limit values."""
        response = api_client.get("/api/v1/runs")
        
        assert response.status_code == 200
        # Default should return results (empty list is valid)
        assert isinstance(response.json(), list)
    
    def test_custom_limit(self, api_client):
        """Test custom limit parameter."""
        response = api_client.get("/api/v1/runs?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
    
    def test_skip_parameter(self, api_client):
        """Test skip parameter."""
        response = api_client.get("/api/v1/runs?skip=10")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
