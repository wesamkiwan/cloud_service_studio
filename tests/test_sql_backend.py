import pytest
import os
from tools.sql_ide.backend import SqlBackend

@pytest.fixture
def clean_backend():
    backend = SqlBackend()
    yield backend
    backend.disconnect()

def test_sql_connect_memory(clean_backend):
    # Connect to in-memory SQLite database
    profile = {
        'auth_type': 'uri',
        'uri': 'sqlite:///:memory:'
    }
    success, msg = clean_backend.connect(profile)
    assert success is True
    assert clean_backend.connection is not None
    assert clean_backend.engine is not None

def test_sql_execute_query_ddl_and_select(clean_backend):
    profile = {
        'auth_type': 'uri',
        'uri': 'sqlite:///:memory:'
    }
    clean_backend.connect(profile)
    
    # Test DDL
    ddl = "CREATE TABLE test_users (id INTEGER PRIMARY KEY, name TEXT)"
    success, msg, cols, data = clean_backend.execute_query(ddl)
    assert success is True
    
    # Test DML
    dml = "INSERT INTO test_users (name) VALUES ('Alice'), ('Bob')"
    success, msg, cols, data = clean_backend.execute_query(dml)
    assert success is True
    
    # Test Select
    select_query = "SELECT * FROM test_users"
    success, msg, cols, data = clean_backend.execute_query(select_query)
    assert success is True
    assert cols == ['id', 'name']
    assert len(data) == 2
    assert data[0][1] == 'Alice'
    assert data[1][1] == 'Bob'

def test_sql_execute_query_error(clean_backend):
    profile = {
        'auth_type': 'uri',
        'uri': 'sqlite:///:memory:'
    }
    clean_backend.connect(profile)
    
    # Invalid query
    success, msg, cols, data = clean_backend.execute_query("SELECT * FROM non_existent_table")
    assert success is False
    assert "no such table" in msg.lower()
