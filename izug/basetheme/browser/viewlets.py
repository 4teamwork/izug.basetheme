from AccessControl import getSecurityManager
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from izug.basetheme import MessageFactory as _
from izug.basetheme.browser.helper import css_class_from_obj
from izug.basetheme.interfaces import ISiteProperties
from izug.basetheme.utils import get_version_and_config
from pkg_resources import iter_entry_points
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.viewlets import common, content
from plone.memoize import ram
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry
from random import randrange
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError


class PathBar(common.PathBarViewlet):
    index = ViewPageTemplateFile('viewlets_templates/pathbar.pt')

    def update(self):
        super(PathBar, self).update()
        template_info = None
        translation = None
        if 'PUBLISHED' in self.context.REQUEST and hasattr(self.context.REQUEST['PUBLISHED'], 'getId'):
            template_info = self.context.REQUEST['PUBLISHED'].getId()
            translation = self.context.translate(msgid=template_info,mapping=None,context=self.context)
        if template_info==translation:
            self.template_text = None
        else:
            self.template_text = translation

class PersonalBar(common.PersonalBarViewlet):
    index = ViewPageTemplateFile('viewlets_templates/personal_bar.pt')

class ZugPersonalBar(common.PersonalBarViewlet):
    index = ViewPageTemplateFile('viewlets_templates/zug_personal_bar.pt')

class IZugPersonalBar(common.PersonalBarViewlet):
    index = ViewPageTemplateFile('viewlets_templates/izug_personal_bar.pt')

class SiteActions(common.SiteActionsViewlet):
    index = ViewPageTemplateFile('viewlets_templates/siteactions.pt')

    @ram.cache(lambda *a, **kw: getSecurityManager().getUser().getId())
    def version(self):
        package_version_string = None
        for ep in iter_entry_points('izug.basetheme'):
            if ep.name == 'version':
                module = ep.load()
                package_version_string = getattr(module, 'VERSION', None)
                break

        if package_version_string:
            data = get_version_and_config(version_template=package_version_string)
            if len(data):
                return data[0]
        return ''

class ZugSiteActions(common.SiteActionsViewlet):
    """Custom site actions viewlet for zug.ch
    """
    index = ViewPageTemplateFile('viewlets_templates/zug_siteactions.pt')

    def update(self):
        super(ZugSiteActions, self).update()
        portal_root = getToolByName(self.context,'portal_url').getPortalObject()
        nav_root = getNavigationRoot(self.context)

        if nav_root != '/'.join(portal_root.getPhysicalPath()):
            parent_nav_root = getNavigationRoot(aq_parent(self.context.restrictedTraverse(nav_root)))
            parent_obj = self.context.restrictedTraverse(parent_nav_root)
        else:
            parent_obj = portal_root

        self.backtoparent_link = parent_obj.absolute_url()
        self.backtoparent_title = getattr(parent_obj,'title',',Kanton Zug')

class ZugEditMenu(common.ViewletBase):
    render = ViewPageTemplateFile('viewlets_templates/zug_edit_menu.pt')

    def getWorkflowState(self):
        context = self.context
        request = context.request
        context_state = getMultiAdapter((context, request), name='plone_context_state')
        plone_tools = getMultiAdapter((context, request), name='plone_tools')
        state = context_state.workflow_state()
        workflows = plone_tools.workflow().getWorkflowsFor(self.context)
        if workflows:
            for w in workflows:
                if w.states.has_key(state):
                    return w.states[state].title or state


class DocumentActions(content.DocumentActionsViewlet):
    index = ViewPageTemplateFile('viewlets_templates/documentactions.pt')


class DocumentActionsIzug4(content.DocumentActionsViewlet):
    index = ViewPageTemplateFile('viewlets_templates/documentactions.pt')

    def update(self):
        content.DocumentActionsViewlet.update(self)
        self.actions = self.get_actions()

    def get_actions(self):
        """Returns all document actions but lists first those from the
        actions tool, then those from the types tool.
        The default document actions viewlet has the opposite order.
        """
        context = aq_inner(self.context)
        atool = getToolByName(context, "portal_actions")
        ttool = getToolByName(context, "portal_types")

        category = 'document_actions'

        actions = []
        actions.extend(atool.listActionInfos(
            object=context,
            categories=(category, )))

        actions.extend(ttool.listActionInfos(
            object=context,
            category=category))

        return actions


class Byline(content.DocumentBylineViewlet):
    index = ViewPageTemplateFile('viewlets_templates/byline.pt')

    def css_class_from_obj(self):
        return css_class_from_obj(self.context)

    @memoize
    def workflow_state(self):
        context = aq_inner(self.context)
        state = self.context_state.workflow_state()
        self.tools = getMultiAdapter((context, context.REQUEST), name='plone_tools')
        workflows = self.tools.workflow().getWorkflowsFor(self.context.aq_explicit)
        if workflows:
            for w in workflows:
                if w.states.has_key(state):
                    return w.states[state].title or state


class DebugInfo(common.TitleViewlet):

    index = ViewPageTemplateFile('viewlets_templates/debug_info.pt')

    @ram.cache(lambda *a, **kw: getSecurityManager().getUser().getId())
    def get_debug_information(self):
        # only show debug information if another package requests that
        # with an entry point. izug.basetheme does not display it by
        # default.
        some_package_requests_debug = False
        for ep in iter_entry_points('izug.basetheme'):
            if ep.name == 'debug':
                some_package_requests_debug = True
                break

        if not some_package_requests_debug:
            return ''

        data = get_version_and_config()
        if data:
            return ', '.join(data)
        else:
            return ''


class Banner(common.ViewletBase):
    render = ViewPageTemplateFile('viewlets_templates/banner.pt')

    @property
    def available(self):
        context = aq_inner(self.context).aq_explicit
        if INavigationRoot.providedBy(context) and getattr(context, 'bannerbilder', None):
            return True
        return False

    def update(self):
        if not self.available:
            return
        context = aq_inner(self.context)
        self.img_path = '%s/default_banner.jpg' % context.portal_url()
        self.img_title = context.Title
        #check for folder 'bannerbilder'
        bannerfolder = getattr(context.aq_explicit,'bannerbilder',False)
        if bannerfolder:
            all_imgs = context.portal_catalog({'portal_type':['Banner',],
                                               'path':'/'.join(bannerfolder.getPhysicalPath()),
                                               'review_state':['published_internet','published']})

            counted = len(all_imgs)
            if counted:
                randomized = randrange(1,int(counted)+1,1)
                self.img_path = all_imgs[randomized-1].getURL()
                self.img_title = all_imgs[randomized-1].Title

# for izug only
class ZugBylineViewlet(content.DocumentBylineViewlet):
    @memoize
    def show(self):
        if self.getWorkflowState() not in ["published_internet", "revision"] or "behoerden" not in self.context.getPhysicalPath():
            return False
        properties = self.tools.properties()
        site_properties = getattr(properties, 'site_properties')
        anonymous = self.portal_state.anonymous()
        allowAnonymousViewAbout = site_properties.getProperty('allowAnonymousViewAbout', True)
        return not anonymous or allowAnonymousViewAbout

    @memoize
    def effective(self):
        effective = self.context.effective()
        if effective.year() > 1900:
            return self.context.effective()

    def getWorkflowState(self):
        context = self.context
        request = context.request
        context_state = getMultiAdapter((context, request), name='plone_context_state')
        plone_tools = getMultiAdapter((context, request), name='plone_tools')
        state = context_state.workflow_state()
        workflows = plone_tools.workflow().getWorkflowsFor(self.context)
        if workflows:
            for w in workflows:
                if w.states.has_key(state):
                    return w.states[state].title or state
    index = ViewPageTemplateFile("viewlets_templates/izug_document_byline.pt")

class ContentMenuViewlet(common.ViewletBase):
    render = ViewPageTemplateFile('viewlets_templates/izug_dropdown_content_menu.pt')
    def show_menu(self):
        if IPloneSiteRoot.providedBy(self.context):
            return False
        if 'arbeitsplatz' in self.context.getPhysicalPath() and not self.context.restrictedTraverse('within_book')():
            return True
        if not self.context.restrictedTraverse('@@plone').showEditableBorder():
            return False
        return int(self.context.request.get('izug_edit_mode', 0))

class SearchBoxViewlet(common.SearchBoxViewlet):
    render = ViewPageTemplateFile('viewlets_templates/searchbox.pt')

    def get_search_title(self):

        # If the Registrykey or the registry itself is not available we
        # need a fallback. In this case you have to run the registry.xml
        try:
            registry = getUtility(IRegistry)
            app_title = registry.forInterface(ISiteProperties).application_title
        except (ComponentLookupError, KeyError):
            app_title = "Website"

        searchtext = _(
            u"searchbox_title",
            default=u'Search ${text}',
            mapping={'text': app_title})

        return searchtext


class GeverSearchBoxViewlet(SearchBoxViewlet):
    render = ViewPageTemplateFile('viewlets_templates/gever_searchbox.pt')


class IZugSearchBoxViewlet(SearchBoxViewlet):
    render = ViewPageTemplateFile('viewlets_templates/izug_searchbox.pt')
