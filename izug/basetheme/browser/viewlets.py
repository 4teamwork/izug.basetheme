from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import common, content
from plone.memoize.instance import memoize
from zope.component import getMultiAdapter

class PathBar(common.PathBarViewlet):
    index = ViewPageTemplateFile('viewlets_templates/pathbar.pt')


class SiteActions(common.SiteActionsViewlet):
    index = ViewPageTemplateFile('viewlets_templates/siteactions.pt')


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

