from zope.interface import Interface


class IRestorable(Interface):
    """Marker interface for objects which can be restored.
    """


class ITrashed(Interface):
    """Marker interface for trashed objects which should no longer appear.
    """


class IIsRestoreAllowedAdapter(Interface):
    """The IIsRestoreAllowedAdapter multi adapter decides whether an object can be
    restored or not.
    See the readme for usage details.
    """
