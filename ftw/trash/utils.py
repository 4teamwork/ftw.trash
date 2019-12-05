from contextlib import contextmanager
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import isLinked
from zope.component.hooks import getSite
import inspect
import os


def is_trash_profile_installed():
    portal_setup = getToolByName(getSite(), 'portal_setup')
    return portal_setup.getLastVersionForProfile('ftw.trash:default') != 'unknown'


def is_trash_disabled():
    return os.environ.get('DISABLE_FTW_TRASH', None) == 'true'


def is_migrating_plone_site(obj):
    """Detects whether we are in a request which migrates Plone to a new version.
    In this case we want to disable the trash, because it may cause problems
    e.g. when deleting tools.
    """
    # obj may not be acquisition wrapped and may not have a request.
    # Fall back to Plone site.
    request = getattr(obj, 'REQUEST', None)
    if not request:
        request = getSite().REQUEST

    return request.steps and request.steps[-1] in (
        '@@plone-upgrade',  # ZMI TTW
        'plone_upgrade',  # ftw.upgrade
    )


@contextmanager
def temporary_disable_trash():

    os.environ['DISABLE_FTW_TRASH'] = 'true'
    try:
        yield
    finally:
        del os.environ['DISABLE_FTW_TRASH']


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


def filter_children_in_paths(paths):
    """Accepts a list of paths and returns a filtered list, where children are removed
    when their parents (or grandparents, etc.) are also included in the list.
    As a side effect, trailing slashes are removed.
    """
    paths = map(lambda path: os.path.join(path, ''), sorted(paths, reverse=True))
    for parent in paths[:]:
        for child in paths[:]:
            if parent != child and child.startswith(parent):
                paths.remove(child)
    return map(lambda path: path.rstrip('/'), sorted(paths))
