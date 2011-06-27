from zope.interface import implements, Interface
from zope.component import adapts
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from plone.memoize.instance import memoize
from plone.app.portlets.portlets import navigation as plone_navigation


class ZugNavigationRenderer(plone_navigation.Renderer):
    render = ViewPageTemplateFile('zug_navigation.pt')
    recurse = ViewPageTemplateFile('zug_navigation_recurse.pt')

    sort_attributes = {
            'sortable_title': 'Title',
            'getObjPositionInParent': 'getObjPositionInParent',
            'created': 'created',
            'effective': 'effective',
            'modified': 'modified'}

    @memoize
    def getNavTree(self, _marker=None):
        tree = super(ZugNavigationRenderer, self).getNavTree(_marker)
        tree['children'] = self.cleanup_nodes(tree['children'])
        tree = self.cleanup_nodes([tree])[0]
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
            if currentParent and currentParent \
                and not any_child_is_currentParent:
                node['currentItem'] = True
            # sort children
            node = self.sort_children(node)
            # walk down
            node['children'] = self.cleanup_nodes(node['children'])
        return nodes

    def sort_children(self, node):

        def subSorter(node):
            sortAttribute = node.get('sortAttribute', '')
            if sortAttribute=='getObjPositionInParent' \
                or sortAttribute not in self.sort_attributes.keys():
                # already sorted by catalog or no valid sortAttribute
                return node
            else:
                sortAttribute = self.sort_attributes[sortAttribute]
            children = list(node['children'])
            children.sort(
                lambda a, b: cmp(
                    a.get(sortAttribute, ''),
                    b.get(sortAttribute, '')))
            if node.get('sortOrder', '') == 'descending':
                children.reverse()
            node['children'] = children
            return node
        # ------------------
        # remove aktuell, it should be always at the bottom
        aktuell = None
        for n in node['children']:
            if n['item'].id=='aktuell':
                aktuell = n
                node['children'].remove(n)
                break
        # sort with subSorter
        node = subSorter(node)
        # readd aktuell
        if aktuell:
            node['children'].append(aktuell)
        return node

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
        if self.bottomLevel!=0 and self.bottomLevel<node['depth']:
            return False
        # we want to see objects with id "aktuell"
        if node['item'].id=='aktuell':
            return True
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
        
        # sortAttribute and sortOrder should be stored on the brain
        node['sortAttribute'] = getattr(
            node['item'],
            'sortAttribute',
            'getPositionInParent')
        node['sortOrder'] = getattr(
            node['item'],
            'sortOrder',
            '')
            
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
