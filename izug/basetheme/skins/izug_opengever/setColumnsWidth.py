## Script (Python) "setColumnsWidth"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=left,content
##title=
context.REQUEST.SESSION["leftColumnWidth"] = left
context.REQUEST.SESSION["contentColumnWidth"] = content
