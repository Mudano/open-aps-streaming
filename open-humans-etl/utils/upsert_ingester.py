
from utils.database import Database
from utils.utils import Utils


class UpsertIngester(Utils):

    def __init__(self, db_connection):

        self.db = Database(helpers_connection=db_connection)

    def add_target(self, target_data, table_name, output_schema, primary_keys, date_format):

        self.target_data = target_data

        self.table_name = table_name
        self.schema = output_schema
        self.primary_keys = primary_keys

        date_cols = [x['column_name'] for x in self.db.execute_query(f""" SELECT column_name FROM information_schema.columns WHERE table_schema = '{output_schema}' AND table_name = '{table_name}' AND ( data_type ILIKE '%timestamp%' OR data_type ILIKE '%date%' ); """, return_object=True)]

        if not self.target_data:

            raise IndexError('Target data for table ' + self.table_name + ' is empty.')

        else:
            self.target_data, self.target_columns = Utils.add_missing_keys(Utils.keys_to_snakecase(self, self.target_data))

            self.column_names = ', '.join([x for x in self.target_columns])
            self.columns_insert = ', '.join(['%(' + x + ')s' if x not in [k for k in date_cols]
                                             else f"TO_TIMESTAMP(%(" + x + ")s, '" + date_format + "')"
                                             for x in self.target_columns])

            self._ingest_target()

    def _ingest_target(self):

        self.db.execute_query(f""" INSERT INTO       {self.schema}.{self.table_name}
                                                     ({self.column_names})
                                   VALUES            ({self.columns_insert})
                                   ON CONFLICT       (""" + ', '.join([x for x in self.primary_keys]) + """)
                                   DO NOTHING
                                   ;
                                   """, multiple=True, args=self.target_data)

    def close(self):

        self.db.close()
