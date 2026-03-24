from sqlalchemy import create_engine, text
import pandas as pd

class SqlBackend:
    def __init__(self):
        self.engine = None
        self.connection = None
        
    def connect(self, conn_profile: dict) -> tuple[bool, str]:
        """Attempt to connect and return (success, message)."""
        try:
            auth_type = conn_profile.get('auth_type', 'uri')
            if auth_type == 'uri':
                conn_str = conn_profile.get('uri', '')
            else:
                user = conn_profile.get('username', '')
                pwd = conn_profile.get('password', '')
                host = conn_profile.get('host', 'localhost')
                port = conn_profile.get('port', '5432')
                db = conn_profile.get('database', '')
                conn_str = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"

            self.engine = create_engine(conn_str)
            self.connection = self.engine.connect()
            return True, "Connected successfully"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
            
    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
        if self.engine:
            self.engine.dispose()
            self.engine = None
            
    def execute_query(self, query: str):
        """Execute a query and return results (columns, data)."""
        if not self.connection:
            return False, "Not connected to a database", [], []
            
        try:
            # First handle queries that might not return rows
            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER")):
                res = self.connection.execute(text(query))
                self.connection.commit()
                return True, f"Operation successful. {res.rowcount} rows affected.", [], []
                
            # For SELECTs, use pandas
            df = pd.read_sql_query(text(query), self.connection)
            columns = df.columns.tolist()
            # Convert NaN to None or empty string
            df = df.fillna("")
            data = df.values.tolist()
            return True, f"Query executed successfully ({len(data)} rows)", columns, data
        except Exception as e:
            return False, f"Query error: {str(e)}", [], []
