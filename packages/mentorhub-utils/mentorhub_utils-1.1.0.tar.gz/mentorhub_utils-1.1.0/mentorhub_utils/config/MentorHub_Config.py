import os
import json
from pathlib import Path

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MentorHub_Config:
    _instance = None  # Singleton instance

    def __init__(self):
        if MentorHub_Config._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            MentorHub_Config._instance = self
            self.config_items = []
            self.versions = []
            self.enumerators = {}
            self.CONFIG_FOLDER = "./"
            
            # Declare instance variables to support IDE code assist
            self.BUILT_AT = ''
            self.LOGGING_LEVEL = ''
            self.CONFIG_FOLDER = ''
            self.MONGO_DB_NAME = ''
            self.CURRICULUM_COLLECTION_NAME = ''
            self.ENCOUNTERS_COLLECTION_NAME = ''
            self.PARTNERS_COLLECTION_NAME = ''
            self.PATHS_COLLECTION_NAME = ''
            self.PEOPLE_COLLECTION_NAME = ''
            self.PLANS_COLLECTION_NAME = ''
            self.RATINGS_COLLECTION_NAME = ''
            self.REVIEWS__COLLECTION_NAME = ''
            self.TOPICS_COLLECTION_NAME = ''
            self.VERSION_COLLECTION_NAME = ''
            self.ENUMERATORS_COLLECTION_NAME = ''
            self.CURRICULUM_UI_URI = ''
            self.ENCOUNTER_UI_URI = ''
            self.PARTNERS_UI_URI = ''
            self.PEOPLE_UI_URI = ''
            self.TOPICS_UI_URI = ''
            self.SEARCH_UI_URI = ''
            self.CURRICULUM_API_PORT = 0
            self.ENCOUNTER_API_PORT = 0
            self.PARTNERS_API_PORT = 0
            self.PEOPLE_API_PORT = 0
            self.TOPICS_API_PORT = 0
            self.SEARCH_API_PORT = 0
            self.ELASTIC_INDEX_NAME = ""
            self.MONGO_CONNECTION_STRING = ""
            self.ELASTIC_CLIENT_OPTIONS = {}
            self.API_KEY = ''
    
            # Default Values grouped by value type            
            self.config_strings = {
                "BUILT_AT": "LOCAL",
                "CONFIG_FOLDER": "./",
                "LOGGING_LEVEL": "INFO", 
                "MONGO_DB_NAME": "mentorHub",
                "CURRICULUM_COLLECTION_NAME": "curriculum",
                "ENCOUNTERS_COLLECTION_NAME": "encounters",
                "PARTNERS_COLLECTION_NAME": "partners",
                "PATHS_COLLECTION_NAME": "paths",
                "PEOPLE_COLLECTION_NAME": "people",
                "PLANS_COLLECTION_NAME": "plans",
                "RATINGS_COLLECTION_NAME": "ratings",
                "REVIEWS__COLLECTION_NAME": "reviews",
                "TOPICS_COLLECTION_NAME": "topics",
                "VERSION_COLLECTION_NAME": "msmCurrentVersions",
                "ENUMERATORS_COLLECTION_NAME": "enumerators",
                "CURRICULUM_UI_URI": "http://localhost:8089/",
                "ENCOUNTER_UI_URI": "http://localhost:8091/",
                "PARTNERS_UI_URI": "http://localhost:8085/",
                "PEOPLE_UI_URI": "http://localhost:8083/",
                "TOPICS_UI_URI": "http://localhost:8087/",
                "SEARCH_UI_URI": "http://localhost:8080/"
            }
            self.config_ints = {
                "CURRICULUM_API_PORT": "8088",
                "ENCOUNTER_API_PORT": "8090",
                "PARTNERS_API_PORT": "8084",
                "PEOPLE_API_PORT": "8082",
                "TOPICS_API_PORT": "8086",
                "SEARCH_API_PORT": "8081"
            }
            self.config_string_secrets = {
                "ELASTIC_INDEX_NAME": "mentorhub", 
                "MONGO_CONNECTION_STRING": "mongodb://mongodb:27017/?replicaSet=rs0",
                "API_KEY": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqHGgfkNCTiFeRWDOr3ip\nr452VyEmnQ99UBSK1Og9QjKT1mMTzOpUogJIj9hEmuquAFg4al8DQqqFxFqm64zr\nblgJxO4RDw1vxKxUVSVR+IYypxxh/NC/fLF78bGfsDj7jMM/bKCl40Y3t8OUXRxt\nrxXw53M2EzRSGQSzf2YhGRwxBtQ5vUulfQjLHdqKhn54GoBf0sWSFcCspCGnDAuw\nvyjeG+OkeeNLaAO+A0vrg/T3OFKXYkhG+OJaKW7eh3PeMNKw10naoZNx2d3ig5vR\nIul3wl8oL7I4wp/FKQtGkKgBhsTGe6+2FN+TghKErprUXuSq6zw1Qrta29wo9P7r\nMwIDAQAB\n-----END PUBLIC KEY-----\n"
            }
            self.config_json_secrets = {
                "ELASTIC_CLIENT_OPTIONS": '{"node":"http://localhost:9200"}',
            }

            # Initialize configuration
            self.initialize()

    def initialize(self):
        """Initialize configuration values."""
        self.config_items = []
        self.versions = []
        self.enumerators = {}

        # Initialize Config Strings
        for key, default in self.config_strings.items():
            value = self._get_config_value(key, default, False)
            setattr(self, key, value)
            
        # Initialize Config Integers
        for key, default in self.config_ints.items():
            value = int(self._get_config_value(key, default, False))
            setattr(self, key, value)
            
        # Initialize String Secrets
        for key, default in self.config_string_secrets.items():
            value = self._get_config_value(key, default, True)
            setattr(self, key, value)

        # Initialize JSON Secrets
        for key, default in self.config_json_secrets.items():
            value = json.loads(self._get_config_value(key, default, True))
            setattr(self, key, value)

        # Set Logging Level
        logging.basicConfig(level=self.LOGGING_LEVEL)
        logger.info(f"Configuration Initialized: {self.config_items}")
            
    def _get_config_value(self, name, default_value, is_secret):
        """Retrieve a configuration value, first from a file, then environment variable, then default."""
        value = default_value
        from_source = "default"

        # Check for config file first
        file_path = Path(self.CONFIG_FOLDER) / name
        if file_path.exists():
            value = file_path.read_text().strip()
            from_source = "file"
            
        # If no file, check for environment variable
        elif os.getenv(name):
            value = os.getenv(name)
            from_source = "environment"

        # Record the source of the config value
        self.config_items.append({
            "name": name,
            "value": "secret" if is_secret else value,
            "from": from_source
        })
        return value

    # Serializer
    def to_dict(self, token):
        """Convert the Config object to a dictionary with the required fields."""
        return {
            "config_items": self.config_items,
            "versions": self.versions,
            "enumerators": self.enumerators,
            "token": token
        }    

    # Singleton Getter
    @staticmethod
    def get_instance():
        """Get the singleton instance of the Config class."""
        if MentorHub_Config._instance is None:
            MentorHub_Config()
        return MentorHub_Config._instance
        