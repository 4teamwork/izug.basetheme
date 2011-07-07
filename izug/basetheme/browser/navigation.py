from Acquisition import aq_inner
from zope.interface import implements
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _checkPermission
from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import INavigationBreadcrumbs
from Products.CMFPlone.browser.interfaces import INavigationTabs
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs

from plone.app.layout.navigation.root import getNavigationRoot
from Products.CMFPlone.browser.navigation import get_view_url
from zope.publisher.browser import BrowserView


class PhysicalNavigationBreadcrumbs(BrowserView):
    """ Breadcrumbs for navigation.
        If the user does not have 'View' permission on the item do not
        provide an url, just the title.
    """
    implements(INavigationBreadcrumbs)
    
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
        

class CatalogNavigationTabs(BrowserView):
    implements(INavigationTabs)

    def topLevelTabs(self, actions=None, category='portal_tabs'):
        context = aq_inner(self.context)

        portal_catalog = getToolByName(context, 'portal_catalog')
        portal_properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        site_properties = getattr(portal_properties, 'site_properties')

        # Build result dict
        result = []

        # check whether we only want actions
        if not site_properties.getProperty('disable_folder_sections', False):
            customQuery = getattr(context, 'getCustomNavQuery', False)
            if customQuery is not None and utils.safe_callable(customQuery):
                query = customQuery()
            else:
                query = {}
            
            rootPath = getNavigationRoot(context)
            query['path'] = {'query' : rootPath, 'depth' : 1}
            
            query['portal_type'] = utils.typesToList(context)
            
            sortAttribute = navtree_properties.getProperty('sortAttribute', None)
            if sortAttribute is not None:
                query['sort_on'] = sortAttribute
            
                sortOrder = navtree_properties.getProperty('sortOrder', None)
                if sortOrder is not None:
                    query['sort_order'] = sortOrder
            
            if navtree_properties.getProperty('enable_wf_state_filtering', False):
                query['review_state'] = navtree_properties.getProperty('wf_states_to_show', [])
            
            query['is_default_page'] = False
            
            if site_properties.getProperty('disable_nonfolderish_sections', False):
                query['is_folderish'] = True
            
            # Get ids not to list and make a dict to make the search fast
            idsNotToList = navtree_properties.getProperty('idsNotToList', ())
            excludedIds = {}
            for id in idsNotToList:
                excludedIds[id]=1
            
            rawresult = portal_catalog.searchResults(**query)
            
            # now add the content to results
            for item in rawresult:
                if not (excludedIds.has_key(item.getId) or item.exclude_from_nav):
                    id, item_url = get_view_url(item)
                    data = {'name'      : utils.pretty_title_or_id(context, item),
                            'id'         : item.getId,
                            'url'        : item_url,
                            'description': item.Description}
                    result.append(data)
                
        # actions are last for zug
        if actions is not None:
            for actionInfo in actions.get(category, []):
                data = actionInfo.copy()
                data['name'] = data['title']
                result.append(data)
        return result