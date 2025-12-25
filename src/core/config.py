import json
import os

class ConfigManager:
    def __init__(self, filename="profiles.json"):
        self.filename = filename
        self.profiles = self._load()

    def _load(self):
        if not os.path.exists(self.filename):
            return {}
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except:
            return {}

    def save_profile(self, name, details):
        """
        Saves a connection profile.
        details: dict with server, database, username, password, trusted
        """
        self.profiles[name] = details
        self._save_to_disk()

    def get_profile(self, name):
        return self.profiles.get(name)

    def get_all_profiles(self):
        return self.profiles

    def delete_profile(self, name):
        if name in self.profiles:
            del self.profiles[name]
            self._save_to_disk()

    def _save_to_disk(self):
        with open(self.filename, 'w') as f:
            json.dump(self.profiles, f, indent=4)
