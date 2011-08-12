## Script (Python) "checkReviewPortalContentPermission"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=find related items for an object
##

from izug.theme.interfaces import ICustomCheckReviewPortalContent
# XXX This is necessary because we can't call providedBy in a script
try:
    adapter = ICustomCheckReviewPortalContent(context)
    if adapter:
        return adapter()
except:
    pass

return ""

