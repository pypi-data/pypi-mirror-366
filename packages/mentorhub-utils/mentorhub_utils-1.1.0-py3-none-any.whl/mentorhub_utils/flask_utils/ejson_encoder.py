from flask.json.provider import DefaultJSONProvider as FlaskJSONProvider
import datetime
from bson.objectid import ObjectId

class MongoJSONEncoder(FlaskJSONProvider):
    def default(self, obj):
        if isinstance(obj, (ObjectId, datetime.datetime)):
            return str(obj)