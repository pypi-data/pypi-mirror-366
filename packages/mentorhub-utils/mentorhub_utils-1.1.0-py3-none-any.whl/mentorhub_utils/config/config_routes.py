import logging

logger = logging.getLogger(__name__)

from flask import Blueprint, jsonify
from mentorhub_utils.flask_utils import create_breadcrumb, create_token
from mentorhub_utils.config.MentorHub_Config import MentorHub_Config

# Define the Blueprint for config routes
def create_config_routes():
    config_routes = Blueprint('config_routes', __name__)
    config = MentorHub_Config.get_instance()
    
    # GET /api/config - Return the current configuration as JSON
    @config_routes.route('/', methods=['GET'])
    def get_config():
        try:
            # Return the JSON representation of the config object
            token = create_token()
            breadcrumb = create_breadcrumb(token)
            logger.info(f"Get Config Success {breadcrumb}")
            return jsonify(config.to_dict(token)), 200
        except Exception as e:
            logger.warning(f"Get Config Error has occurred: {e}")
            return jsonify({"error": "A processing error occurred"}), 500
        
    # Ensure the Blueprint is returned correctly
    return config_routes
