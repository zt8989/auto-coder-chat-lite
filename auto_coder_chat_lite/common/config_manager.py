import os
import json

class ConfigManager:
    """
    A class to manage configuration files.
    """

    def __init__(self, config_file_path):
        """
        Initialize the ConfigManager with the path to the configuration file.
        
        :param config_file_path: The path to the configuration file.
        """
        self.config_file_path = config_file_path

    def save(self, config):
        """
        Save the configuration to the specified file.
        
        :param config: The configuration dictionary to save.
        """
        with open(self.config_file_path, 'w', encoding='utf-8') as config_file:
            json.dump(config, config_file, ensure_ascii=False, indent=4)

    def load(self):
        """
        Load the configuration from the specified file.
        
        :return: The configuration dictionary.
        """
        with open(self.config_file_path, 'r', encoding='utf-8') as config_file:
            return json.load(config_file)