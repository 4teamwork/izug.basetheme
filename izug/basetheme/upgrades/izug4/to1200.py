from ftw.upgrade import UpgradeStep
import logging


LOG = logging.getLogger('izug.basetheme.upgrades.izug4')


class AddTabbedviewCSS(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-izug.basetheme.upgrades.izug4:1200')
