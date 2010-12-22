## Script (Python) "external_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=http://cmf.zope.org/Members/tseaver/20020723_external_editor_available

from Products.PythonScripts.standard import url_quote
from DateTime import DateTime
user_agent = context.REQUEST.get('HTTP_USER_AGENT')

if 'Mac' in user_agent:
  return context.REQUEST['RESPONSE'].redirect(
    '%s/externalEdit_/%s.zem?macosx=1&%s' % (context.aq_parent.absolute_url(),
                             url_quote(context.getId()),DateTime().millis()))
else:
  return context.REQUEST['RESPONSE'].redirect(
    '%s/externalEdit_/%s?%s' % (context.aq_parent.absolute_url(),
                             url_quote(context.getId()),DateTime().millis()))
