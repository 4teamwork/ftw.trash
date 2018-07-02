from ftw.trash.trasher import Trasher


def manage_delObjects(self, ids=None, REQUEST=None):
    """Marks an object as trashed.
    """
    if ids is None:
        ids = []
    if isinstance(ids, basestring):
        ids = [ids]
    for id_ in ids:
        Trasher(self._getOb(id_)).trash()
