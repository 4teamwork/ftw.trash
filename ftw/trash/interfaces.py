from zope.component.interfaces import IObjectEvent
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


class IBeforeObjectTrashedEvent(IObjectEvent):
    """An object will be trashed.
    """


class IObjectTrashedEvent(IObjectEvent):
    """An object has been trashed.
    """


class IBeforeObjectRestoredEvent(IObjectEvent):
    """An object will be restored.
    """


class IObjectRestoredEvent(IObjectEvent):
    """An object has been restored.
    """
