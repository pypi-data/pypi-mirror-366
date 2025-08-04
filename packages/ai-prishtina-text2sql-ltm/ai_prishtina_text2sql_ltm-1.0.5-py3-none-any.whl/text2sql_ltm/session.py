"""
Session management for the Text2SQL-LTM library.

This module provides comprehensive session management with user isolation,
security, and lifecycle management with full type safety.
"""

from __future__ import annotations

import asyncio
import uuid
import logging
from typing import Dict, List, Optional, Any, AsyncContextManager
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from .config import SecurityConfig, PerformanceConfig
from .types import (
    UserID, SessionID, QueryID, UserSession, Timestamp,
    validate_user_id, validate_session_id
)
from .exceptions import (
    SessionError, SessionNotFoundError, SessionExpiredError,
    SessionLimitExceededError, SecurityError
)

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Production-grade session manager with comprehensive security and lifecycle management.

    This class provides:
    - Type-safe session creation and management
    - User isolation and security validation
    - Session lifecycle management with automatic cleanup
    - Concurrent session limits and monitoring
    - Comprehensive audit logging and metrics
    """

    def __init__(
        self,
        security_config: SecurityConfig,
        performance_config: PerformanceConfig
    ):
        """
        Initialize the session manager.

        Args:
            security_config: Security configuration settings
            performance_config: Performance configuration settings
        """
        self.security_config = security_config
        self.performance_config = performance_config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # State tracking
        self._initialized = False
        self._closed = False

        # Session storage
        self._sessions: Dict[SessionID, UserSession] = {}
        self._user_sessions: Dict[UserID, List[SessionID]] = {}

        # Cleanup and monitoring
        self._cleanup_task: Optional[asyncio.Task] = None
        self._session_metrics: Dict[str, int] = {
            "total_sessions": 0,
            "active_sessions": 0,
            "expired_sessions": 0,
            "sessions_created": 0,
            "sessions_deleted": 0,
        }

        # Async locks for thread safety
        self._sessions_lock = asyncio.Lock()
        self._metrics_lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Initialize the session manager."""
        if self._initialized:
            return

        try:
            self.logger.info("Initializing SessionManager...")

            # Start cleanup task
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())

            self._initialized = True
            self.logger.info("SessionManager initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize SessionManager: {str(e)}")
            raise SessionError(
                "Session manager initialization failed",
                details={"error": str(e)},
                cause=e
            ) from e

    async def close(self) -> None:
        """Close the session manager and clean up resources."""
        if self._closed:
            return

        try:
            self.logger.info("Closing SessionManager...")

            # Cancel cleanup task
            if self._cleanup_task:
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass

            # Clear all sessions
            async with self._sessions_lock:
                self._sessions.clear()
                self._user_sessions.clear()

            self._closed = True
            self.logger.info("SessionManager closed successfully")

        except Exception as e:
            self.logger.error(f"Error closing SessionManager: {str(e)}")
            raise SessionError(
                "Failed to close session manager",
                details={"error": str(e)},
                cause=e
            ) from e

    @asynccontextmanager
    async def session_context(self) -> AsyncContextManager[SessionManager]:
        """Async context manager for session manager lifecycle."""
        await self.initialize()
        try:
            yield self
        finally:
            await self.close()

    def _ensure_initialized(self) -> None:
        """Ensure the session manager is initialized."""
        if not self._initialized:
            raise SessionError("SessionManager not initialized. Call initialize() first.")

        if self._closed:
            raise SessionError("SessionManager is closed. Create a new instance.")

    async def create_session(
        self,
        user_id: str,
        context: Optional[Dict[str, Any]] = None,
        preferences: Optional[Dict[str, Any]] = None,
        expires_in_hours: Optional[int] = None
    ) -> UserSession:
        """
        Create a new user session with comprehensive validation.

        Args:
            user_id: User identifier
            context: Initial session context
            preferences: User preferences
            expires_in_hours: Session expiry time (uses config default if None)

        Returns:
            UserSession: Created session object

        Raises:
            SessionLimitExceededError: When user has too many active sessions
            SessionError: When session creation fails
        """
        self._ensure_initialized()

        try:
            # Validate user ID
            validated_user_id = validate_user_id(user_id)

            # Check session limits
            await self._check_session_limits(validated_user_id)

            # Generate session ID and timestamps
            session_id = SessionID(str(uuid.uuid4()))
            current_time = datetime.utcnow()

            # Calculate expiry time
            expiry_hours = expires_in_hours or self.security_config.token_expiry_hours
            expires_at = current_time + timedelta(hours=expiry_hours)

            # Create session object
            session = UserSession(
                session_id=session_id,
                user_id=validated_user_id,
                created_at=current_time,
                last_activity=current_time,
                context=context or {},
                query_history=[],
                preferences=preferences or {},
                is_active=True,
                expires_at=expires_at,
                metadata={
                    "created_by": "session_manager",
                    "user_agent": "",  # Would be populated from request context
                    "ip_address": "",  # Would be populated from request context
                }
            )

            # Store session
            async with self._sessions_lock:
                self._sessions[session_id] = session

                if validated_user_id not in self._user_sessions:
                    self._user_sessions[validated_user_id] = []
                self._user_sessions[validated_user_id].append(session_id)

            # Update metrics
            async with self._metrics_lock:
                self._session_metrics["total_sessions"] += 1
                self._session_metrics["active_sessions"] += 1
                self._session_metrics["sessions_created"] += 1

            self.logger.info(
                f"Session created successfully",
                extra={
                    "session_id": session_id,
                    "user_id": validated_user_id,
                    "expires_at": expires_at.isoformat()
                }
            )

            return session

        except Exception as e:
            if isinstance(e, (SessionLimitExceededError, SessionError)):
                raise

            self.logger.error(f"Failed to create session: {str(e)}")
            raise SessionError(
                "Session creation failed",
                details={"user_id": user_id, "error": str(e)},
                cause=e
            ) from e

    async def get_session(self, session_id: str) -> Optional[UserSession]:
        """
        Get a session by ID with validation.

        Args:
            session_id: Session identifier

        Returns:
            UserSession: Session object if found and valid, None otherwise
        """
        self._ensure_initialized()

        try:
            validated_session_id = validate_session_id(session_id)

            async with self._sessions_lock:
                session = self._sessions.get(validated_session_id)

            if not session:
                return None

            # Check if session is expired
            if session.is_expired():
                await self._expire_session(validated_session_id)
                return None

            # Update last activity
            session.update_activity()

            return session

        except Exception as e:
            self.logger.error(f"Failed to get session: {str(e)}")
            return None

    async def update_session(self, session: UserSession) -> None:
        """Update an existing session."""
        self._ensure_initialized()

        try:
            async with self._sessions_lock:
                if session.session_id in self._sessions:
                    self._sessions[session.session_id] = session

        except Exception as e:
            self.logger.error(f"Failed to update session: {str(e)}")
            raise SessionError(
                "Session update failed",
                details={"session_id": session.session_id, "error": str(e)},
                cause=e
            ) from e

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        self._ensure_initialized()

        try:
            validated_session_id = validate_session_id(session_id)

            async with self._sessions_lock:
                session = self._sessions.get(validated_session_id)
                if not session:
                    return False

                # Remove from sessions
                del self._sessions[validated_session_id]

                # Remove from user sessions
                user_sessions = self._user_sessions.get(session.user_id, [])
                if validated_session_id in user_sessions:
                    user_sessions.remove(validated_session_id)
                    if not user_sessions:
                        del self._user_sessions[session.user_id]

            # Update metrics
            async with self._metrics_lock:
                self._session_metrics["active_sessions"] -= 1
                self._session_metrics["sessions_deleted"] += 1

            self.logger.info(f"Session deleted: {session_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete session: {str(e)}")
            return False

    async def get_user_sessions(self, user_id: str) -> List[UserSession]:
        """Get all active sessions for a user."""
        self._ensure_initialized()

        try:
            validated_user_id = validate_user_id(user_id)

            async with self._sessions_lock:
                session_ids = self._user_sessions.get(validated_user_id, [])
                sessions = []

                for session_id in session_ids:
                    session = self._sessions.get(session_id)
                    if session and not session.is_expired():
                        sessions.append(session)

            return sessions

        except Exception as e:
            self.logger.error(f"Failed to get user sessions: {str(e)}")
            return []

    def get_metrics(self) -> Dict[str, int]:
        """Get session metrics."""
        return self._session_metrics.copy()

    # Helper methods

    async def _check_session_limits(self, user_id: UserID) -> None:
        """Check if user has exceeded session limits."""
        async with self._sessions_lock:
            user_session_ids = self._user_sessions.get(user_id, [])

            # Count active sessions
            active_count = 0
            for session_id in user_session_ids:
                session = self._sessions.get(session_id)
                if session and not session.is_expired():
                    active_count += 1

            if active_count >= self.security_config.max_sessions_per_user:
                raise SessionLimitExceededError(
                    user_id=str(user_id),
                    current_sessions=active_count,
                    max_sessions=self.security_config.max_sessions_per_user
                )

    async def _expire_session(self, session_id: SessionID) -> None:
        """Mark a session as expired and clean it up."""
        async with self._sessions_lock:
            session = self._sessions.get(session_id)
            if session:
                session.is_active = False

                # Remove from active sessions
                await self.delete_session(str(session_id))

                # Update metrics
                async with self._metrics_lock:
                    self._session_metrics["expired_sessions"] += 1

    async def _cleanup_expired_sessions(self) -> None:
        """Background task to clean up expired sessions."""
        while not self._closed:
            try:
                current_time = datetime.utcnow()
                expired_session_ids = []

                async with self._sessions_lock:
                    for session_id, session in self._sessions.items():
                        if session.is_expired():
                            expired_session_ids.append(session_id)

                # Clean up expired sessions
                for session_id in expired_session_ids:
                    await self._expire_session(session_id)

                if expired_session_ids:
                    self.logger.info(f"Cleaned up {len(expired_session_ids)} expired sessions")

                # Wait before next cleanup
                await asyncio.sleep(300)  # 5 minutes

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in session cleanup: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying