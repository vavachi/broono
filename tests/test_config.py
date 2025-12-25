import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.config import ConfigManager

def test_config():
    print("Testing ConfigManager...")
    test_file = "test_profiles.json"
    
    # Clean up before test
    if os.path.exists(test_file):
        os.remove(test_file)
        
    manager = ConfigManager(test_file)
    
    # Test 1: Save Profile
    details = {
        'server': 'localhost',
        'database': 'TestDB',
        'username': 'sa',
        'password': 'password',
        'trusted': False
    }
    manager.save_profile("Test Profile", details)
    
    assert os.path.exists(test_file), "File should be created"
    
    # Test 2: Load Profile
    loaded = manager.get_profile("Test Profile")
    assert loaded == details, "Loaded details should match saved"
    
    # Test 3: Persistence
    manager2 = ConfigManager(test_file)
    loaded2 = manager2.get_profile("Test Profile")
    assert loaded2 == details, "Persistence check passed"
    
    # Test 4: Delete
    manager.delete_profile("Test Profile")
    assert manager.get_profile("Test Profile") is None, "Profile should be deleted"
    
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)
        
    print("ConfigManager Logic: PASS")

if __name__ == "__main__":
    test_config()
