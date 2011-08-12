## Script (Python) "get_owner"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##¨
#

return context.restrictedTraverse('@@get_owner')()
