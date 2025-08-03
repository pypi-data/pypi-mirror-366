"""Tests for authentication functionality."""

import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from flow._internal.auth import AuthConfig, Authenticator, Session
from flow.errors import AuthenticationError


class TestAuthConfig:
    """Test authentication configuration."""

    def test_api_key_from_env(self, monkeypatch):
        """Test loading API key from environment.
        
        GIVEN: FCP_API_KEY environment variable is set
        WHEN: AuthConfig is initialized
        THEN: API key is loaded from environment
        """
        # GIVEN
        monkeypatch.setenv("FCP_API_KEY", "test-key-123")

        # WHEN
        config = AuthConfig()

        # THEN
        assert config.api_key == "test-key-123"
        assert config.has_api_key is True
        assert config.has_credentials is False

    def test_api_key_explicit(self, monkeypatch):
        """Test explicit API key takes precedence.
        
        GIVEN: API key provided explicitly and in env
        WHEN: AuthConfig is initialized
        THEN: Explicit key is used
        """
        # GIVEN
        monkeypatch.setenv("FCP_API_KEY", "env-key")

        # WHEN
        config = AuthConfig(api_key="explicit-key")

        # THEN
        assert config.api_key == "explicit-key"

    def test_email_password_auth(self):
        """Test email/password configuration.
        
        GIVEN: Email and password provided
        WHEN: AuthConfig is initialized
        THEN: Credentials are properly set
        """
        # GIVEN/WHEN
        config = AuthConfig(email="test@example.com", password="secret123")

        # THEN
        assert config.email == "test@example.com"
        assert config.password == "secret123"
        assert config.has_credentials is True
        assert config.has_api_key is False

    def test_default_session_file(self, tmp_path, monkeypatch):
        """Test default session file location.
        
        GIVEN: No session file specified
        WHEN: AuthConfig is initialized
        THEN: Default location is used
        """
        # GIVEN
        monkeypatch.setenv("HOME", str(tmp_path))

        # WHEN
        config = AuthConfig()

        # THEN
        expected = tmp_path / ".flow" / "session.json"
        assert config.session_file == expected
        assert expected.parent.exists()  # Directory should be created

    def test_custom_session_file(self, tmp_path):
        """Test custom session file location.
        
        GIVEN: Custom session file path
        WHEN: AuthConfig is initialized
        THEN: Custom path is used
        """
        # GIVEN
        custom_path = tmp_path / "custom" / "session.json"

        # WHEN
        config = AuthConfig(session_file=custom_path)

        # THEN
        assert config.session_file == custom_path


class TestSession:
    """Test session management."""

    def test_session_creation(self):
        """Test session object creation.
        
        GIVEN: Session parameters
        WHEN: Session is created
        THEN: Properties are set correctly
        """
        # GIVEN
        token = "session-token-123"
        expires_at = datetime.now() + timedelta(hours=1)
        user_id = "user-456"

        # WHEN
        session = Session(token=token, expires_at=expires_at, user_id=user_id)

        # THEN
        assert session.token == token
        assert session.expires_at == expires_at
        assert session.user_id == user_id
        assert session.is_valid is True

    def test_session_expiry(self):
        """Test session expiration checking.
        
        GIVEN: Sessions with different expiry times
        WHEN: Validity is checked
        THEN: Correct status is returned
        """
        # GIVEN
        valid_session = Session(
            token="valid",
            expires_at=datetime.now() + timedelta(hours=1),
            user_id="user1"
        )

        expired_session = Session(
            token="expired",
            expires_at=datetime.now() - timedelta(hours=1),
            user_id="user2"
        )

        # WHEN/THEN
        assert valid_session.is_valid is True
        assert expired_session.is_valid is False

    def test_session_serialization(self):
        """Test session to/from dict conversion.
        
        GIVEN: Session object
        WHEN: Converted to dict and back
        THEN: Session is preserved
        """
        # GIVEN
        original = Session(
            token="test-token",
            expires_at=datetime.now() + timedelta(hours=2),
            user_id="user-123"
        )

        # WHEN
        data = original.to_dict()
        restored = Session.from_dict(data)

        # THEN
        assert restored.token == original.token
        assert restored.user_id == original.user_id
        # Allow small time difference due to serialization
        time_diff = abs((restored.expires_at - original.expires_at).total_seconds())
        assert time_diff < 1


class TestAuthenticator:
    """Test authentication flow."""

    @pytest.fixture
    def mock_http_client(self):
        """Mock HTTP client for testing."""
        return MagicMock()

    def test_authenticate_with_api_key(self, mock_http_client):
        """Test authentication using API key.
        
        GIVEN: API key is configured
        WHEN: authenticate() is called
        THEN: API key is returned directly
        """
        # GIVEN
        config = AuthConfig(api_key="test-api-key")
        auth = Authenticator(config, mock_http_client)

        # WHEN
        token = auth.authenticate()

        # THEN
        assert token == "test-api-key"
        # No HTTP calls should be made
        mock_http_client.post.assert_not_called()

    def test_authenticate_with_valid_session(self, mock_http_client):
        """Test authentication with existing valid session.
        
        GIVEN: Valid session exists
        WHEN: authenticate() is called
        THEN: Session token is returned
        """
        # GIVEN
        config = AuthConfig()
        auth = Authenticator(config, mock_http_client)

        valid_session = Session(
            token="session-token",
            expires_at=datetime.now() + timedelta(hours=1),
            user_id="user-123"
        )
        auth._session = valid_session

        # WHEN
        token = auth.authenticate()

        # THEN
        assert token == "session-token"
        mock_http_client.post.assert_not_called()

    def test_authenticate_load_saved_session(self, mock_http_client, tmp_path):
        """Test loading session from file.
        
        GIVEN: Valid session saved to file
        WHEN: authenticate() is called
        THEN: Session is loaded and token returned
        """
        # GIVEN
        session_file = tmp_path / "session.json"
        saved_session = {
            "token": "saved-token",
            "expires_at": (datetime.now() + timedelta(hours=1)).isoformat(),
            "user_id": "user-123"
        }
        session_file.write_text(json.dumps(saved_session))

        config = AuthConfig(session_file=session_file)
        auth = Authenticator(config, mock_http_client)

        # WHEN
        token = auth.authenticate()

        # THEN
        assert token == "saved-token"
        assert auth._session is not None
        assert auth._session.token == "saved-token"

    def test_authenticate_with_credentials(self, mock_http_client, tmp_path):
        """Test authentication with email/password.
        
        GIVEN: Email and password configured
        WHEN: authenticate() is called
        THEN: Login endpoint is called and session created
        """
        # GIVEN
        config = AuthConfig(
            email="test@example.com",
            password="secret123",
            session_file=tmp_path / "session.json"
        )
        auth = Authenticator(config, mock_http_client)

        # Mock login response
        mock_http_client.request.return_value = {
            "token": "new-session-token",
            "expires_in": 3600,
            "user_id": "user-456"
        }

        # WHEN
        token = auth.authenticate()

        # THEN
        assert token == "new-session-token"
        mock_http_client.request.assert_called_once_with(
            method="POST",
            url="/auth/login",
            json={"email": "test@example.com", "password": "secret123"},
            retry_server_errors=False
        )

        # Verify session was saved
        assert config.session_file.exists()
        saved_data = json.loads(config.session_file.read_text())
        assert saved_data["token"] == "new-session-token"

    def test_authenticate_no_method_available(self, mock_http_client):
        """Test authentication with no valid method.
        
        GIVEN: No API key or credentials
        WHEN: authenticate() is called
        THEN: AuthenticationError is raised
        """
        # GIVEN
        config = AuthConfig()  # No API key or credentials
        auth = Authenticator(config, mock_http_client)

        # WHEN/THEN
        with pytest.raises(AuthenticationError) as exc_info:
            auth.authenticate()

        assert "No valid authentication method" in str(exc_info.value)
        assert "FCP_API_KEY" in str(exc_info.value)

    def test_session_refresh_on_expiry(self, mock_http_client, tmp_path):
        """Test automatic session refresh when expired.
        
        GIVEN: Expired session with valid credentials
        WHEN: authenticate() is called
        THEN: New session is obtained
        """
        # GIVEN
        config = AuthConfig(
            email="test@example.com",
            password="secret123",
            session_file=tmp_path / "session.json"
        )
        auth = Authenticator(config, mock_http_client)

        # Set expired session
        expired_session = Session(
            token="expired-token",
            expires_at=datetime.now() - timedelta(hours=1),
            user_id="user-123"
        )
        auth._session = expired_session

        # Mock new login
        mock_http_client.request.return_value = {
            "token": "refreshed-token",
            "expires_in": 3600,
            "user_id": "user-123"
        }

        # WHEN
        token = auth.authenticate()

        # THEN
        assert token == "refreshed-token"
        assert auth._session.token == "refreshed-token"
        assert auth._session.is_valid is True


    def test_logout(self, mock_http_client, tmp_path):
        """Test logout functionality.
        
        GIVEN: Active session
        WHEN: logout() is called
        THEN: Session is cleared and file deleted
        """
        # GIVEN
        session_file = tmp_path / "session.json"
        session_file.write_text('{"token": "test"}')

        config = AuthConfig(session_file=session_file)
        auth = Authenticator(config, mock_http_client)
        auth._session = Session(
            token="active-token",
            expires_at=datetime.now() + timedelta(hours=1),
            user_id="user-123"
        )

        # WHEN
        auth.logout()

        # THEN
        assert auth._session is None
        assert not session_file.exists()
        mock_http_client.request.assert_called_once_with(
            method="POST",
            url="/auth/logout",
            headers={"Authorization": "Bearer active-token"}
        )


class TestAuthIntegration:
    """Integration tests for authentication flow."""

    def test_full_api_key_flow(self, tmp_path, monkeypatch):
        """Test complete API key authentication flow.
        
        GIVEN: API key in environment
        WHEN: Full auth flow is executed
        THEN: Can make authenticated requests
        """
        # GIVEN
        monkeypatch.setenv("FCP_API_KEY", "integration-test-key")
        monkeypatch.setenv("HOME", str(tmp_path))

        # Create mock HTTP client
        mock_http = MagicMock()
        mock_http.post.return_value = {"status": "ok"}

        # WHEN
        config = AuthConfig()
        auth = Authenticator(config, mock_http)
        token = auth.authenticate()

        # THEN
        assert token == "integration-test-key"

    def test_full_credential_flow(self, tmp_path):
        """Test complete email/password authentication flow.
        
        GIVEN: Email and password credentials
        WHEN: Full auth flow is executed
        THEN: Session is created and persisted
        """
        # GIVEN
        mock_http = MagicMock()
        mock_http.request.return_value = {
            "token": "session-abc123",
            "expires_in": 7200,
            "user_id": "user-789"
        }

        # WHEN
        config = AuthConfig(
            email="user@example.com",
            password="password123",
            session_file=tmp_path / "session.json"
        )
        auth = Authenticator(config, mock_http)

        # First authentication creates session
        token1 = auth.authenticate()

        # Second authentication uses cached session
        auth2 = Authenticator(config, mock_http)
        token2 = auth2.authenticate()

        # THEN
        assert token1 == "session-abc123"
        assert token2 == "session-abc123"
        # Login should only be called once
        mock_http.request.assert_called_once()

        # Verify session file exists
        assert config.session_file.exists()
        saved = json.loads(config.session_file.read_text())
        assert saved["token"] == "session-abc123"
        assert saved["user_id"] == "user-789"
