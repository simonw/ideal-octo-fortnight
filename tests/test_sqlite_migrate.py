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
        db.query("insert into dogs (name) values ('Pancakes')")

    return migrations


@pytest.fixture
def migrations_not_ordered_alphabetically():
    # Names order alphabetically in the wrong direction but this
    # should still be applied correctly
    migrations = Migrations("test")

    @migrations()
    def m002(db):
        db["dogs"].insert({"name": "Cleo"})

    @migrations()
    def m001(db):
        db["cats"].create({"name": str})
        db.query("insert into dogs (name) values ('Pancakes')")

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


def test_order_does_not_matter(migrations, migrations_not_ordered_alphabetically):
    db1 = sqlite_utils.Database(memory=True)
    db2 = db = sqlite_utils.Database(memory=True)
    migrations.apply(db1)
    migrations_not_ordered_alphabetically.apply(db2)
    assert db1.schema == db2.schema


def test_upgrades_sqlite_migrations_from_one_to_two_primary_keys(migrations):
    db = sqlite_utils.Database(memory=True)
    db["_sqlite_migrations"].create(
        {
            "migration_set": str,
            "name": str,
            "applied_at": str,
        },
        pk="name",
    )
    # Applying migrations should fix that
    assert db.table_names() == ["_sqlite_migrations"]
    assert db["_sqlite_migrations"].pks == ["name"]
    migrations.apply(db)
    assert db["_sqlite_migrations"].pks == ["migration_set", "name"]
