from datetime import datetime
from json import JSONEncoder

try:
    from bson import ObjectId
except Exception:

    class ObjectId:
        pass


class GenericJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)

        if isinstance(o, datetime):
            return o.isoformat()

        return JSONEncoder.default(self, o)
