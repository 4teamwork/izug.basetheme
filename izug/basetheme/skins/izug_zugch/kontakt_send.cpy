## Controller Python Script "kontakt_send"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Send a message
##
REQUEST=context.REQUEST

from Products.CMFPlone.utils import transaction_note
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from ZODB.POSException import ConflictError
from Products.CMFPlone.utils import normalizeString
import DateTime
## This may change depending on the called (portal_feedback or author)
state_success = "success"
state_failure = "failure"

plone_utils = getToolByName(context, 'plone_utils')
urltool = getToolByName(context, 'portal_url')
portal = urltool.getPortalObject()
url = context.absolute_url()

## make these arguments?
sender_prename = REQUEST.get('sender_prename', '')
sender_surname = REQUEST.get('sender_surname', '')
sender_from_address = REQUEST.get('sender_from_address', '')
message = REQUEST.get('message', '')
sender_address = REQUEST.get('sender_address', '')
sender_zip = REQUEST.get('sender_zip', '')
sender_residence = REQUEST.get('sender_residence', '')
sender_phone = REQUEST.get('sender_phone', '')
sender_fullname = str(sender_prename) + ' ' + str(sender_surname)

try:
	send_to_address = context.getEmail()
except:
	send_to_address = portal.getProperty('contact_email_to_address')

subject = 'Kontaktformular: ' + context.Title()

state.set(status=state_success) ## until proven otherwise

host = context.MailHost # plone_utils.getMailHost() (is private)
encoding = portal.getProperty('email_charset')

variables = {
				'sender_from_address'   : sender_from_address,
				'sender_fullname'       : sender_fullname,
				'url'                   : url,
				'subject'               : subject,
				'message'               : message,
				'sender_address'        : sender_address,
				'sender_zip'            : sender_zip,
				'sender_residence'      : sender_residence,
				'sender_phone'          : sender_phone
			}

addHeaders = {'Reply-to':sender_from_address}

try:
    from_mail = portal.getProperty('contact_email_from_address')
    message = context.kontakt_template(context, **variables)
    if not 'contactmessages' in portal.objectIds():
        portal.manage_addProduct['OFSP'].manage_addFolder('contactmessages')
    contactmessages=portal.get('contactmessages')
    id_ = normalizeString(sender_prename +" "+ sender_surname, 'unicode')
    if id_ in contactmessages.objectIds():
        already_used = True
        i = 1
        while already_used == True:
            if id_ in contactmessages.objectIds():
                id_ = id_ + "-"+str(len(contactmessages.objectIds())+i)
                i += 1
            else:
                already_used = False
    contactmessages.manage_addProduct['OFSP'].manage_addFile(id=id_, title=subject)
    msg = contactmessages.get(id_)
    msg.manage_addProperty('filedata', message.encode('utf-8'), 'text')
    msg.manage_addProperty('sender', sender_from_address.encode('utf-8'), 'string')
    msg.manage_addProperty('senderfullname', sender_fullname.encode('utf-8'), 'string')
    msg.manage_addProperty('send_date', DateTime.now(), 'date')
    result = host.secureSend(message, send_to_address, from_mail, subject=subject, subtype='plain', charset=encoding, debug=False, **addHeaders)
except ConflictError:
    raise
# except: # TODO Too many things could possibly go wrong. So we catch all.
#     exception = plone_utils.exceptionString()
#     message = _(u'Unable to send mail: ${exception}',
#                 mapping={u'exception' : exception})
#     plone_utils.addPortalMessage(message, 'error')
#     return state.set(status=state_failure)

## clear request variables so form is cleared as well
REQUEST.set('sender_prename', None)
REQUEST.set('sender_surname', None)
REQUEST.set('sender_from_address', None)
REQUEST.set('message', None)
REQUEST.set('sender_address', None)
REQUEST.set('sender_zip', None)
REQUEST.set('sender_residence', None)
REQUEST.set('sender_phone', None)

##set "variables" for the success form
variables['sender_prename'] = sender_prename
variables['sender_surname'] = sender_surname
REQUEST.set('infos', variables)

plone_utils.addPortalMessage(_(u'Mail sent.'))
return state

