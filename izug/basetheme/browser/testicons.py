from zope.publisher.browser import BrowserView
from plone.memoize.instance import memoize
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getMultiAdapter, queryUtility
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.Expression import createExprContext
from Products.CMFCore.utils import getToolByName
from zope.site.hooks import getSite
from zope.i18n import translate


BAD_TYPES = ("ATBooleanCriterion", "ATDateCriteria", "ATDateRangeCriterion",
             "ATListCriterion", "ATPortalTypeCriterion", "ATReferenceCriterion",
             "ATSelectionCriterion", "ATSimpleIntCriterion", "Plone Site",
             "ATSimpleStringCriterion", "ATSortCriterion",
             "Discussion Item", "TempFolder", "ATCurrentAuthorCriterion",
             "ATPathCriterion", "ATRelativePathCriterion", )


class TestIconsView(BrowserView):

    @memoize
    def content_types(self):
        context = aq_inner(self.context)
        request = self.request
        portal_state = getMultiAdapter((context, request), name='plone_portal_state')
        site = getSite()
        ttool = getToolByName(site, 'portal_types', None)
        idnormalizer = queryUtility(IIDNormalizer)
        expr_context = createExprContext(
            aq_parent(context), portal_state.portal(), context)
        if ttool is None:
            return []
        results = []
        for t in ttool.listContentTypes():
            if t not in BAD_TYPES:
                fti = ttool[t]
                typeId = fti.getId()
                cssId = idnormalizer.normalize(typeId)
                cssClass = 'contenttype-%s' % cssId
                icon = fti.getIconExprObject()
                if icon:
                    icon = icon(expr_context)
                results.append({ 'id'           : typeId,
                                 'title'        : fti.Title(),
                                 'description'  : fti.Description(),
                                 'action'       : None,
                                 'selected'     : False,
                                 'icon'         : icon,
                                 'extra'        : {'id' : cssId, 'separator' : None, 'class' : cssClass},
                                 'submenu'      : None,
                                })
        results = [(translate(ctype['title'], context=request), ctype) for ctype in results]
        results.sort()
        results = [ctype[-1] for ctype in results]
        return results
