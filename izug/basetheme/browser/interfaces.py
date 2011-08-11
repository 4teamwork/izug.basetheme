from plone.theme.interfaces import IDefaultPloneLayer

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """

class IOpengeverSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer specific for OpenGever.
    """

class IIzugSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer specific for izug.
    """

