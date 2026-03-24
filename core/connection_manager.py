import json
import os
import uuid

class ConnectionManager:
    def __init__(self, filepath="connections.json"):
        # We store connections at the root of the project
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.filepath = os.path.join(project_root, filepath)
        self.connections = self.load_connections()

    def load_connections(self):
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading connections: {e}")
            return []

    def save_connections(self):
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.connections, f, indent=4)
        except Exception as e:
            print(f"Error saving connections: {e}")

    def get_all(self):
        return self.connections
        
    def get_by_service(self, service_type):
        """Returns connection profiles for a specific service (e.g. 'sql', 'mongodb')."""
        return [c for c in self.connections if c.get('service_type') == service_type]

    def get_connection(self, conn_id):
        for c in self.connections:
            if c.get('id') == conn_id:
                return c
        return None

    def add_connection(self, data):
        data['id'] = str(uuid.uuid4())
        self.connections.append(data)
        self.save_connections()
        return data['id']

    def update_connection(self, conn_id, new_data):
        for i, conn in enumerate(self.connections):
            if conn.get('id') == conn_id:
                new_data['id'] = conn_id
                self.connections[i] = new_data
                self.save_connections()
                return True
        return False

    def delete_connection(self, conn_id):
        new_list = [c for c in self.connections if c.get('id') != conn_id]
        if len(new_list) != len(self.connections):
            self.connections = new_list
            self.save_connections()
            return True
        return False
