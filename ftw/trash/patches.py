from ftw.trash.interfaces import ITrashed
from ftw.trash.trasher import Trasher
from ftw.trash.utils import called_from_ZMI
from ftw.trash.utils import is_trash_profile_installed
from ftw.trash.utils import within_link_integrity_check


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
    if is_trash_profile_installed() and \
       not within_link_integrity_check() and \
       not called_from_ZMI(REQUEST):
        return self.manage_trashObjects(ids=ids, REQUEST=REQUEST)
    else:
        return self.manage_immediatelyDeleteObjects(ids=ids, REQUEST=REQUEST)


def manage_immediatelyDeleteObjects(self, ids=None, REQUEST=None):
    """Immediately delete an object instead of only trashing it.
    """
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


def _getFieldObjects(self, *args, **kwargs):
    return filter(lambda obj: not ITrashed.providedBy(obj),
                  self._old__getFieldObjects(*args, **kwargs))


def getRawActionAdapter(self, *args, **kwargs):
    adapter_ids = self._old_getRawActionAdapter(*args, **kwargs)
    adapter_result = []

    for adapter_id in adapter_ids:
        if not ITrashed.providedBy(self.get(adapter_id)):
            adapter_result.append(adapter_id)

    return tuple(adapter_result)
