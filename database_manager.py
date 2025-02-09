import pandas as pd
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.dialects.postgresql import insert
from secret_codes import secret_codes
sql_host = secret_codes["PostgreSQL host"]
sql_port = secret_codes["PostgreSQL port"]
sql_username = secret_codes["PostgreSQL username"]
sql_password = secret_codes["PostgreSQL password"]
sql_database = secret_codes["PostgreSQL database"]


class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(f'postgresql+psycopg2://{sql_username}:{sql_password}@{sql_host}:{sql_port}/{sql_database}', isolation_level="AUTOCOMMIT")
        self.connection = self.engine.connect()
        self.metadata = MetaData()
        create_market_data = """
        CREATE TABLE IF NOT EXISTS market_data (
            symbol TEXT NOT NULL,
            exchange TEXT NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            PRIMARY KEY (symbol, exchange)
        );
        """
        self.execute(create_market_data)
        create_historical_market_data = """
        CREATE TABLE IF NOT EXISTS historical_market_data (
            symbol TEXT NOT NULL,
            exchange TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            open FLOAT NOT NULL CHECK (open > 0),
            close FLOAT NOT NULL CHECK (close > 0),
            high FLOAT NOT NULL CHECK (high > 0),
            low FLOAT NOT NULL CHECK (low > 0),
            volume BIGINT NOT NULL CHECK (volume >= 0),
            PRIMARY KEY (symbol, exchange, timestamp),
            FOREIGN KEY (symbol, exchange) REFERENCES market_data(symbol, exchange) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """
        self.execute(create_historical_market_data)

    @staticmethod
    def upsert(table, conn, keys, data_iter):
        data = [dict(zip(keys, row)) for row in data_iter]
        insert_statement = insert(table.table).values(data)
        upsert_statement = insert_statement.on_conflict_do_update(
            constraint=f"{table.table.name}_pkey",
            set_={c.key: c for c in insert_statement.excluded},
        )
        conn.execute(upsert_statement)

    def execute(self, sql_query):
        res = self.connection.execute(text(sql_query))
        return res

    def save_market_data(self, data):
        data.to_sql(
            "market_data",
            con=self.connection,
            if_exists='append',
            index=True,
            method=self.upsert
        )

    def load_market_data(self):
        data = pd.read_sql("SELECT * FROM market_data", self.connection)
        data.set_index(['symbol', 'exchange'], inplace=True)
        return data

    def save_historical_market_data(self, data):
        data.to_sql(
            "historical_market_data",
            con=self.connection,
            if_exists='append',
            index=True,
            method=self.upsert
        )

    def save_government_data(self, data):
        pass

    def save_country_data(self, data):
        pass

    def save_balance_sheet_data(self, data):
        pass

    def save_cash_flow_data(self, data):
        pass

    def save_income_statement_data(self, data):
        pass


if __name__ == '__main__':
    db = DatabaseManager()
    result = db.execute(
        '''
        ALTER TABLE historical_market_data
        ADD CONSTRAINT fk_market_data
        FOREIGN KEY (symbol, exchange)
        REFERENCES market_data(symbol, exchange)
        ON DELETE CASCADE
        ON UPDATE CASCADE;
        '''
    )
    print('')
