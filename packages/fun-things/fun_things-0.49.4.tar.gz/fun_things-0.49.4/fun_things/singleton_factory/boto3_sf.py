from . import SingletonFactory

try:
    import boto3

    _exists = True

except Exception:
    _exists = False


class Boto3SF(SingletonFactory):
    def _instantiate(self):
        if not _exists:
            raise ImportError("You don't have `boto3` installed!")

        return boto3.client(  # type: ignore
            *self.args,
            **self.kwargs,
        )

    def _destroy(self):
        self.instance.close()

        return True
