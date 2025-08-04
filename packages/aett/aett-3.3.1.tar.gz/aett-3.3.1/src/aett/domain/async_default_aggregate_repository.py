import datetime
import inspect
import logging
import uuid
from typing import Type, Dict

from pydantic_core import from_json

from aett.domain import Aggregate
from aett.domain.async_aggregate_repository import AsyncAggregateRepository
from aett.eventstore import (
    ICommitEventsAsync,
    IAccessSnapshotsAsync,
    MAX_INT,
    Commit,
    Snapshot,
)


class AsyncDefaultAggregateRepository(AsyncAggregateRepository):
    def __init__(
        self,
        tenant_id: str,
        store: ICommitEventsAsync,
        snapshot_store: IAccessSnapshotsAsync,
        logger: logging.Logger | None = None,
    ):
        """
        Initialize the default aggregate repository.

        :param tenant_id: The tenant id of the repository instance
        :param store: The event store to use
        :param snapshot_store: The snapshot store to use
        """
        self._tenant_id = tenant_id
        self._store = store
        self._snapshot_store = snapshot_store
        self._logger = (
            logger
            if logger is not None
            else logging.getLogger(AsyncDefaultAggregateRepository.__name__)
        )

    async def get(
        self,
        cls: Type[AsyncAggregateRepository.TAggregate],
        stream_id: str,
        max_version: int = MAX_INT,
    ) -> AsyncAggregateRepository.TAggregate:
        self._logger.debug(
            f"Getting aggregate {cls.__name__} with id {stream_id} at version {max_version}"
        )
        snapshot = await self._snapshot_store.get(
            tenant_id=self._tenant_id, stream_id=stream_id, max_revision=max_version
        )
        min_version = 0
        commit_sequence = 0
        if snapshot is not None:
            min_version = snapshot.stream_revision + 1
            commit_sequence = snapshot.commit_sequence
        commits = []
        ita = self._store.get(
            tenant_id=self._tenant_id,
            stream_id=stream_id,
            min_revision=min_version,
            max_revision=max_version,
        )
        async for x in ita:
            commits.append(x)
        if len(commits) > 0:
            commit_sequence = commits[-1].commit_sequence
        memento_type = (
            inspect.signature(cls.apply_memento).parameters["memento"].annotation
        )
        aggregate: Aggregate = cls(
            stream_id,
            commit_sequence,
            memento_type(**from_json(snapshot.payload))
            if snapshot is not None
            else None,
        )
        for commit in commits:
            for event in commit.events:
                aggregate.raise_event(event.body)
        aggregate.uncommitted.clear()
        return aggregate

    async def get_to(
        self,
        cls: Type[AsyncAggregateRepository.TAggregate],
        stream_id: str,
        max_time: datetime.datetime = datetime.datetime.max,
    ) -> AsyncAggregateRepository.TAggregate:
        self._logger.debug(
            f"Getting aggregate {cls.__name__} with id {stream_id} at time point {max_time:%Y%m%d-%H%M%S%z}"
        )
        ait = self._store.get_to(
            tenant_id=self._tenant_id, stream_id=stream_id, max_time=max_time
        )
        commits = [x async for x in ait]
        commit_sequence = commits[-1].commit_sequence if len(commits) > 0 else 0
        aggregate = cls(stream_id, commit_sequence, None)
        for commit in commits:
            for event in commit.events:
                aggregate.raise_event(event.body)
        aggregate.uncommitted.clear()
        return aggregate

    async def save(
        self,
        aggregate: AsyncAggregateRepository.TAggregate,
        headers: Dict[str, str] | None = None,
    ) -> None:
        self._logger.debug(
            f"Saving aggregate {aggregate.id} at version {aggregate.version}"
        )
        if headers is None:
            headers = {}
        if len(aggregate.uncommitted) == 0:
            return
        commit = Commit(
            tenant_id=self._tenant_id,
            stream_id=aggregate.id,
            stream_revision=aggregate.version,
            commit_id=uuid.uuid4(),
            commit_sequence=aggregate.commit_sequence + 1,
            commit_stamp=datetime.datetime.now(datetime.timezone.utc),
            headers=dict(headers),
            events=list(aggregate.uncommitted),
            checkpoint_token=0,
        )
        await self._store.commit(commit)
        self._logger.debug(f"Saved aggregate {aggregate.id}")
        aggregate.uncommitted.clear()

    async def snapshot(
        self,
        cls: Type[AsyncAggregateRepository.TAggregate],
        stream_id: str,
        version: int = MAX_INT,
        headers: Dict[str, str] | None = None,
    ) -> None:
        self._logger.debug(
            f"Snapshotting aggregate {cls.__name__} with id {stream_id} at version {version}"
        )
        agg = await self.get(cls, stream_id, version)
        await self._snapshot_aggregate(agg, headers)

    async def snapshot_at(
        self,
        cls: Type[AsyncAggregateRepository.TAggregate],
        stream_id: str,
        cut_off: datetime.datetime,
        headers: Dict[str, str] | None = None,
    ) -> None:
        self._logger.debug(
            f"Snapshotting aggregate {cls.__name__} with id {stream_id} at time point {cut_off:%Y%m%d-%H%M%S%z}"
        )
        agg = await self.get_to(cls, stream_id, cut_off)
        await self._snapshot_aggregate(agg, headers)

    async def _snapshot_aggregate(
        self, aggregate: Aggregate, headers: Dict[str, str] | None = None
    ) -> None:
        memento = aggregate.get_memento()
        snapshot = Snapshot(
            tenant_id=self._tenant_id,
            stream_id=aggregate.id,
            commit_sequence=aggregate.commit_sequence,
            payload=memento.model_dump_json(serialize_as_any=True),
            stream_revision=memento.version,
            headers=headers or {},
        )
        await self._snapshot_store.add(snapshot=snapshot, headers=headers)
