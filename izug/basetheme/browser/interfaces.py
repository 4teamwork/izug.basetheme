from plone.theme.interfaces import IDefaultPloneLayer

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """

class IZugWebsiteSpecific(IThemeSpecific):
    """Marker interface for zug.ch
    """
    