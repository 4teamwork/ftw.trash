from ftw.trash.trasher import Trasher
from ftw.trash.utils import is_trash_profile_installed


def manage_trashObjects(self, ids=None, REQUEST=None):
    """Marks objects as trashed.
    """
    if ids is None:
        ids = []
    if isinstance(ids, basestring):
        ids = [ids]
    for id_ in ids:
        Trasher(self._getOb(id_)).trash()


def manage_delObjects(self, ids=None, REQUEST=None):
    if is_trash_profile_installed():
        return self.manage_trashObjects(ids=ids, REQUEST=REQUEST)
    else:
        return self._old_manage_delObjects(ids=ids, REQUEST=REQUEST)
