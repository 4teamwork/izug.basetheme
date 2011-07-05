## Script (Python) "addZugMerklisteToHomeFolder"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.CMFPlone import PloneMessageFactory as _


plone_root = context.portal_url.getPortalObject()
mtool = context.portal_membership
isAnon = mtool.isAnonymousUser()

state = context.restrictedTraverse("@@plone_context_state")
view_url_backup = '%s/%s' % (context.absolute_url(), state.view_template_id())

view_url = context.REQUEST.get('HTTP_REFERER', view_url_backup) #+'#portal-message'

RESPONSE = context.REQUEST.RESPONSE
putils = context.plone_utils

if context == plone_root:
  #XXX replace with a status message
  putils.addPortalMessage(_(u'merkliste_message_root',default=u'You can not use this action on plone root'), 'error')
  return RESPONSE.redirect(view_url)

objectUID = context.UID()
title = context.pretty_title_or_id

if isAnon:
  putils.addPortalMessage(_(u'merkliste_message_register',default=u'only registered user can use this function.'), 'error')
  return RESPONSE.redirect(view_url + "#" + objectUID)



#get members home folder
member = mtool.getAuthenticatedMember()
if not member:
  putils.addPortalMessage(_(u'merkliste_message_admin',default=u'you are a Portel Administrator, without user profil'), 'error')
  return RESPONSE.redirect(view_url + "#" + objectUID)

homefolder = member.getHomeFolder()

#create the object

#get the created Object
try:
  id ='fav_' + str(int( context.ZopeTime()))
  newid = homefolder.invokeFactory(id=id,type_name='ZugMerkliste',favObj=objectUID)
  homefolder[newid].setTitle(context.Title())
  

except:
  putils.addPortalMessage(_(u'merkliste_message_somereason',default=u'for some reasons the object could not be created, it is possible your homefolder does no exist'), 'error')
  return RESPONSE.redirect(view_url  + "#" + objectUID)

putils.addPortalMessage(_(u'merkliste_message_added',default=u'added to Merkliste'),'info')
return RESPONSE.redirect(view_url  + "#" + objectUID)
