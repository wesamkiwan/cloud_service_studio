import pymongo
from pymongo.errors import PyMongoError

class MongoBackend:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        
    def connect(self, conn_profile: dict) -> tuple[bool, str]:
        try:
            auth_type = conn_profile.get('auth_type', 'uri')
            if auth_type == 'uri':
                conn_str = conn_profile.get('uri', '')
                self.client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=2000)
            else:
                user = conn_profile.get('username', '')
                pwd = conn_profile.get('password', '')
                host = conn_profile.get('host', 'localhost')
                port = conn_profile.get('port', 27017)
                db = conn_profile.get('database', '')
                
                self.client = pymongo.MongoClient(
                    host=host,
                    port=int(port) if port else 27017,
                    username=user if user else None,
                    password=pwd if pwd else None,
                    authSource=db if db else 'admin',
                    serverSelectionTimeoutMS=2000
                )
            # Test connection
            self.client.admin.command('ping')
            return True, "Connected successfully"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
            
    def disconnect(self):
        if self.client:
            self.client.close()
            self.client = None
            
    def get_databases(self):
        if not self.client: return []
        try:
            return self.client.list_database_names()
        except:
            return []
            
    def get_collections(self, db_name: str):
        if not self.client: return []
        try:
            return self.client[db_name].list_collection_names()
        except:
            return []
            
    def set_db_col(self, db_name: str, col_name: str):
        if self.client:
            self.db = self.client[db_name]
            self.collection = self.db[col_name]
            
    def query_documents(self, filter_dict=None, limit=50):
        if not self.collection:
            return False, "No collection selected", []
            
        if filter_dict is None:
            filter_dict = {}
            
        try:
            docs = list(self.collection.find(filter_dict).limit(limit))
            # Convert ObjectId to string for easy display
            for doc in docs:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            return True, f"Found {len(docs)} documents", docs
        except Exception as e:
            return False, f"Query error: {str(e)}", []
