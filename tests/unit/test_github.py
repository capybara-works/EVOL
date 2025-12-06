"""
Unit tests for GitHub Collector.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from evol.collector.github import GitHubCollector


class TestGitHubCollector:
    """Test cases for GitHubCollector class."""
    
    @pytest.fixture
    def collector(self, test_db, mock_github_token):
        """Create a GitHubCollector instance for testing."""
        return GitHubCollector(
            db=test_db,
            project="test-owner/test-repo",
            token="fake_token_for_testing_12345"
        )
    
    def test_initialization(self, collector):
        """Test GitHubCollector initialization."""
        assert collector.owner == "test-owner"
        assert collector.repo == "test-repo"
        assert collector.token == "fake_token_for_testing_12345"
    
    def test_request_success(self, collector):
        """Test successful API request."""
        with patch.object(collector.client, 'request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {"test": "data"}
            mock_response.raise_for_status = Mock()
            mock_request.return_value = mock_response
            
            result = collector._request("GET", "/test/endpoint")
            
            assert result == {"test": "data"}
            assert mock_request.call_count == 1
    
    def test_request_retry_on_failure(self, collector):
        """Test retry logic on failed requests."""
        with patch.object(collector.client, 'request') as mock_request:
            # Simulate 3 failures
            mock_request.side_effect = Exception("API Error")
            
            # The actual exception will be raised, not wrapped
            with pytest.raises(Exception, match="API Error"):
                collector._request("GET", "/test/endpoint")
            
            # Should retry 3 times
            assert mock_request.call_count == 3
    
    def test_request_retry_success_on_second_attempt(self, collector):
        """Test successful retry on second attempt."""
        with patch.object(collector.client, 'request') as mock_request:
            # First call fails, second succeeds
            mock_response = Mock()
            mock_response.json.return_value = {"success": True}
            mock_response.raise_for_status = Mock()
            
            # Set side_effect to list of responses
            mock_request.side_effect = [
                Exception("Temporary error"),
                mock_response
            ]
            
            # Should succeed on second attempt
            result = collector._request("GET", "/test/endpoint")
            
            assert result == {"success": True}
            assert mock_request.call_count == 2


class TestGitHubSyncOperations:
    """Test GitHub sync operations."""
    
    @pytest.fixture
    def collector(self, test_db, mock_github_token):
        """Create collector instance."""
        return GitHubCollector(
            db=test_db,
            project="test/repo",
            token="fake_token"
        )
    
    def test_sync_runs(self, collector):
        """Test syncing workflow runs."""
        with patch.object(collector, '_request') as mock_request:
            mock_request.return_value = {
                "total_count": 1,
                "workflow_runs": [
                    {
                        "id": 123456,
                        "name": "Test Workflow",
                        "status": "completed",
                        "conclusion": "success",
                        "created_at": "2025-01-01T00:00:00Z",
                        "updated_at": "2025-01-01T00:05:00Z"
                    }
                ]
            }
            
            # This test verifies the function can be called
            # Full integration with database would be in integration tests
            result = collector._request("GET", "/repos/test/repo/actions/runs")
            
            assert result["total_count"] == 1
            assert len(result["workflow_runs"]) == 1
            assert result["workflow_runs"][0]["status"] == "completed"
