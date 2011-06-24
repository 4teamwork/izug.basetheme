## Controller Python Script "validate_registration"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=name='',familyname='',username='',email='',password='',password_confirm='', form_of_adress=''
##title=validates the Registration of a User

from Products.CMFPlone import PloneMessageFactory as _

reg_tool=context.portal_registration
def missing(field):
    state.setError(field, _(u'This field is required, please provide some information.'), 'input_required')
def nomatch(field):
    state.setError(field, _(u'Passwords do not match.'), 'nomatch_password')
def minlimit(field):
    state.setError(field, _(u'Passwords must contain at least 5 letters.'), 'min_password')
def notallowed(field):
    state.setError(field, _(u'This username is reserved. Please choose a different name.'), 'not_allowed')

portal = context.portal_url.getPortalObject()


#set email adress as username if username is empty.
if not username:
    username = email
    context.REQUEST.form['username'] = username

if not name:
    missing('name')
if not familyname:
    missing('familyname')
if not username:
    missing('username')
if not email:
    missing('email')
if username and username == portal.getId():
    notallowed('username')
if not form_of_adress:
    missing('form_of_adress')

if not portal.validate_email:
     if password!=password_confirm:
         nomatch('password')
         nomatch('password_confirm')

     if not password:
         missing('password')
     if not password_confirm:
         missing('password_confirm')

     if not state.getError('password') and len(password) < 5:
         minlimit('password')
         minlimit('password_confirm')

if not state.getError('username') and not reg_tool.isMemberIdAllowed(username):
    state.setError('username',
                   _(u'zug_reserved_userid'),
                   'username_invalid' )

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'zug_error_on_register_message'), 'error')
    return state.set(status='failure')

city = context.REQUEST.get('city','')
zip = context.REQUEST.get('zip','')
if zip and city:
    city_plz = '%s %s'%(zip,city)
else:
    city_plz = ''

context.REQUEST.set('fullname', '%s %s'%(name, familyname))
context.REQUEST.set('city_plz', city_plz)


return state
