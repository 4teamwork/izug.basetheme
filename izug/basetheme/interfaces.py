from zope import schema
from zope.interface import Interface


class ISiteProperties(Interface):
    """Is used by livesearch field
    """

    application_title = schema.TextLine(
        title=u"Title of the application",
        default=u"Website")