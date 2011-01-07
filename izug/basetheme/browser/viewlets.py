from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from izug.basetheme.utils import get_version_and_config
from pkg_resources import iter_entry_points
from plone.app.layout.viewlets import common, content
from plone.memoize import ram
from plone.memoize.instance import memoize
from zope.component import getMultiAdapter

class PathBar(common.PathBarViewlet):
    index = ViewPageTemplateFile('viewlets_templates/pathbar.pt')


class SiteActions(common.SiteActionsViewlet):
    index = ViewPageTemplateFile('viewlets_templates/siteactions.pt')

    @ram.cache(lambda *a, **kw: True)
    def version(self):
        package_version_string = None
        for ep in iter_entry_points('izug.basetheme'):
            if ep.name == 'version':
                module = ep.load()
                package_version_string = getattr(module, 'VERSION', None)
                break

        if package_version_string:
            data = get_version_and_config()
            if len(data):
                return package_version_string % {'version': data[0]}
        return ''


class DocumentActions(content.DocumentActionsViewlet):
    index = ViewPageTemplateFile('viewlets_templates/documentactions.pt')


class Byline(content.DocumentBylineViewlet):
    index = ViewPageTemplateFile('viewlets_templates/byline.pt')
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

    @ram.cache(lambda *a, **kw: True)
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
