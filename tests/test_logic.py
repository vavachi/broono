import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.compare import SchemaComparer
from src.core.generator import ScriptGenerator

def test_logic():
    print("Setting up test schemas...")
    
    # Source: User wants this state
    source_schema = {
        'tables': {
            'dbo.Users': {
                'columns': {
                    'ID': {'type': 'int', 'nullable': False, 'length': None, 'precision': 10, 'scale': 0},
                    'Name': {'type': 'varchar', 'nullable': False, 'length': 100, 'precision': 0, 'scale': 0},
                    'Email': {'type': 'varchar', 'nullable': True, 'length': 255, 'precision': 0, 'scale': 0}
                }
            }
        },
        'procedures': {
            'dbo.GetUser': {'definition': 'CREATE PROCEDURE dbo.GetUser AS SELECT * FROM Users', 'type': 'SQL_STORED_PROCEDURE'}
        },
        'functions': {},
        'triggers': {}
    }

    # Target: Current DB state
    target_schema = {
        'tables': {
            'dbo.Users': {
                'columns': {
                    'ID': {'type': 'int', 'nullable': False, 'length': None, 'precision': 10, 'scale': 0},
                    'Name': {'type': 'varchar', 'nullable': False, 'length': 50, 'precision': 0, 'scale': 0}
                }
            }
        },
        'procedures': {
            'dbo.GetUser': {'definition': 'CREATE PROCEDURE dbo.GetUser AS SELECT ID FROM Users', 'type': 'SQL_STORED_PROCEDURE'}
        },
        'functions': {},
        'triggers': {}
    }

    print("Running Comparison...")
    comparer = SchemaComparer()
    diff = comparer.compare(source_schema, target_schema)
    
    # Assertions
    assert 'dbo.Users' in diff['tables']['modified'], "dbo.Users should be modified"
    assert 'dbo.GetUser' in diff['procedures']['modified'], "dbo.GetUser should be modified"
    
    print("Comparison Logic: PASS")
    
    print("Generating Script...")
    generator = ScriptGenerator()
    script = generator.generate(diff)
    
    print("-" * 20)
    print(script)
    print("-" * 20)
    
    assert "ALTER PROCEDURE dbo.GetUser" in script, "Script should alter GetUser"
    assert "ALTER TABLE dbo.Users ALTER COLUMN [Name] varchar(100) NOT NULL" in script, "Script should alter Name"
    
    print("Generation Logic: PASS")

if __name__ == "__main__":
    test_logic()
