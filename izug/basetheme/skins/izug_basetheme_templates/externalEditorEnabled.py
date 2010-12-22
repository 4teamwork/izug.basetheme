## Script (Python) "externalEditorEnabled" 
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Can an object be changed with the external editor and by the user
##
#
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import webdav_enabled

portal = getToolByName(context, 'portal_url').getPortalObject()
mtool = getToolByName(portal, 'portal_membership')

if mtool.isAnonymousUser():
    return False

# Temporary content cannot be changed through EE (raises AttributeError)
portal_factory = getToolByName(portal, 'portal_factory')
if portal_factory.isTemporary(context):
    return False

if not webdav_enabled(context, container):
    return False

# Object not locked ?
# note: you may comment out those two lines if you prefer to let the user to borrow the lock
if context.wl_isLocked():
    return False

allowed_types = [
    'opengever.document.document',
    ]
if context.portal_type not in allowed_types:
    return False

# document must contain data
if context.portal_type == 'opengever.document.document':
    if not context.file:
        return False

# Content may provide data to the external editor ?
return not not portal.externalEditLink_(context)
