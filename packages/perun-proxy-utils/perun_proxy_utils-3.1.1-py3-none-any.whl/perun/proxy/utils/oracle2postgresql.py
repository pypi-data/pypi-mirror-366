import argparse
import yaml
from sys import stderr, exit
from sqlalchemy import (
    create_engine,
    Table,
    Column,
    MetaData,
    UniqueConstraint,
    Integer,
    BigInteger,
    String,
    Text,
    Date,
    text,
)
from sqlalchemy.exc import SQLAlchemyError


class Oracle2PostgreSQL:
    """
    Import append-only attributes from Oracle DB to Postgresql.
    For all IDs returned from the Oracle SQL, insert a predefined value into an attribute.
    Currently, for all alumni insert alum into eduPersonAffiliation.
    """

    def __init__(self, full_sync):
        self.table_for_imported_attributes = "attributefromsqlunique"
        self.imported_table_name = "w_exp_passwd_all"
        self.__get_config()
        self.full_sync = full_sync
        self.oracle_engine = self.__get_oracle_engine()
        self.postgresql_engine = self.__get_postgresql_engine()
        self.__create_tables_if_they_dont_exist()

    def run_sync(self):
        self.__import_attributes(self.import_attributes)
        self.__import_tables(self.import_tables, self.full_sync)

    def __get_config(self):
        filepath = "/etc/oracle2postgresql_cfg.yaml"
        try:
            with open(filepath, "r") as file:
                conf = yaml.safe_load(file)
                self.batch_size = conf["batch_size"]
                self.oracle_con_string = conf["oracle_con_string"]
                self.postgresql_con_string = conf["postgres_con_string"]
                self.import_attributes = conf["import_attributes"]
                self.import_tables = conf["import_table"]
        except OSError as e:
            print(
                f"Cannot open config with path: {filepath}, error: {e.strerror}",
                file=stderr,
            )
            exit(2)

    def __get_oracle_engine(self):
        return create_engine(self.oracle_con_string)

    def __get_postgresql_engine(self):
        return create_engine(self.postgresql_con_string)

    def __create_tables_if_they_dont_exist(self):
        metadata = MetaData()

        Table(
            self.table_for_imported_attributes,
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("uid", String(100), nullable=False),
            Column("sp", String(250), server_default="%"),
            Column("attribute", String(30), nullable=False),
            Column("value", Text),
            Column("expires", Date, server_default="9999-12-31"),
            UniqueConstraint("uid", "attribute", "sp", "expires"),
        )

        Table(
            "w_exp_passwd_all",
            metadata,
            Column("people_id", BigInteger, primary_key=True),
            Column("login", String(31), nullable=True),
            Column("heslo_primarni", String(255), nullable=True),
            Column("heslo_sekundarni", String(255), nullable=True),
            Column("zmeneno_primarni", Date, nullable=True),
            Column("zmeneno_sekundarni", Date, nullable=True),
        )

        try:
            metadata.create_all(self.postgresql_engine)
        except SQLAlchemyError as e:
            print(f"Error creating tables: {e}")

    def __run_oracle_statement(self, select, params={}):
        with self.oracle_engine.connect() as conn:
            stmt = text(select)
            return conn.execute(stmt, params)

    def __import_attributes(self, imports):
        """
        Import attributes.
        imports -- array in the form:
            'select': {
                'attribute_name': 'value'
            }
        """
        for select, attribute in imports.items():
            stmt = self.__run_oracle_statement(select)
            batch = []
            for row in stmt:
                batch.append(row[0])
                if len(batch) >= self.batch_size:
                    self.__insert(batch, attribute)
                    batch = []
            if len(batch) > 0:
                self.__insert(batch, attribute)

    def __import_tables(self, source_table_info, full_sync):
        """
        Import table.
        source_table_info -- array in the form:
            'source_table': 'source_table_name',
            'columns': ['first', 'second'],
            'changed': ['timestamp_column']

        """
        columns = source_table_info["columns"] + source_table_info["changed"]
        column_list_expr = source_table_info["columns"]
        for change_column in source_table_info["changed"]:
            column_list_expr.append(
                f"TO_CHAR({change_column}, 'YYYY-MM-DD HH24:MI:SS') AS {change_column}"
            )
        column_list_expr = ",".join(column_list_expr)
        params = {}
        if full_sync:
            select = f"SELECT {column_list_expr} FROM {source_table_info.get('source_table', self.imported_table_name)}"
        else:
            selects = []
            with self.oracle_engine.connect() as conn:
                for change_column in source_table_info["changed"]:
                    select = f"SELECT {column_list_expr} FROM {source_table_info.get('source_table', self.imported_table_name)}"
                    last_value = conn.execute(
                        text(
                            f"SELECT MAX({change_column}) FROM {self.imported_table_name}"
                        )
                    ).scalar()
                    select += f" WHERE {change_column} >= TO_TIMESTAMP(:{change_column}, 'YYYY-MM-DD HH24:MI:SS')"
                    selects.append(select)
                    params[change_column] = last_value
            select = " UNION ".join(selects)
        with self.oracle_engine.connect() as conn:
            insert_data = conn.execute(text(select), params)

        updates = [f"{column} = EXCLUDED.{column}" for column in columns]
        placeholders = [f":{column}" for column in columns]
        query = text(
            f"INSERT INTO {self.imported_table_name} ({','.join(columns)}) VALUES ({','.join(placeholders)}) ON CONFLICT (people_id) DO UPDATE SET {','.join(updates)}"
        )
        row_count = 0
        with self.postgresql_engine.begin() as conn:
            for row in insert_data:
                row_count += 1
                params = {columns[i]: row[i] for i in range(len(columns))}
                conn.execute(query, params)
        print(f"Oracle2PostgreSQL.py - {row_count} account(s) were updated.")

    def __insert(self, usernames, attribute):
        if not usernames:
            return

        insert_text = text(
            f'INSERT INTO "{self.table_for_imported_attributes}" (uid, attribute, value) '
            "VALUES (:uid, :attribute, :value) "
            "ON CONFLICT (uid,attribute,sp,expires) DO NOTHING"
        )
        with self.postgresql_engine.begin() as conn:
            for username in usernames:
                for name, value in attribute.items():
                    try:
                        with conn.begin_nested():
                            conn.execute(
                                insert_text,
                                {"uid": username, "attribute": name, "value": value},
                            )
                    except Exception as e:
                        print(
                            f"Oracle2PostgreSQL - Failed to insert/update, "
                            f"user {username}, attribute {name}, value {value}"
                            f"{e}"
                        )


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--full_sync",
        action="store_true",
        default=False,
        help="Whether to do a full sync or not.",
    )
    return parser.parse_args()


def main():
    args = get_args()

    ora2postgresql = Oracle2PostgreSQL(args.full_sync)
    ora2postgresql.run_sync()


if __name__ == "__main__":
    main()
