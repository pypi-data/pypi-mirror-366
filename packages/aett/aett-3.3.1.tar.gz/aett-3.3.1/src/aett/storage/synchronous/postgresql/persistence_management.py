from typing import Iterable

import psycopg

from aett.eventstore import IManagePersistence, TopicMap, COMMITS, SNAPSHOTS, Commit
from aett.storage.synchronous.postgresql import _item_to_commit


class PersistenceManagement(IManagePersistence):
    def __init__(
        self,
        connection_string: str,
        topic_map: TopicMap,
        commits_table_name: str = COMMITS,
        snapshots_table_name: str = SNAPSHOTS,
    ):
        self._connection_string: str = connection_string
        self._topic_map = topic_map
        self._commits_table_name = commits_table_name
        self._snapshots_table_name = snapshots_table_name

    def initialize(self):
        try:
            with psycopg.connect(
                self._connection_string, autocommit=True
            ) as connection:
                with connection.cursor() as c:
                    c.execute(f"""CREATE TABLE {self._commits_table_name}
        (
            TenantId varchar(64) NOT NULL,
            StreamId char(64) NOT NULL,
            StreamIdOriginal varchar(1000) NOT NULL,
            StreamRevision int NOT NULL CHECK (StreamRevision > 0),
            Items smallint NOT NULL CHECK (Items > 0),
            CommitId uuid NOT NULL,
            CommitSequence int NOT NULL CHECK (CommitSequence > 0),
            CommitStamp timestamp NOT NULL,
            CheckpointNumber BIGSERIAL NOT NULL,
            Headers bytea NULL,
            Payload bytea NOT NULL,
            CONSTRAINT PK_Commits PRIMARY KEY (CheckpointNumber)
        );
        CREATE UNIQUE INDEX IX_Commits_CommitSequence ON {self._commits_table_name} (TenantId, StreamId, CommitSequence);
        CREATE UNIQUE INDEX IX_Commits_CommitId ON {self._commits_table_name} (TenantId, StreamId, CommitId);
        CREATE UNIQUE INDEX IX_Commits_Revisions ON {self._commits_table_name} (TenantId, StreamId, StreamRevision, Items);
        CREATE INDEX IX_Commits_Stamp ON {self._commits_table_name} (CommitStamp);
        
        CREATE TABLE {self._snapshots_table_name}
        (
            TenantId varchar(40) NOT NULL,
            StreamId char(40) NOT NULL,
            StreamRevision int NOT NULL CHECK (StreamRevision > 0),
            CommitSequence int NOT NULL CHECK (CommitSequence > 0),
            Payload bytea NOT NULL,
            Headers bytea NOT NULL,
            CONSTRAINT PK_Snapshots PRIMARY KEY (TenantId, StreamId, StreamRevision)
        );""")
                    c.commit()
        except Exception:
            pass

    def drop(self):
        with psycopg.connect(self._connection_string, autocommit=True) as connection:
            with connection.cursor() as c:
                c.execute(
                    f"""DROP TABLE {self._snapshots_table_name};DROP TABLE {self._commits_table_name};"""
                )

    def purge(self, tenant_id: str):
        with psycopg.connect(self._connection_string, autocommit=True) as connection:
            with connection.cursor() as c:
                c.execute(
                    f"""DELETE FROM {self._commits_table_name} WHERE TenantId = %s;""",
                    tenant_id,
                )
                c.execute(
                    f"""DELETE FROM {self._snapshots_table_name} WHERE TenantId = %s;""",
                    tenant_id,
                )

    def get_from(self, checkpoint: int) -> Iterable[Commit]:
        with psycopg.connect(self._connection_string, autocommit=True) as connection:
            with connection.cursor() as cur:
                cur.execute(
                    f"""SELECT TenantId, StreamId, StreamIdOriginal, StreamRevision, CommitId, CommitSequence, CommitStamp,  CheckpointNumber, Headers, Payload
                                  FROM {self._commits_table_name}
                                 WHERE CommitStamp >= %s
                                 ORDER BY CheckpointNumber;""",
                    (checkpoint,),
                )
                fetchall = cur.fetchall()
                for doc in fetchall:
                    yield _item_to_commit(doc, self._topic_map)
