"""
Simple authentication middleware for EVOL WebUI.

Provides optional Basic HTTP authentication based on environment variables.
If EVOL_UI_USERNAME and EVOL_UI_PASSWORD are not set, authentication is disabled.
"""
import secrets
import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials


security = HTTPBasic()


def get_auth_credentials() -> Optional[tuple[str, str]]:
    """
    Get authentication credentials from environment variables.
    
    Returns:
        Tuple of (username, password) if configured, None otherwise.
    """
    username = os.getenv("EVOL_UI_USERNAME")
    password = os.getenv("EVOL_UI_PASSWORD")
    
    if not username or not password:
        return None
    
    return (username, password)


def verify_credentials(
    credentials: HTTPBasicCredentials = Depends(security)
) -> Optional[str]:
    """
    Verify HTTP Basic authentication credentials.
    
    Uses timing-attack-resistant comparison.
    
    Args:
        credentials: HTTP Basic credentials from request
        
    Returns:
        Username if authentication succeeds or is disabled
        
    Raises:
        HTTPException: If authentication fails
    """
    auth = get_auth_credentials()
    
    if auth is None:
        # Authentication is not configured - skip verification
        return None
    
    username, password = auth
    
    # Timing attack resistant comparison
    is_username_correct = secrets.compare_digest(
        credentials.username.encode("utf8"),
        username.encode("utf8") 
    )
    is_password_correct = secrets.compare_digest(
        credentials.password.encode("utf8"),
        password.encode("utf8")
    )
    
    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username


def get_current_user_optional() -> Optional[str]:
    """
    Dependency to get current user if authentication is enabled.
    
    Returns None if authentication is not configured.
    """
    auth = get_auth_credentials()
    if auth is None:
        return None
    return Depends(verify_credentials)
