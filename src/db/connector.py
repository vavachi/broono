import pyodbc

class DbConnector:
    def __init__(self):
        self.connection = None

    def connect(self, server, database, username=None, password=None, trusted=False, trust_cert=False):
        """
        Establishes a connection to the MSSQL database.
        """
        drivers = [d for d in pyodbc.drivers() if 'SQL Server' in d]
        if not drivers:
            raise Exception("No ODBC Drivers for SQL Server found.")
        
        # Prefer Driver 17 over Driver 18: Driver 18 enables encryption by default
        # which causes ODBC 08001 errors on older/local SQL Server instances.
        preferred = [d for d in drivers if 'ODBC Driver 17' in d]
        driver = preferred[0] if preferred else sorted(drivers, reverse=True)[0]
        
        conn_str = f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};'
        
        if trusted:
            conn_str += 'Trusted_Connection=yes;'
        else:
            conn_str += f'UID={username};PWD={password};'

        if trust_cert:
            conn_str += 'TrustServerCertificate=yes;'
        
        # Driver 18 forces encryption on by default; explicitly disable it
        # so localhost connections work without a valid SSL certificate chain.
        if 'ODBC Driver 18' in driver:
            conn_str += 'Encrypt=no;'

        try:
            self.connection = pyodbc.connect(conn_str)
            return True
        except pyodbc.Error as e:
            raise Exception(f"Connection failed: {str(e)}")

    def execute_query(self, query, params=None):
        """
        Executes a query and returns the cursor.
        """
        if not self.connection:
            raise Exception("Not connected to a database.")
        
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor

    def fetch_all(self, query, params=None):
        cursor = self.execute_query(query, params)
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return results

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
