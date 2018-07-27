from ftw.upgrade import UpgradeStep


class Add_CleanTrash_permission(UpgradeStep):
    """Add "Clean trash" permission.
    """

    def __call__(self):
        self.install_upgrade_profile()
