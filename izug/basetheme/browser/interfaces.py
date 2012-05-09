from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface


class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 skin layer.
    """


class IOpengeverSpecific(Interface):
    """Marker interface that defines a Zope 3 browser layer specific for
    OpenGever.
    """


class IIzugSpecific(Interface):
    """Marker interface that defines a Zope 3 browser layer specific for izug.
    """


class IIzug4Specific(Interface):
    """Marker interface that defines a Zope 3 browser layer specific for izug.
    """


class IZugSpecific(Interface):
    """Marker interface that defines a Zope 3 browser layer specific for zug.
    """


class IDirectorySpecific(Interface):
    """Marker Interface for directories"""
