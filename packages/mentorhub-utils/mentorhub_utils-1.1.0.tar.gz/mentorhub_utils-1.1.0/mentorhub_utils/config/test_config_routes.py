import unittest
from flask import Flask
from mentorhub_utils.config.config_routes import create_config_routes
from mentorhub_utils.flask_utils.ejson_encoder import MongoJSONEncoder

class TestConfigRoutes(unittest.TestCase):

    def setUp(self):
        # Set up the Flask test app and register the blueprint
        self.app = Flask(__name__)
        self.app.json = MongoJSONEncoder(self.app)        
        config_routes = create_config_routes()
        self.app.register_blueprint(config_routes, url_prefix='/api/config')
        self.client = self.app.test_client()

    def test_get_config_success(self):
        # Simulate a GET request to the /api/config endpoint
        response = self.client.get('/api/config/', headers={"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1c2VyX3JvbGVzIjpbIlN0YWZmIl0sIm1vbmdvX2lkIjoiYWFhYTAwMDAwMDAwMDAwMDAwMDAwMDAxIn0.ZBMSyki3fPetSyLaOj6Zln9uL8-GnXr5biWMwC-bG4KTWZwtS6kDWatbmKzviPG5aqKfFJgkgZOCeyI9RvvFDgjLStdslt-6yqzdTuu7k1ypscXwhrnxDQtMTdcsccpUqSvciTcbXuIycAexRz1SBvoxB8HHDri4gBQQUAybsQT3YCpI-hasNDWl1bqCFksJc7AeB9MCbwLEQteZ0nnYqXvE6T3a0Ncp6uGNoTXJKxw0QOqUOtqjyn2wPIf925AysVAv-cdnW0PhmuhkHuvz3D45EkVJvOtZKtmg-ywMtOzkPhqS_6J8eQOaCCFu2Co_HDBWMX1Dqw5o3PKbrKWMSg"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)

        data = response.get_json()
        self.assertIsInstance(data, dict)

if __name__ == '__main__':
    unittest.main()