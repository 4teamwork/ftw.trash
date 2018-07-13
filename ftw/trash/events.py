from ftw.trash.interfaces import IBeforeObjectRestoredEvent
from ftw.trash.interfaces import IBeforeObjectTrashedEvent
from ftw.trash.interfaces import IObjectRestoredEvent
from ftw.trash.interfaces import IObjectTrashedEvent
from zope.component.interfaces import ObjectEvent
from zope.interface import implementer


@implementer(IBeforeObjectTrashedEvent)
class BeforeObjectTrashedEvent(ObjectEvent):
    """An object will be trashed.
    """

    def __init__(self, object):
        self.object = object


@implementer(IObjectTrashedEvent)
class ObjectTrashedEvent(ObjectEvent):
    """An object has been trashed.
    """

    def __init__(self, object):
        self.object = object


@implementer(IBeforeObjectRestoredEvent)
class BeforeObjectRestoredEvent(ObjectEvent):
    """An object will be restored.
    """

    def __init__(self, object):
        self.object = object


@implementer(IObjectRestoredEvent)
class ObjectRestoredEvent(ObjectEvent):
    """An object has been restored.
    """

    def __init__(self, object):
        self.object = object
