## Script (Python) "getLeftColumnWidth"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=



session = context.REQUEST.get('SESSION')
if session:
    if context.REQUEST.SESSION.get("leftColumnWidth") == None:
        context.REQUEST.SESSION["leftColumnWidth"] = "20%"
    return context.REQUEST.SESSION.get("leftColumnWidth")
return "20%"