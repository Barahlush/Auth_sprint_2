from __future__ import annotations

import abc
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional, Union

from etl_utils.backoff import backoff_function
from redis import Redis
from redis.exceptions import ConnectionError


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict[str, Any]) -> None:
        """Save state to the storage."""

    @abc.abstractmethod
    def retrieve_state(self) -> dict[str, Any]:
        """Load state from the storage."""


class State:
    """
    Class for keeping state while working with data.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.state = self.storage.retrieve_state() or {}

    def set_state(self, key: str, value: Any) -> None:
        self.state[key] = value
        self.storage.save_state(self.state)

    def get_state(self, key: str) -> Optional[Any]:
        return self.state.get(key)


def json_serializer(obj: Any) -> str:
    """JSON serializer for datetime objects."""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError('Type %s not serializable' % type(obj))


class JsonFileStorage(BaseStorage):
    """Local JSON file storage for states."""

    def __init__(self, file_path: Optional[Union[Path, str]] = None):
        self.file_path = (
            Path(file_path) if file_path else Path('storage.json').resolve()
        )
        if not self.file_path.exists():
            with self.file_path.open('w') as state_file:
                json.dump({}, state_file)

    def save_state(self, state: dict[str, Any]) -> None:
        with self.file_path.open('w') as state_file:
            json.dump(
                state, state_file, indent=4, sort_keys=True, default=json_serializer
            )

    def retrieve_state(self) -> Any:
        if not self.file_path.exists():
            with self.file_path.open('w') as state_file:
                json.dump({}, state_file)
        with self.file_path.open('r') as state_file:
            state = json.load(state_file)
        return state


class RedisStorage(BaseStorage):
    def __init__(self, redis_adapter: Redis[Any], name: str):
        self.redis_adapter = redis_adapter
        self.name = name

    @backoff_function(ConnectionError)
    def save_state(self, state: dict[str, Any]) -> None:
        self.redis_adapter.set(
            self.name,
            json.dumps(state, indent=4, sort_keys=True, default=json_serializer),
        )

    @backoff_function(ConnectionError)
    def retrieve_state(self) -> Any:
        state_str = self.redis_adapter.get(self.name)
        return json.loads(state_str) if state_str else None


class StatefulMixin:
    """Mixin and state wrapper for classes which require `last_modified` state."""

    def __init__(self, state: State, state_key: str):
        self.state = state
        self.state_key = state_key
        init_state = self.state.get_state(self.state_key)

        if init_state is None:
            self.state.set_state(self.state_key, datetime.min)
            self.last_modified = datetime.min
        else:
            self.last_modified = datetime.fromisoformat(init_state)

    def get_last_modified(self) -> datetime:
        return self.last_modified

    def set_last_modified(self, last_modified: datetime) -> None:
        self.last_modified = last_modified
        self.state.set_state(self.state_key, last_modified)
