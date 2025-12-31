from .connector import DbConnector

class SchemaExtractor:
    def __init__(self, connector: DbConnector):
        self.connector = connector

    def get_tables(self):
        """
        Retrieves a list of tables from the database.
        """
        query = """
        SELECT 
            t.name AS TABLE_NAME,
            s.name AS TABLE_SCHEMA,
            t.modify_date
        FROM sys.tables t
        JOIN sys.schemas s ON t.schema_id = s.schema_id
        ORDER BY s.name, t.name
        """
        return self.connector.fetch_all(query)

    def get_columns(self, schema, table):
        """
        Retrieves column details for a specific table.
        """
        query = """
        SELECT 
            COLUMN_NAME, 
            DATA_TYPE, 
            IS_NULLABLE, 
            CHARACTER_MAXIMUM_LENGTH,
            NUMERIC_PRECISION,
            NUMERIC_SCALE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
        """
        return self.connector.fetch_all(query, (schema, table))

    def get_stored_objects(self, object_type):
        """
        Retrieves stored objects (Procedures, Functions, Triggers) and their definitions.
        object_type: 'P' (Procedure), 'FN' (Scalar Function), 'IF' (Inline Table-valued Function), 
                     'TF' (Table-valued Function), 'TR' (Trigger)
        """
        query = """
        SELECT 
            s.name AS [schema],
            o.name,
            m.definition,
            o.type_desc,
            o.modify_date
        FROM sys.objects o
        JOIN sys.schemas s ON o.schema_id = s.schema_id
        JOIN sys.sql_modules m ON o.object_id = m.object_id
        WHERE o.type = ?
        ORDER BY s.name, o.name
        """
        return self.connector.fetch_all(query, (object_type,))

    def get_full_schema(self):
        """
        Builds a comprehensive dictionary of the entire schema.
        Structure:
        {
            'tables': { 'schema.name': { 'columns': {...}, 'modify_date': datetime } },
            'procedures': { 'schema.name': { 'definition': '...', 'type': '...', 'modify_date': datetime } },
            'functions': { 'schema.name': { 'definition': '...', 'type': '...', 'modify_date': datetime } },
            'triggers': { 'schema.name': { 'definition': '...', 'type': '...', 'modify_date': datetime } }
        }
        """
        full_schema = {
            'tables': {},
            'procedures': {},
            'functions': {},
            'triggers': {}
        }

        # 1. Tables
        tables = self.get_tables()
        for t in tables:
            schema_name = t['TABLE_SCHEMA']
            table_name = t['TABLE_NAME']
            full_name = f"{schema_name}.{table_name}"
            
            columns = self.get_columns(schema_name, table_name)
            col_dict = {}
            for col in columns:
                col_name = col['COLUMN_NAME']
                col_dict[col_name] = {
                    'type': col['DATA_TYPE'],
                    'nullable': col['IS_NULLABLE'] == 'YES',
                    'length': col['CHARACTER_MAXIMUM_LENGTH'],
                    'precision': col['NUMERIC_PRECISION'],
                    'scale': col['NUMERIC_SCALE']
                }
            
            full_schema['tables'][full_name] = {
                'columns': col_dict,
                'modify_date': t['modify_date']
            }

        # 2. Procedures
        procs = self.get_stored_objects('P')
        for p in procs:
            full_name = f"{p['schema']}.{p['name']}"
            full_schema['procedures'][full_name] = {
                'definition': p['definition'],
                'type': p['type_desc'],
                'modify_date': p['modify_date']
            }

        # 3. Functions (FN, IF, TF)
        for ftype in ['FN', 'IF', 'TF']:
            funcs = self.get_stored_objects(ftype)
            for f in funcs:
                full_name = f"{f['schema']}.{f['name']}"
                full_schema['functions'][full_name] = {
                    'definition': f['definition'],
                    'type': f['type_desc'],
                    'modify_date': f['modify_date']
                }

        # 4. Triggers
        triggers = self.get_stored_objects('TR')
        for tr in triggers:
            full_name = f"{tr['schema']}.{tr['name']}"
            full_schema['triggers'][full_name] = {
                'definition': tr['definition'],
                'type': tr['type_desc'],
                'modify_date': tr['modify_date']
            }
            
        return full_schema
