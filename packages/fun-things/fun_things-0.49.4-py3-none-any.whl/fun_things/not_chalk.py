from .lazy import lazy


@lazy
class NotChalk:
    """
    Just a placeholder if `simple-chalk` is not installed.

    This does nothing.
    """

    def __call__(self, v):
        return v

    def __getattribute__(self, _):
        return self
