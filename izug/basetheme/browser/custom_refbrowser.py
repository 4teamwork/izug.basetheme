from archetypes.referencebrowserwidget.browser.view import \
    ReferenceBrowserPopup as base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ReferenceBrowserPopup(base):
    """Custom popup which works without sprites"""
    template_custom = ViewPageTemplateFile('no_sprites_popup.pt')

    def __call__(self):
        self.update()

        # Reoverride template
        return self.template_custom()
