## Script (Python) "referencebrowser_context"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Determine whether to show an id in an edit form
# 
# 

context = context
at_url = context.REQUEST.get('at_url')
at_uid = context.REQUEST.get('at_uid')

fieldName = context.REQUEST.get('fieldName');
try:
    at_obj =  context.restrictedTraverse(at_url)
#XXX import of Unauthorized not allowed in script 
# except Unauthorized:
except:
    if '/portal_factory/' in at_url:
        relative_path = str(at_url[len('/'.join(context.getPhysicalPath()))+1:])
        if not len(relative_path):
            at_obj = context
        else:
            at_obj =  context.restrictedTraverse(relative_path)   
    elif fieldName.startswith('crit__'):
        at_obj = context.restrictedTraverse(at_url)
    else:
        results = context.portal_catalog(UID=at_uid);
        if len(results):
            at_obj = results[0].getObject()
    
return at_obj