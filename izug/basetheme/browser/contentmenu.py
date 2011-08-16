from plone.app.contentmenu.view import ContentMenuProvider as PloneContentMenuProvider
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile


class ContentMenuProvider(PloneContentMenuProvider):
    """Adapter to handle sprites in the contentmenu
    Normally we could set the content_icon attribute from a contenttype to an empty string and plone
    automatically add a css class to the link and no icon. Because we need the content_icon for other templates
    to differ between contenttypes and mimetypes we cant set this attribute to an empty string.
    So we have to override the contentmenu-template that it always use css classes and no images
    """

    render = ZopeTwoPageTemplateFile('contentmenu.pt')
