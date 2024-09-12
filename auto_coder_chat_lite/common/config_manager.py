import os
import json

class ConfigManager:
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path

    def save(self, config):
        with open(self.config_file_path, 'w', encoding='utf-8') as config_file:
            json.dump(config, config_file, ensure_ascii=False, indent=4)
        print(f"Configuration saved to {self.config_file_path}")

    def load(self):
        with open(self.config_file_path, 'r', encoding='utf-8') as config_file:
            return json.load(config_file)