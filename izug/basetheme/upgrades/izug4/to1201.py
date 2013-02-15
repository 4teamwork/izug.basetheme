from ftw.upgrade import UpgradeStep


class ReorderViewlets(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-izug.basetheme.upgrades.izug4:1201')
