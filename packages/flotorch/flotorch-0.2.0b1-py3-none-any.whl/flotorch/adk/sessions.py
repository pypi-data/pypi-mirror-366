from __future__ import annotations

import copy
import logging
import time
from typing import Any, Optional
import uuid

from typing_extensions import override

from flotorch.sdk.session import FlotorchSession
from google.adk.events.event import Event
from google.adk.base_session_service import BaseSessionService
from google.adk.base_session_service import GetSessionConfig
from google.adk.base_session_service import ListSessionsResponse
from google.adk.session import Session
from google.adk.state import State

logger = logging.getLogger('flotorch_adk.' + __name__)


class FlotorchADKSession(BaseSessionService):
    """A Flotorch-based implementation of the session service.

    Uses FlotorchSession from SDK for session management while maintaining
    ADK-compatible interface.
    """

    def __init__(self, api_key: str, base_url: str):
        """Initialize FlotorchADKSession.

        Args:
            api_key: The API key for Flotorch service.
            base_url: The base URL for Flotorch service.
        """
        # Flotorch session for session management
        self._flotorch_session = FlotorchSession(
            api_key=api_key,
            base_url=base_url,
        )
        
        # In-memory state management (for app_state and user_state)
        # These are kept in memory as they're not part of FlotorchSession
        self.user_state: dict[str, dict[str, dict[str, Any]]] = {}
        self.app_state: dict[str, dict[str, Any]] = {}

    @override
    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        state: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Session:
        return self._create_session_impl(
            app_name=app_name,
            user_id=user_id,
            state=state,
            session_id=session_id,
        )

    def create_session_sync(
        self,
        *,
        app_name: str,
        user_id: str,
        state: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Session:
        logger.warning('Deprecated. Please migrate to the async method.')
        return self._create_session_impl(
            app_name=app_name,
            user_id=user_id,
            state=state,
            session_id=session_id,
        )

    def _create_session_impl(
        self,
        *,
        app_name: str,
        user_id: str,
        state: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Session:
        session_id = (
            session_id.strip()
            if session_id and session_id.strip()
            else str(uuid.uuid4())
        )
        
        # Create session using FlotorchSession
        session_data = self._flotorch_session.create(
            app_name=app_name,
            user_id=user_id,
            uid=session_id,
            state=state or {},
        )
        
        # Create ADK Session object
        session = Session(
            app_name=app_name,
            user_id=user_id,
            id=session_id,
            state=session_data.get('state', {}),
            last_update_time=session_data.get('last_update_time', time.time()),
        )

        copied_session = copy.deepcopy(session)
        return self._merge_state(app_name, user_id, copied_session)

    @override
    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: Optional[GetSessionConfig] = None,
    ) -> Optional[Session]:
        return self._get_session_impl(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            config=config,
        )

    def get_session_sync(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: Optional[GetSessionConfig] = None,
    ) -> Optional[Session]:
        logger.warning('Deprecated. Please migrate to the async method.')
        return self._get_session_impl(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            config=config,
        )

    def _get_session_impl(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: Optional[GetSessionConfig] = None,
    ) -> Optional[Session]:
        # Get session using FlotorchSession
        session_data = self._flotorch_session.get(
            uid=session_id,
            after_timestamp=config.after_timestamp if config else None,
            num_recent_events=config.num_recent_events if config else None,
        )
        
        if not session_data:
            return None

        # Create ADK Session object
        session = Session(
            app_name=app_name,
            user_id=user_id,
            id=session_id,
            state=session_data.get('state', {}),
            last_update_time=session_data.get('last_update_time', time.time()),
        )
        
        # Add events if available
        events_data = session_data.get('events', [])
        session.events = [
            self._convert_flotorch_event_to_adk(event_data)
            for event_data in events_data
        ]

        copied_session = copy.deepcopy(session)
        return self._merge_state(app_name, user_id, copied_session)

    def _merge_state(
        self, app_name: str, user_id: str, copied_session: Session
    ) -> Session:
        # Merge app state
        if app_name in self.app_state:
            for key in self.app_state[app_name].keys():
                copied_session.state[State.APP_PREFIX + key] = self.app_state[app_name][
                    key
                ]

        if (
            app_name not in self.user_state
            or user_id not in self.user_state[app_name]
        ):
            return copied_session

        # Merge session state with user state.
        for key in self.user_state[app_name][user_id].keys():
            copied_session.state[State.USER_PREFIX + key] = self.user_state[app_name][
                user_id
            ][key]
        return copied_session

    @override
    async def list_sessions(
        self, *, app_name: str, user_id: str
    ) -> ListSessionsResponse:
        return self._list_sessions_impl(app_name=app_name, user_id=user_id)

    def list_sessions_sync(
        self, *, app_name: str, user_id: str
    ) -> ListSessionsResponse:
        logger.warning('Deprecated. Please migrate to the async method.')
        return self._list_sessions_impl(app_name=app_name, user_id=user_id)

    def _list_sessions_impl(
        self, *, app_name: str, user_id: str
    ) -> ListSessionsResponse:
        # List sessions using FlotorchSession
        sessions_data = self._flotorch_session.list(
            app_name=app_name,
            user_id=user_id,
        )
        
        sessions_without_events = []
        for session_data in sessions_data:
            session = Session(
                app_name=app_name,
                user_id=user_id,
                id=session_data.get('uid', ''),
                state=session_data.get('state', {}),
                last_update_time=session_data.get('last_update_time', time.time()),
            )
            session.events = []  # Don't include events in list response
            copied_session = copy.deepcopy(session)
            copied_session = self._merge_state(app_name, user_id, copied_session)
            sessions_without_events.append(copied_session)
            
        return ListSessionsResponse(sessions=sessions_without_events)

    @override
    async def delete_session(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> None:
        self._delete_session_impl(
            app_name=app_name, user_id=user_id, session_id=session_id
        )

    def delete_session_sync(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> None:
        logger.warning('Deprecated. Please migrate to the async method.')
        self._delete_session_impl(
            app_name=app_name, user_id=user_id, session_id=session_id
        )

    def _delete_session_impl(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> None:
        if (
            self._get_session_impl(
                app_name=app_name, user_id=user_id, session_id=session_id
            )
            is None
        ):
            return

        # Delete session using FlotorchSession
        self._flotorch_session.delete(session_id)

    @override
    async def append_event(self, session: Session, event: Event) -> Event:
        # Update the in-memory session.
        await super().append_event(session=session, event=event)
        session.last_update_time = event.timestamp

        # Update the storage session
        app_name = session.app_name
        user_id = session.user_id
        session_id = session.id

        def _warning(message: str) -> None:
            logger.warning(
                f'Failed to append event to session {session_id}: {message}'
            )

        # Verify session exists
        session_data = self._flotorch_session.get(uid=session_id)
        if not session_data:
            _warning(f'session_id {session_id} not found in FlotorchSession')
            return event

        # Handle state delta updates
        if event.actions and event.actions.state_delta:
            for key in event.actions.state_delta:
                if key.startswith(State.APP_PREFIX):
                    self.app_state.setdefault(app_name, {})[
                        key.removeprefix(State.APP_PREFIX)
                    ] = event.actions.state_delta[key]

                if key.startswith(State.USER_PREFIX):
                    self.user_state.setdefault(app_name, {}).setdefault(user_id, {})[
                        key.removeprefix(State.USER_PREFIX)
                    ] = event.actions.state_delta[key]

        # Add event using FlotorchSession
        event_data = self._convert_adk_event_to_flotorch(event)
        self._flotorch_session.add_event(
            uid=session_id,
            invocation_id=event.invocation_id,
            author=event.author,
            content=event_data.get('content'),
            actions=event_data.get('actions'),
            **event_data.get('metadata', {})
        )

        return event

    def _convert_flotorch_event_to_adk(self, event_data: dict[str, Any]) -> Event:
        """Convert Flotorch event data to ADK Event object."""
        # This is a placeholder - you'll need to implement the actual conversion
        # based on your Flotorch event structure
        from google.adk.events.event_actions import EventActions
        
        event_actions = EventActions()
        if event_data.get('actions'):
            event_actions = EventActions(
                state_delta=event_data['actions'].get('state_delta', {}),
                # Add other action fields as needed
            )

        event = Event(
            id=event_data.get('uid_event', ''),
            invocation_id=event_data.get('invocation_id', ''),
            author=event_data.get('author', ''),
            actions=event_actions,
            content=event_data.get('content'),
            timestamp=event_data.get('timestamp', time.time()),
            error_code=event_data.get('error_code'),
            error_message=event_data.get('error_message'),
        )
        
        return event

    def _convert_adk_event_to_flotorch(self, event: Event) -> dict[str, Any]:
        """Convert ADK Event object to Flotorch event data."""
        event_data = {
            'content': event.content,
            'actions': {},
            'metadata': {}
        }
        
        if event.actions:
            event_data['actions'] = {
                'state_delta': event.actions.state_delta or {},
                # Add other action fields as needed
            }
        
        if event.partial is not None:
            event_data['metadata']['partial'] = event.partial
        if event.turn_complete is not None:
            event_data['metadata']['turn_complete'] = event.turn_complete
        if event.interrupted is not None:
            event_data['metadata']['interrupted'] = event.interrupted
        if event.branch:
            event_data['metadata']['branch'] = event.branch
        if event.custom_metadata:
            event_data['metadata']['custom_metadata'] = event.custom_metadata
        if event.long_running_tool_ids:
            event_data['metadata']['long_running_tool_ids_json'] = list(event.long_running_tool_ids)
        if event.grounding_metadata:
            event_data['metadata']['grounding_metadata'] = event.grounding_metadata
            
        return event_data
