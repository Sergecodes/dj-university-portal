"""Site-wide mixins"""

class GetObjectMixin:
    """
    Cache object so as to prevent hitting database multiple times.
    Use this mixin in views that have UserPassesTestMixin to prevent multiple database fetches
    when doing `self.get_object()`
    """

    def get_object(self):
        if not hasattr(self, '_object'):
            self._object = super().get_object()
            
        return self._object

