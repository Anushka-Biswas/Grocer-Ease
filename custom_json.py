from flask.json import JSONEncoder as FlaskJSONEncoder
from bson import ObjectId
from mongoengine.base import BaseDocument
from mongoengine.queryset.base import BaseQuerySet

class CustomJSONEncoder(FlaskJSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, (BaseDocument, BaseQuerySet)):
            return str(obj.to_json())
        return super().default(obj)

def override_json_encoder(app):
    app.json_encoder = CustomJSONEncoder

