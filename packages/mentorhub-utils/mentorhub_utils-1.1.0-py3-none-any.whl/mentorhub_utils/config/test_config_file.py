import unittest
import os
from mentorhub_utils.config.MentorHub_Config import MentorHub_Config

class TestConfigFiles(unittest.TestCase):

    def setUp(self):
        """Re-initialize the config for each test."""
        self.config = MentorHub_Config.get_instance()
        
        # Set Config Folder location
        os.environ["CONFIG_FOLDER"] = "./test/config"

        # Initialize the Config object
        self.config.initialize()
        
        # Reset config folder location 
        del os.environ["CONFIG_FOLDER"]

    def test_file_string_properties(self):
        for key, default in {**self.config.config_strings, **self.config.config_string_secrets}.items():
            if key != "BUILT_AT" and key != "CONFIG_FOLDER" and key != "API_KEY":
                self.assertEqual(getattr(self.config, key), "TEST_VALUE")

    def test_file_int_properties(self):
        for key, default in self.config.config_ints.items():
            self.assertEqual(getattr(self.config, key), 9999)

    def test_file_json_secret_properties(self):
        for key, default in self.config.config_json_secrets.items():
            self.assertEqual(getattr(self.config, key), {"foo":"bat"})

    def test_file_string_ci(self):
        for key, default in self.config.config_strings.items():
            if key != "BUILT_AT" and key != "CONFIG_FOLDER":
                self._test_config_file_value(key, "TEST_VALUE")

    def test_file_int_ci(self):
        for key, default in self.config.config_ints.items():
            self._test_config_file_value(key, "9999")

    def test_file_secret_ci(self):
        for key, default in {**self.config.config_string_secrets, **self.config.config_json_secrets}.items():
            self._test_config_file_value(key, "secret")


    def _test_config_file_value(self, config_name, value):
        """Helper function to check file values."""
        items = self.config.config_items
        item = next((i for i in items if i['name'] == config_name), None)
        self.assertIsNotNone(item)
        self.assertEqual(item['name'], config_name)
        self.assertEqual(item['from'], "file")
        self.assertEqual(item['value'], value)

if __name__ == '__main__':
    unittest.main()