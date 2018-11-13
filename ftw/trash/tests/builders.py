from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder
from ftw.builder.archetypes import ArchetypesBuilder


class DXFolderBuilder(DexterityBuilder):
    portal_type = 'dxfolder'


class FormFolderBuilder(ArchetypesBuilder):
    portal_type = 'FormFolder'


builder_registry.register('FormFolder', FormFolderBuilder)
