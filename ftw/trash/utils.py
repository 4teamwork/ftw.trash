from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import isLinked
from zope.component.hooks import getSite
import inspect


def is_trash_profile_installed():
    portal_setup = getToolByName(getSite(), 'portal_setup')
    return portal_setup.getLastVersionForProfile('ftw.trash:default') != 'unknown'


def within_link_integrity_check():
    """Returns True when we are within a link integrity check.
    """
    frame = inspect.currentframe()
    while True:
        frame = frame.f_back
        if frame is None:
            return False

        if frame.f_code == isLinked.func_code:
            return True


def called_from_ZMI(request):
    """Returns True when the object deletion was called from ZMI.
    """
    if request is None:
        return None
    return request.PUBLISHED.__name__ == 'manage_delObjects'
