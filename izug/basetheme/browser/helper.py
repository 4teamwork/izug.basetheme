from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility


def css_class_from_obj(item):
    normalize = getUtility(IIDNormalizer).normalize
    if not item.portal_type == 'opengever.document.document':
        css_class = "contenttype-%s" % normalize(item.portal_type)
    else:
        # It's a document, we therefore want to display an icon
        # for the mime type of the contained file
        icon = item.getIcon()
        if not icon == '':
            # Strip '.gif' from end of icon name and remove leading 'icon_'
            filetype = icon[:icon.rfind('.')].replace('icon_', '')
            css_class = 'icon-%s' % normalize(filetype)
        else:
            # Fallback for unknown file type
            css_class = "contenttype-%s" % normalize(item.portal_type)
    return css_class
