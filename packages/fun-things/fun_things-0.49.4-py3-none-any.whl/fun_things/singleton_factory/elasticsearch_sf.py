from . import SingletonFactory

try:
    from elasticsearch import Elasticsearch

    _exists = True

except Exception:
    _exists = False


class ElasticsearchSF(SingletonFactory["Elasticsearch"]):
    def _instantiate(self):
        if not _exists:
            raise ImportError("You don't have `elasticsearch` installed!")

        return Elasticsearch(  # type: ignore
            *self.args,
            **self.kwargs,
        )

    def _destroy(self):
        self.instance.close()

        return True
