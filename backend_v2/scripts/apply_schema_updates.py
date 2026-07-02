import os
import sys

from sqlalchemy import inspect, text
from sqlalchemy.schema import CreateColumn, CreateIndex

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import Base, check_db_connection, engine
import app.models  # noqa: F401


def quote_name(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def main():
    if not check_db_connection():
        print("ERROR: Cannot connect to the database.")
        sys.exit(1)

    print("Creating any missing tables...")
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    with engine.begin() as conn:
        for table_name, table in sorted(Base.metadata.tables.items()):
            existing_columns = {
                column["name"]
                for column in inspector.get_columns(table_name)
            }
            for column in table.columns:
                if column.name in existing_columns:
                    continue
                ddl = CreateColumn(column).compile(dialect=engine.dialect)
                conn.execute(text(f"ALTER TABLE {quote_name(table_name)} ADD COLUMN {ddl}"))
                print(f"Added column {table_name}.{column.name}")

        print("Creating any missing indexes...")
        for table in sorted(Base.metadata.tables.values(), key=lambda t: t.name):
            existing_indexes = {idx["name"] for idx in inspector.get_indexes(table.name)}
            for index in sorted(table.indexes, key=lambda idx: idx.name or ""):
                if index.name in existing_indexes:
                    continue
                conn.execute(text(str(CreateIndex(index).compile(dialect=engine.dialect))))
                print(f"Added index {index.name}")

    print("Schema update complete.")


if __name__ == "__main__":
    main()
