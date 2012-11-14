from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import common


class ContentViews(common.ViewletBase):
    """Renders plone default contentview manager"""
    index = ViewPageTemplateFile('viewlets_templates/contentviews.pt')
