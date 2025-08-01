import werkzeug.exceptions

from flask import request
from joserfc import jwt
from joserfc.errors import JoseError
from joserfc.jwk import RSAKey
from werkzeug.datastructures import WWWAuthenticate

from mentorhub_utils.config.MentorHub_Config import MentorHub_Config

def create_token():

    config = MentorHub_Config.get_instance()

    encoded_jwt = request.authorization.token

    def get_key():
        key = RSAKey.import_key(config.API_KEY)

        return key

    def get_token(encoded_jwt, key):
        try:
            return jwt.decode(encoded_jwt, key)
        except JoseError as e:
            raise werkzeug.exceptions.Unauthorized(www_authenticate=WWWAuthenticate("bearer", {"realm": "mentorHub", "error": e.error, "error_description": e.description}))
        # Since `request.authorization` either returns an Authorization object or None, an AttributeError will be raised when the header is missing or lacks a token
        except AttributeError:
            # Exclude error information as per RFC 6750 section 3.1
            raise werkzeug.exceptions.Unauthorized(www_authenticate=WWWAuthenticate("bearer", {"realm": "mentorHub"}))

    key = get_key()
    token = get_token(encoded_jwt, key)

    return token.claims
