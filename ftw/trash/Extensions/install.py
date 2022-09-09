from plone.api.portal import get_tool

def uninstall(self):
    setup_tool = get_tool("portal_setup")
    setup_tool.runAllImportStepsFromProfile(
        "profile-ftw.trash:uninstall", ignore_dependencies=True
    )
