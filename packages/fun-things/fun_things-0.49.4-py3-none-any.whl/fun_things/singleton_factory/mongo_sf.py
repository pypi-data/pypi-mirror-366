from . import SingletonFactory

try:
    from pymongo import MongoClient

    _exists = True

except Exception:
    _exists = False


class MongoSF(SingletonFactory["MongoClient"]):
    def _instantiate(self):
        if not _exists:
            raise ImportError("You don't have `pymongo` installed!")

        return MongoClient(  # type: ignore
            *self.args,
            **self.kwargs,
        )

    def _destroy(self):
        self.instance.close()

        return True
