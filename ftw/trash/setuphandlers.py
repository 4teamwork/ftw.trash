# -*- coding: utf-8 -*-
import logging
from plone import api
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


PROFILE_ID = "profile-ftw.trash:default"
INDEXES = (("trashed", "FieldIndex"),)


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "plonetraining.testing:uninstall",
        ]


def post_install(context):
    """Post install script"""

    add_catalog_indexes(context)


def uninstall(context):
    """Uninstall script"""

    remove_catalog_indexes(context)


def add_catalog_indexes(context, logger=None):
    """Method to add our wanted indexes to the portal_catalog.

    @parameters:

    When called from the import_various method below, 'context' is
    the plone site and 'logger' is the portal_setup logger.  But
    this method can also be used as upgrade step, in which case
    'context' will be portal_setup and 'logger' will be None.
    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger("ftw.trash")

    logger.info(f"Start add_catalog_indexes")
    # Run the catalog.xml step as that may have defined new metadata
    # columns.  We could instead add <depends name="catalog"/> to
    # the registration of our import step in zcml, but doing it in
    # code makes this method usable as upgrade step as well.  Note that
    # this silently does nothing when there is no catalog.xml, so it
    # is quite safe.
    setup = api.portal.get_tool("portal_setup")
    setup.runImportStepFromProfile(PROFILE_ID, "catalog")

    catalog = api.portal.get_tool("portal_catalog")
    indexes = catalog.indexes()
    # Specify the indexes you want, with ('index_name', 'index_type')
    wanted = INDEXES
    indexables = []
    for name, meta_type in wanted:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
            logger.info("Added %s for field %s.", meta_type, name)
    if len(indexables) > 0:
        logger.info("Indexing new indexes %s.", ", ".join(indexables))
        catalog.manage_reindexIndex(ids=indexables)
    logger.info(f"Completed add_catalog_indexes")


def remove_catalog_indexes(context, logger=None):
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger("ftw.trash")

    logger.info(f"Start remove_catalog_indexes")
    catalog = api.portal.get_tool("portal_catalog")
    indexes = catalog.indexes()

    for name, meta_type in INDEXES:
        if name in indexes:
            catalog.delIndex(name)
            logger.info(f"Delete index {name}")
    logger.info(f"Completed remove_catalog_indexes")
