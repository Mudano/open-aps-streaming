
from utils.database import Database
from utils.utils import Utils


class StreamIngester(Utils):

    def __init__(self, db_connection):

        self.db = Database(helpers_connection=db_connection)

    def add_target(self, target_data, table_name, output_schema, date_format):

        self.target_data = target_data

        self.table_name = table_name
        self.schema = output_schema

        date_cols = [x['column_name'] for x in self.db.execute_query(f""" SELECT column_name FROM information_schema.columns WHERE table_schema = '{output_schema}' AND table_name = '{table_name}' AND ( data_type ILIKE '%timestamp%' OR data_type ILIKE '%date%' ); """, return_object=True)]

        self.target_data, self.target_columns = Utils.add_missing_keys(self.target_data)

        self.column_names = ', '.join(['"' + x + '"' for x in self.target_columns])
        self.columns_insert = ', '.join(['%(' + x + ')s' if x not in [k for k in date_cols]
                                         else f"TO_TIMESTAMP(%(" + x + ")s, '" + date_format + "')"
                                         for x in self.target_columns])

        self._ingest_target()

    def _ingest_target(self):

        self.db.execute_query(f""" INSERT INTO       {self.schema}.{self.table_name}
                                                     ({self.column_names})
                                   VALUES            ({self.columns_insert})
        """, multiple=True,
             args=self.target_data)
