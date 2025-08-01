"""SQLite database construction components."""

import dataclasses
import sqlite3


class SQLiteDBConnection(sqlite3.Connection):
    """Enhanced SQLite DB connection."""

    def __init__(self, *args, **kwargs) -> None:
        """Object initialization routine."""
        super().__init__(*args, **kwargs)
        self.db_location: str | None = str(args[0]) if args else None


@dataclasses.dataclass(slots=True)
class SQLiteDBColumnDefinition:
    """SQLite DB column definition."""

    name: str
    type: str
    constraint: str = ""

    def __str__(self):
        elements = [str(e).strip() for e in (self.name, self.type, self.constraint) if e]
        return " ".join(elements)


@dataclasses.dataclass(slots=True)
class SQLiteDBTableDefinition:
    """SQLite DB table definition."""

    name: str
    columns: list[SQLiteDBColumnDefinition] = dataclasses.field(default_factory=list)
    constraint: str = ""
    options: str = ""
    sql_create_table: str = dataclasses.field(init=False, repr=False)

    def __post_init__(self):
        """Post-initialization steps."""
        column_defs = [str(column) for column in self.columns]

        sql_create_table = "CREATE TABLE {name}({column_defs}{constraint}){options};".format(
            name=self.name,
            column_defs=",".join(column_defs),
            constraint=f", {self.constraint}" if self.constraint else "",
            options=f" {self.options}" if self.options else "",
        )

        # Do basic SQL syntax sanity check
        if sqlite3.complete_statement(sql_create_table):
            self.sql_create_table = sql_create_table
        else:
            raise sqlite3.ProgrammingError(
                f"Generate DB table creation SQL: Table '{self.name}': Broken SQL: {sql_create_table}"
            )


@dataclasses.dataclass(slots=True)
class SQLiteDBTriggerProgStmtDefinition:
    """Definition of statement of SQLite DB trigger program."""

    body: str

    def __str__(self):
        return self.body


@dataclasses.dataclass(slots=True)
class SQLiteDBTriggerDefinition:
    """SQLite DB trigger definition.

    Ref: https://www.sqlite.org/lang_createtrigger.html
    """

    name: str  # DB trigger name
    timing: str  # BEFORE | AFTER
    action: str  # DELETE | INSERT | UPDATE
    table_name: str  # name of a target DB table
    column_names: list[str] = dataclasses.field(default_factory=list)
    prog_stmts: list[SQLiteDBTriggerProgStmtDefinition] = dataclasses.field(default_factory=list)
    sql_create_trigger: str = dataclasses.field(init=False, repr=False)

    def __post_init__(self):
        """Post-initialization steps.

        Example of trigger creation SQL:

            CREATE TRIGGER before_update_my_table
            BEFORE UPDATE OF column_name1,column_name2,column_name3 ON my_table
            BEGIN SELECT RAISE(FAIL,"Update prohibited");END
        """

        prog_stmts_clause = "".join([f"{str(stmt)};" for stmt in self.prog_stmts])

        sql_template = (
            "CREATE TRIGGER {name} {timing} {action}{col_names_clause} ON {table_name} BEGIN {prog_stmts_clause} END;"
        )
        sql_create_trigger = sql_template.format(
            name=self.name,
            timing=self.timing,
            action=self.action,
            col_names_clause=f" OF {','.join(self.column_names)}" if self.column_names else "",
            table_name=self.table_name,
            prog_stmts_clause=prog_stmts_clause,
        )

        # Do basic SQL syntax sanity check
        if sqlite3.complete_statement(sql_create_trigger):
            self.sql_create_trigger = sql_create_trigger
        else:
            raise sqlite3.ProgrammingError(
                f"Generate DB trigger creation SQL: Trigger '{self.name}': Broken SQL: {sql_create_trigger}"
            )


@dataclasses.dataclass(slots=True)
class SQLiteDBDefinition:
    """SQLite DB definition."""

    tables: list[SQLiteDBTableDefinition] = dataclasses.field(default_factory=list)
    triggers: list[SQLiteDBTriggerDefinition] = dataclasses.field(default_factory=list)

    def db_init(self, db_cursor: sqlite3.Cursor) -> None:
        """Create database structure.

        :param db_cursor:   cursor of an active DB connection
        """
        db_location = getattr(db_cursor.connection, "db_location", "Undefined location")

        # Create tables
        for table in self.tables:
            try:
                db_cursor.execute(table.sql_create_table)
            except sqlite3.Error as e:
                raise type(e)(f"Initialize database: {db_location}: Create table '{table.name}': {e}") from e

        # Create triggers
        for trigger in self.triggers:
            try:
                db_cursor.execute(trigger.sql_create_trigger)
            except sqlite3.Error as e:
                raise type(e)(f"Initialize database: {db_location}: Create trigger '{trigger.name}': {e}") from e

        try:
            db_cursor.connection.commit()
        except sqlite3.Error as e:
            raise type(e)(f"Initialize database: {db_location}: Save DB schema: {e}")

    def db_verify(self, db_cursor: sqlite3.Cursor) -> None:
        """Verify DB structure and consistency.

        :param db_cursor:   cursor of an active DB connection
        """
        db_location = getattr(db_cursor.connection, "db_location", "Undefined location")

        # TODO: Add check for TEXT encoding (PRAGMA encoding;)
        # Ref: https://www.sqlite.org/pragma.html#pragma_encoding
        # TODO: Add check for general DB integrity (PRAGMA integrity_check;)
        # Ref: https://www.sqlite.org/pragma.html#pragma_integrity_check

        # TODO: Refactor 'sql_create_*' checks for all DB entities to reduce code duplication.
        for table in self.tables:
            try:
                db_cursor.execute("SELECT * FROM sqlite_schema WHERE type=? AND name=?", ("table", table.name))
                if db_table_schema := db_cursor.fetchone():
                    db_table_schema_sql = db_table_schema["sql"] + ";"
                    if db_table_schema_sql != table.sql_create_table:
                        raise sqlite3.DatabaseError(
                            f"Unexpected table schema: reference '{table.sql_create_table}'"
                            f" != detected '{db_table_schema_sql}'"
                        )
                else:
                    raise sqlite3.DatabaseError("Table does not exist")
            except sqlite3.Error as e:
                raise type(e)(f"Verify database: {db_location}: Check table '{table.name}': {e}") from e

        for trigger in self.triggers:
            try:
                db_cursor.execute("SELECT * FROM sqlite_schema WHERE type=? AND name=?", ("trigger", trigger.name))
                if db_trigger_schema := db_cursor.fetchone():
                    db_trigger_schema_sql = db_trigger_schema["sql"] + ";"
                    if db_trigger_schema_sql != trigger.sql_create_trigger:
                        raise sqlite3.DatabaseError(
                            f"Unexpected trigger schema: reference '{trigger.sql_create_trigger}'"
                            f" != detected '{db_trigger_schema_sql}'"
                        )
                else:
                    raise sqlite3.DatabaseError("Trigger does not exist")
            except sqlite3.Error as e:
                raise type(e)(f"Verify database: {db_location}: Check trigger '{trigger.name}': {e}") from e

        # TODO: Add check for presence of unnecessary (not defined by the schema) DB objects
        #       (e.g. tables)

    @staticmethod
    def db_is_void(db_cursor: sqlite3.Cursor) -> bool:
        """Check, if DB does not have any structure (table 'sqlite_schema' is empty).

        :param db_cursor:   cursor of an active DB connection
        :return:            True if DB is void, False otherwise
        """
        db_location = getattr(db_cursor.connection, "db_location", "Undefined location")

        try:
            db_cursor.execute("SELECT COUNT(*) AS object_count FROM sqlite_schema")
            if db_cursor.fetchone()["object_count"] == 0:
                return True
            else:
                return False
        except sqlite3.Error as e:
            raise type(e)(f"Check if database is void: {db_location}: {e}") from e
