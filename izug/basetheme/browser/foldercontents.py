from Acquisition import aq_inner
from OFS.interfaces import IOrderedContainer
from plone.app.content.browser.foldercontents import FolderContentsTable
from plone.app.content.browser.foldercontents import FolderContentsView
from plone.app.content.browser.tableview import Table, TableKSSView
from Products.ATContentTypes.interface import IATTopic
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.i18n import translate

import urllib


class IzugFolderContentsView(FolderContentsView):
    """Customized izug folder_contents
    Check https://extranet.4teamwork.ch/support/zug/maintlog/1583
    Behaviour:
    * Default sort-order is alphabetical (sortable_title)
    * Use sortAttribute and sortOrder, if available
    * Plone-root is using plone-default folder_contents
      (Registred on IBaseObject)
    * Columntitle is clickable and triggers js-sort
    * The sortable row is only available if sortAttribute is manuall
      (getObjPositionInParent), on plone root or on some explicit configuered
      types (Default: Folder)
    * Batchsize is 50
    * Column type: show title not the icon.
    """

    def contents_table(self):
        table = IzugFolderContentsTable(aq_inner(self.context), self.request)
        return table.render()


class IzugFolderContentsTable(FolderContentsTable):
    """
    The foldercontents table renders the table and its actions.
    """

    def __init__(self, context, request, contentFilter={}):
        self.context = context
        self.request = request
        self.contentFilter = contentFilter
        self.update_filter()

        url = context.absolute_url()
        view_url = url + '/@@folder_contents'
        self.table = IzugTable(request, url, view_url, self.items,
                           show_sort_column=self.show_sort_column,
                           buttons=self.buttons)

    def update_filter(self):
        content_filter = {}

        # Huck for js sort on table
        if 'sort_on' in self.contentFilter:
            return

        # Default is sortable_title
        content_filter['sort_on'] = 'sortable_title'
        # Look for available sort attr.
        sort_on = self.context.aq_explicit.get('sortAttribute', None)
        sort_order = self.context.aq_explicit.get('sortOrder', None)
        if sort_on:
            content_filter['sort_on'] = sort_on
        if sort_order:
            content_filter['sort_order'] = sort_order
        self.contentFilter.update(content_filter)
        # Fix for kss update_table - THIS SHOULD BE DONE BY PLONE!!
        if sort_on:
            self.request.set('sort_on', sort_on)

    @property
    def orderable(self):
        """
        """

        iface = IOrderedContainer.providedBy(aq_inner(self.context))

        # Some types should be always orderable
        # XXX: Use a propertysheet
        if self.context.Type() in ['Folder', ] and iface:
            return True

        attr = self.context.aq_explicit\
            .get('sortAttribute', '') == 'getObjPositionInParent'
        if self.contentFilter.get('sort_on', '') != 'getObjPositionInParent':
            return False
        return iface and attr
    
    @property
    def items(self):
        """ 
        """
        context = aq_inner(self.context)
        plone_utils = getToolByName(context, 'plone_utils')
        plone_view = getMultiAdapter((context, self.request), name=u'plone')
        portal_workflow = getToolByName(context, 'portal_workflow')
        portal_properties = getToolByName(context, 'portal_properties')
        portal_types = getToolByName(context, 'portal_types')
        site_properties = portal_properties.site_properties

        use_view_action = site_properties.getProperty('typesUseViewActionInListings', ())
        browser_default = context.browserDefault()

        if IATTopic.providedBy(context):
            contentsMethod = context.queryCatalog
        else:   
            contentsMethod = context.getFolderContents

        results = []
        for i, obj in enumerate(contentsMethod(self.contentFilter)):
            if (i + 1) % 2 == 0:
                table_row_class = "draggable even"
            else:
                table_row_class = "draggable odd"

            url = obj.getURL()
            path = obj.getPath or "/".join(obj.getPhysicalPath())
            icon = plone_view.getIcon(obj);

            type_class = 'contenttype-' + plone_utils.normalizeString(
                obj.portal_type)

            review_state = obj.review_state
            state_class = 'state-' + plone_utils.normalizeString(review_state)
            relative_url = obj.getURL(relative=True)

            fti = portal_types.get(obj.portal_type)
            if fti is not None:
                type_title_msgid = fti.Title()
            else:
                type_title_msgid = obj.portal_type
            url_href_title = u'%s: %s' % (translate(type_title_msgid,
                                                    context=self.request),
                                          safe_unicode(obj.Description))

            modified = plone_view.toLocalizedTime(
                obj.ModificationDate, long_format=1)

            obj_type = obj.Type
            if obj_type in use_view_action:
                view_url = url + '/view'
            elif obj.is_folderish:
                view_url = url + "/folder_contents"              
            else:
                view_url = url

            is_browser_default = len(browser_default[1]) == 1 and (
                obj.id == browser_default[1][0])

            results.append(dict(
                url = url,
                url_href_title = url_href_title,
                id  = obj.getId,
                quoted_id = urllib.quote_plus(obj.getId),
                path = path,
                title_or_id = obj.pretty_title_or_id(),
                obj_type = obj_type,
                size = obj.getObjSize,
                modified = modified,
                icon = icon.html_tag(),
                type_class = type_class,
                wf_state = review_state,
                state_title = portal_workflow.getTitleForStateOnType(review_state,
                                                           obj_type),
                state_class = state_class,
                is_browser_default = is_browser_default,
                folderish = obj.is_folderish,
                relative_url = relative_url,
                view_url = view_url,
                table_row_class = table_row_class,
                is_expired = context.isExpired(obj),
            ))
        return results


class FolderContentsKSSView(TableKSSView):
    table = IzugFolderContentsTable


class IzugTable(Table):
    render = ViewPageTemplateFile("table.pt")
