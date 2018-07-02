from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite


def is_trash_profile_installed():
    portal_setup = getToolByName(getSite(), 'portal_setup')
    return portal_setup.getLastVersionForProfile('ftw.trash:default') != 'unknown'
