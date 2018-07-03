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


def searchResults(self, REQUEST=None, **kw):
    kw = kw.copy()

    # Meaning of indexed values of 'trashed':
    # - True => object is trashed
    # - False => object is not trashed
    # - None => object is not properly indexed -> treat like False

    # Meaing and defaults when querying 'trashed':
    # - True => only return trashed objects
    # - False => return trashed objects (includes not properly indexed objects)
    # - None => return all objects, do not filter
    kw.setdefault('trashed', False)

    if kw['trashed'] is False:
        kw['trashed'] = [False, None]
    elif kw['trashed'] is None:
        kw['trashed'] = [True, False, None]

    return self._old_searchResults(REQUEST, **kw)
