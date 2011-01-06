## Script (Python) "getContentColumnWidth"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=

session = context.REQUEST.get('SESSION')
if session:
    if session.get("contentColumnWidth") == None:
    	context.REQUEST.SESSION["contentColumnWidth"] = "80%"
    return context.REQUEST.SESSION.get("contentColumnWidth")
return "80%"