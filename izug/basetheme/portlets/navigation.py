from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.portlets.portlets import navigation as plone_navigation
from plone.memoize.instance import memoize
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.interface import implements


class ZugNavigationRenderer(plone_navigation.Renderer):
    render = ViewPageTemplateFile('zug_navigation.pt')
    recurse = ViewPageTemplateFile('zug_navigation_recurse.pt')

    @memoize
    def getNavTree(self, _marker=None):
        if _marker is None:
            _marker = []
        context = aq_inner(self.context)
        queryBuilder = getMultiAdapter((context, self.data),
                                       INavigationQueryBuilder)
        strategy = getMultiAdapter((context, self.data),
                                   INavtreeStrategy)

        # <custom>
        # alyways sort by title
        queryBuilder.query['sort_on'] = 'sortable_title'
        queryBuilder.query['sort_order'] = ''
        # </custom>

        tree = buildFolderTree(context, obj=context,
                               query=queryBuilder(),
                               strategy=strategy)

        # <custom>
        tree['children'] = self.cleanup_nodes(tree['children'])
        tree = self.cleanup_nodes([tree])[0]
        # </custom>
        return tree

    def cleanup_nodes(self, nodes):
        """
        The cleanup method fixes various issues after generating the
        tree.
        Pass the 'children' list
        """
        for node in nodes:
            # fix currentItem
            any_child_is_currentParent = False
            for n in node.get('children', ()):
                if n['currentItem'] or n['currentParent']:
                    any_child_is_currentParent = True
                    break

            currentParent = node.get('currentParent')
            if currentParent and not any_child_is_currentParent:
                node['currentItem'] = True

            # walk down
            node['children'] = self.cleanup_nodes(node['children'])
        return nodes

    def root_is_current(self):
        return 'navTreeCurrentItem' in self.root_item_class()


class ZugNavtreeStrategy(plone_navigation.NavtreeStrategy):
    """The navtree strategy used for the default navigation portlet
    """
    implements(plone_navigation.INavtreeStrategy)
    adapts(Interface, plone_navigation.INavigationPortlet)

    def __init__(self, context, view=None):
        super(ZugNavtreeStrategy, self).__init__(context, view)
        self.showAllParents = False

    def nodeFilter(self, node):
        # we don't want to show elements that are to deep ..
        if self.bottomLevel != 0 and self.bottomLevel < node['depth']:
            return False

        # strictly do not display objects with "excludeFromNav" set
        if node['item'].exclude_from_nav:
            return False
        # strictly do not display types in
        # portal_properties/navtree_properties/metaTypesNotToList
        # or
        # portal_properties/zug_navi_properties/zugTypesNotToListInNavigation
        if node['item'].portal_type in self.get_excluded_types():
            return False
        if not node['currentItem'] and not node['currentParent'] and \
                node['item'].portal_type in self.get_excluded_sibling_types():
            return False
        return True

    def decoratorFactory(self, node):
        node = super(ZugNavtreeStrategy, self).decoratorFactory(node)

        node['link_remote'] = node['link_remote'] and \
            node['getRemoteUrl'] != 'http://'
        return node

    @memoize
    def get_excluded_types(self):
        portal_properties = getToolByName(self.context, 'portal_properties')
        excluded_types = list(
            portal_properties.navtree_properties.getProperty(
                'metaTypesNotToList',
                []))
        excluded_types += list(
            portal_properties.zug_navi_properties.getProperty(
                'zugTypesNotToListInNavigation',
                []))
        return excluded_types

    @memoize
    def get_excluded_sibling_types(self):
        """
        These types should be shown if they are currentItem or currentParent,
        otherwise they should be hidden.
        Configurable in
        portal_types.izug_theme_properties.navigation_hide_types_if_not_current
        """
        portal_properties = getToolByName(self.context, 'portal_properties')
        theme_props = portal_properties.zug_navi_properties
        types = list(theme_props.navigation_hide_types_if_not_current)
        return types
