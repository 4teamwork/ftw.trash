``ftw.trash`` is a Plone addon which modifies Plone's behavior when content is deleted.
When a user deletes content, it will not actually be deleted but rather marked as trashed.
Trashed content can then be restored when needed.

.. contents:: Table of Contents

Installation and usage
======================

- Be aware that ``ftw.trash`` requires and installs ``collective.deletepermission``.
- Add ``ftw.trash`` to the eggs in your buildout configuration:

  ::

      [instance]
      eggs +=
          ...
          ftw.trash

- Install the ``ftw.trash`` addon in Plone (Addons control panel or portal_setup or quickinstaller).
- Deleting content looks exactly as in standard Plone, but it does not actually delete the content
  but only hides it.
- Administrators can restore content with a global trash view, accessible via the user menu.
- Personal trashes are not implemented at the moment.

.. image:: https://github.com/4teamwork/ftw.trash/raw/master/docs/trash.png


Querying
--------

The catalog is patched, so that it includes the default query ``{'trashed': False}``.
This makes sure that we only work with 'untrashed' objects by default.

If you want to access trashed objects, you can simply use the query keyword ``trashed``
with one of these values:

- ``False``: only return objects which are not trashed.
- ``True``: only return objects which are trashed.
- ``None``: do not apply "trashed" filter, return both trashed and 'untrashed' objects.

These filters only apply when ``portal_catalog.searchResults`` is used.
When using ``portal_catalog.unrestrictedSearchResults`` the behavior is different,
especially for ``trashed=None``, since this method is not patched.


Methods for trashing and deleting
---------------------------------

``ftw.trash`` patches ``manage_delObjects`` so that it trashes the content instead of deleting
it. ``ftw.trash`` also adds new methods:

- ``parent.manage_trashObjects([id1, id2, ..])``: trashes the contents.
- ``parent.manage_immediatelyDeleteObjects(([id1, id2, ..])``: immediately deletes the contents
  without trashing it.
- ``parent.manage_delObjects([id1, id2, ..])``: trashes the contents. If called from ZMI (or
  within link integrity checker), the content is immediately deleted.

The patches are applied on the site root, on DX- and on AT-folders when ``ftw.trash``
is installed in the path.
For the methods to work properly, the Generic Setup profile must be installed as well.


Temporary disable trash feature
--------------------------------

You can either set the env variable ``DISABLE_FTW_TRASH`` manually, or use the provided context manager.

.. code:: python

    from ftw.trash.utils import temporary_disable_trash

    with temporary_disable_trash():
        self.portal.manage_delObjects([container1.getId()])



Setting the required permission for restoring content
-----------------------------------------------------

Restoring a page can be compared to adding a new page to its container.
Therefore by default we require the ``Add portal content`` permission on the parent in order to restore content.

However this can depend on the application and the content type - there are some content types
which can be seen as *part of* the content of their parents, in which case we'd like to
require the ``Modify portal content`` permission for the parent instead.
This can be modelled by simply registering an `IIsRestoreAllowedAdapter` for the
content type being restored. For example:

.. code:: python

  @implementer(IIsRestoreAllowedAdapter)
  @adapter(IMyType, IMyBrowserLayer)
  def is_restore_allowed_for_my_type(context, request):
      parent = aq_parent(aq_inner(context))
      return getSecurityManager().checkPermission('Modify portal content', parent)


Events
------

The following object events are fired:

- `ftw.trash.interfaces.IBeforeObjectTrashedEvent`: the object will be trashed.
- `ftw.trash.interfaces.IObjectTrashedEvent`: the object has been trashed.
- `ftw.trash.interfaces.IBeforeObjectRestoredEvent`: the object will be restored.
- `ftw.trash.interfaces.IObjectRestoredEvent`: the object has been restored.


Internals
=========

- When content is deleted, it is marked as ``ITrashed`` and ``IRestorable``, children are only
  marked as ``ITrashed``.
- Only the root node of the deleted structure can be restored and thus provides ``IRestorable``.
  Restoring children without their deleted parents is not possible since their parent(s) would be missing.
- Trashed content is not moved.
- The catalog's ``searchResults`` method is patched so that it filters trashed objects by default.
- The ``contentItems`` method is patched to exclude trashed content.
  It is used for ``listFolderContents`` and ``getFolderContents``.
- Trashed content is prevented from being published / accessed through the browser unless
  the user has the ``Manager`` role.
- For restoring content, the permissions ``Restore trashed content`` and ``Add portal content``
  are required. The ``Restore trashed content`` is granted by default to the roles
  ``Manager`` and ``Site Administrator`` on the site root.

Development
===========

1. Fork this repo
2. Clone your fork
3. Shell: ``ln -s development.cfg buildout.cfg``
4. Shell: ``python bootstrap.py``
5. Shell: ``bin/buildout``

Run ``bin/test`` to test your changes.

Or start an instance by running ``bin/instance fg``.


Links
=====

- Github: https://github.com/4teamwork/ftw.trash
- Issues: https://github.com/4teamwork/ftw.trash/issues
- Pypi: http://pypi.python.org/pypi/ftw.trash


Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.trash`` is licensed under GNU General Public License, version 2.
