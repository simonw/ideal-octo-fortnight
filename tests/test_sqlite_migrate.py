from sqlite_migrate import Migrations
import sqlite_utils
import pytest


@pytest.fixture
def migrations():
    migrations = Migrations("test")

    @migrations()
    def m001(db):
        db["dogs"].insert({"name": "Cleo"})

    @migrations()
    def m002(db):
        db["cats"].create({"name": str})

    return migrations


@pytest.fixture
def migrations2():
    migrations = Migrations("test2")

    @migrations()
    def m001(db):
        db["dogs2"].insert({"name": "Cleo"})

    return migrations


def test_basic(migrations):
    db = sqlite_utils.Database(memory=True)
    assert db.table_names() == []
    migrations.apply(db)
    assert set(db.table_names()) == {"_sqlite_migrations", "dogs", "cats"}


def test_stop_before(migrations):
    db = sqlite_utils.Database(memory=True)
    assert db.table_names() == []
    migrations.apply(db, stop_before="m002")
    assert set(db.table_names()) == {"_sqlite_migrations", "dogs"}
    # Apply the rest
    migrations.apply(db)
    assert set(db.table_names()) == {"_sqlite_migrations", "dogs", "cats"}


def test_two_migration_sets(migrations, migrations2):
    db = sqlite_utils.Database(memory=True)
    assert db.table_names() == []
    migrations.apply(db)
    migrations2.apply(db)
    assert set(db.table_names()) == {"_sqlite_migrations", "dogs", "cats", "dogs2"}
