from plone.app.contentmenu.view import ContentMenuProvider as PloneContentMenuProvider
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile


class ContentMenuProvider(PloneContentMenuProvider):
    """Adapter to handle sprites in the contentmenu
    """

    render = ZopeTwoPageTemplateFile('contentmenu.pt')
