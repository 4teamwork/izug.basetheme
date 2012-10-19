from ftw.upgrade import UpgradeStep
import logging


LOG = logging.getLogger('izug.basetheme.upgrades.opengever')


class AddTabbedviewCSS(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-izug.basetheme.upgrades.opengever:1200')
