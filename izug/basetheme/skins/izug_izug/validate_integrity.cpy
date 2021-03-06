##title=Validate Integrity 
##bind container=container 
##bind context=context 
##bind namespace= 
##bind script=script 
##bind state=state 
##bind subpath=traverse_subpath 
##parameters= 
## 
 
from Products.Archetypes import PloneMessageFactory as _ 
from Products.Archetypes.utils import addStatusMessage 
 
request = context.REQUEST 
errors = {} 
errors = context.validate(REQUEST=request, errors=errors, data=1, metadata=0) 
 
if errors: 
    message = _(u'Please correct the indicated errors.') 
    addStatusMessage(request, message, type='error') 
    return state.set(status='failure', errors=errors) 
else: 
    if request.get('sendNotification'): 
        return state.set(status='send_notification', portal_status_message='Changes saved.') 
    message = _(u'Changes saved.') 
    addStatusMessage(request, message) 
    return state.set(status='success') 
