from ftw.upgrade import UpgradeStep


class FixTrashActionName(UpgradeStep):
    """Fix trash action name.
    """

    def __call__(self):
        actions_tool = self.getToolByName('portal_actions')
        category = actions_tool.get('user')
        old_name = 'user_management'

        if old_name in category:
            action = category[old_name]
            if action.title == 'Trash':
                del category[old_name]

        self.install_upgrade_profile()
