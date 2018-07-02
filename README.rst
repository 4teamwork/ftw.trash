``ftw.trash`` is a Plone addon modifying the behavior when deleting content.
When a user deletes content, it will actually not be deleted but marked as trashed.
Trashed content can then be restored when needed.

.. contents:: Table of Contents

Installation and usage
----------------------

- Add ``ftw.trash`` to the eggs in your buildout configuration:

  ::

      [instance]
      eggs +=
          ...
          ftw.trash

- Install the ``ftw.trash`` addon in Plone (Addons control panel or portal_setup or quickinstaller).
- Be aware that ``ftw.trash`` requires and installs ``collective.deletepermission``.


Internals
---------

- When content is deleted, it is marked as ``ITrashed`` and ``IRestorable``, children are only
  marked as ``ITrashed``.
- Only the root node of the deleted structure can be restored and thus provides ``IRestorable``.
  Restoring children without their deleted parents cannot work since the parent is missing.
- Trashed content is not moved.


Development
-----------

1. Fork this repo
2. Clone your fork
3. Shell: ``ln -s development.cfg buildout.cfg``
4. Shell: ``python bootstrap.py``
5. Shell: ``bin/buildout``

Run ``bin/test`` to test your changes.

Or start an instance by running ``bin/instance fg``.


Links
-----

- Github: https://github.com/4teamwork/ftw.trash
- Issues: https://github.com/4teamwork/ftw.trash/issues
- Pypi: http://pypi.python.org/pypi/ftw.trash


Copyright
---------

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.trash`` is licensed under GNU General Public License, version 2.
