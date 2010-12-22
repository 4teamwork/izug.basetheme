from Acquisition import aq_inner
from zope.interface import implements
from zope.component import getMultiAdapter

from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.utils import _checkPermission
from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import INavigationBreadcrumbs
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs
from plone.app.layout.navigation.root import getNavigationRoot
from Products.CMFPlone.browser.navigation import get_view_url


class PhysicalNavigationBreadcrumbs(grok.View):
    """ Breadcrumbs for navigation.
        If the user does not have 'View' permission on the item do not
        provide an url, just the title.
    """
    grok.name('breadcrumbs_view')
    grok.context(IContentish)
    grok.require('zope2.View')
    implements(INavigationBreadcrumbs)
    
    def render(self):
        """ required by grok """
        return

    def breadcrumbs(self):
        context = aq_inner(self.context)
        request = self.request
        container = utils.parent(context)

        try:
            name, item_url = get_view_url(context)
        except AttributeError:
            print context
            raise

        if container is None:
            return ({'absolute_url': item_url,
                     'Title': utils.pretty_title_or_id(context, context),
                    },)

        view = getMultiAdapter((container, request), name='breadcrumbs_view')
        base = tuple(view.breadcrumbs())

        # Some things want to be hidden from the breadcrumbs
        if IHideFromBreadcrumbs.providedBy(context):
            return base

        rootPath = getNavigationRoot(context)
        itemPath = '/'.join(context.getPhysicalPath())

        # don't show default pages in breadcrumbs or pages above the navigation root
        if not utils.isDefaultPage(context, request) and not rootPath.startswith(itemPath):
            base += ({'absolute_url': _checkPermission('View', context) and item_url or None,
                      'Title': utils.pretty_title_or_id(context, context),
                     },)

        return base