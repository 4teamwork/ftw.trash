from ftw.trash.interfaces import ITrashed
from plone.indexer import indexer
from zope.interface import Interface


@indexer(Interface)
def trashed_indexer(obj):
    """Indexer for the `trashed` index, this index is used to filter trashed
    objects from catalog search results by default.
    """
    return ITrashed.providedBy(obj)
