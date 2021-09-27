"""Site-wide mixins"""

class GetObjectMixin:
    """Cache object so as to prevent hitting database multiple times."""

    def get_object(self):
        print("in get_object mixin")
        if not hasattr(self, '_object'):
            self._object = super().get_object()
        return self._object