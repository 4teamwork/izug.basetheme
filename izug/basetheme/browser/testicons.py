from zope.publisher.browser import BrowserView
from plone.memoize.instance import memoize
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getMultiAdapter, queryUtility
from Acquisition import aq_inner, aq_parent
from Products.CMFCore.Expression import createExprContext
from Products.CMFCore.utils import getToolByName
from zope.i18n import translate
from operator import itemgetter


BAD_TYPES = ("ATBooleanCriterion", "ATDateCriteria", "ATDateRangeCriterion",
             "ATListCriterion", "ATPortalTypeCriterion", "ATReferenceCriterion",
             "ATSelectionCriterion", "ATSimpleIntCriterion", "Plone Site",
             "ATSimpleStringCriterion", "ATSortCriterion",
             "Discussion Item", "TempFolder", "ATCurrentAuthorCriterion",
             "ATPathCriterion", "ATRelativePathCriterion", )

ALL_CONTENT_TYPES = {             
            'contenttype-albumblock': 'Bildgalerie',
            'contenttype-banner': 'Banner',
            'contenttype-block': 'Block',
            'contenttype-blog-category': 'Blog Category',
            'contenttype-blog-entry': 'Blog Entry',
            'contenttype-blog': 'Blog',
            'contenttype-changeset': 'ChangeSet',
            'contenttype-content-page': 'Content Page',
            'contenttype-course': 'Course',
            'contenttype-coursecategory': 'CourseCategory',
            'contenttype-document': 'Page',
            'contenttype-event': 'Event',
            'contenttype-favorite': 'Favorite',
            'contenttype-fieldsetfolder': 'Fieldset Folder',
            'contenttype-file': 'File',
            'contenttype-flowplayerblock': 'FlowPlayerBlock',
            'contenttype-folder': 'Folder',
            'contenttype-formbooleanfield': 'Boolean Field',
            'contenttype-formcustomscriptadapter': 'Custom Script Adapter',
            'contenttype-formdatefield': 'Date/Time Field',
            'contenttype-formfilefield': 'File Field',
            'contenttype-formfixedpointfield': 'Fixed-Point Field',
            'contenttype-formfolder': 'Form Folder',
            'contenttype-formintegerfield': 'Integer Field',
            'contenttype-formlabelfield': 'Label Field',
            'contenttype-formlinesfield': 'Lines Field',
            'contenttype-formmaileradapter': 'Mailer Adapter',
            'contenttype-formmultiselectionfield': 'Multi-Select Field',
            'contenttype-formpasswordfield': 'Password Field',
            'contenttype-formrichlabelfield': 'Rich Label Field',
            'contenttype-formrichtextfield': 'RichText Field',
            'contenttype-formsavedataadapter': 'Save Data Adapter',
            'contenttype-formselectionfield': 'Selection Field',
            'contenttype-formstringfield': 'String Field',
            'contenttype-formtextfield': 'Text Field',
            'contenttype-formthankspage': 'Thanks Page',
            'contenttype-ftw-mail-mail': 'Mail',
            'contenttype-geolocation': 'Location',
            'contenttype-htmlblock': 'HTML Block',
            'contenttype-image': 'Image',
            'contenttype-kita-folder': 'Kita Folder',
            'contenttype-kita': 'Kita',
            'contenttype-large-plone-folder': 'Large Folder',
            'contenttype-lebenslage': 'Lebenslage',
            'contenttype-lebenslagealias': 'Alias',
            'contenttype-link': 'Link',
            'contenttype-masterselectdemo': 'Master Select Demo',
            'contenttype-medienmitteilung': 'Medienmitteilung',
            'contenttype-mitglied': 'Mitglied',
            'contenttype-mitgliedblock': 'Mitgliedblock',
            'contenttype-news-item': 'News Item',
            'contenttype-news': 'Aktuell',
            'contenttype-newsordner': 'AktuellOrdner',
            'contenttype-opengever-contact-contact': 'Contact',
            'contenttype-opengever-contact-contactfolder': 'ContactFolder',
            'contenttype-opengever-document-document': 'Document',
            'contenttype-opengever-dossier-businesscasedossier': 'Business Case Dossier',
            'contenttype-opengever-dossier-projectdossier': 'Project Dossier',
            'contenttype-opengever-dossier-templatedossier': 'Template Dossier',
            'contenttype-opengever-inbox-forwarding': 'Forwarding',
            'contenttype-opengever-inbox-inbox': 'Inbox',
            'contenttype-opengever-inbox-yearfolder': 'YearFolder',
            'contenttype-opengever-repository-repositoryfolder': 'RepositoryFolder',
            'contenttype-opengever-repository-repositoryroot': 'RepositoryRoot',
            'contenttype-opengever-task-task': 'Task',
            'contenttype-opengever-tasktemplates-tasktemplate': 'TaskTemplate',
            'contenttype-opengever-tasktemplates-tasktemplatefolder': 'TaskTemplateFolder',
            'contenttype-orgunit': 'OrgUnit',
            'contenttype-refegovservice': 'RefEgovService',
            'contenttype-remark': 'Remark',
            'contenttype-stelle': 'Stelle',
            'contenttype-stellenordner': 'StellenOrdner',
            'contenttype-subsite': 'Subsite',
            'contenttype-topic': 'Collection',
            'contenttype-vernehmlassung': 'Vernehmlassung',
            'contenttype-vernehmlassungsordner': 'VernehmlassungsOrdner',
            'contenttype-zugevent': 'ZugEvent',
            'contenttype-zugeventfolder': 'Event Folder',
            'contenttype-zugeventlandingpage': 'Landing Page',
            'contenttype-zughomefolder': 'ZugHomeFolder',
            'contenttype-zugimmo': 'ZugImmo',
            'contenttype-zugimmofolder': 'Immo Folder',
            'contenttype-zugimmolandingpage': 'Landing Page',
            'contenttype-zugkantonsratsvorlage': 'ZugKantonsratsvorlage',
            'contenttype-zugkantonsratsvorlagenordner': 'ZugKantonsratsvorlagenOrdner',
            'contenttype-zugmerkliste': 'ZugMerkliste',
            'contenttype-zugnewsletter': 'ZugNewsletter',
            'contenttype-arbeitsraum': 'Arbeitsraum',
            'contenttype-billboardad': 'BillboardAd',
            'contenttype-billboardcategory': 'BillboardCategory',
            'contenttype-buch': 'Buch',
            'contenttype-buchblock': 'BuchBlock',
            'contenttype-buchhtmlblock': 'BuchHTMLBlock',
            'contenttype-discussionitem': 'DiscussionItem',
            'contenttype-egovform': 'EGovForm',
            'contenttype-graphicblock': 'GraphicBlock',
            'contenttype-izugfolder': 'IZugFolder',
            'contenttype-kapitel': 'Kapitel',
            'contenttype-meeting': 'Meeting',
            'contenttype-meetingitem': 'MeetingItem',
            'contenttype-poodle': 'Poodle',
            'contenttype-shopitem': 'ShopItem',
            'contenttype-subarbeitsraum': 'SubArbeitsraum',
            'contenttype-table': 'Table',
            'contenttype-task': 'Aufgabe',
            'contenttype-ticket': 'Ticket',
            'contenttype-ticketbox': 'TicketBox',
            'contenttype-ticketattachment': 'TicketAttachment',
            'contenttype-webdocument': 'WebDocument',
            'contenttype-zugnewsseite': 'ZugNewsseite'}

class TestIconsView(BrowserView):
    all_content_types = ALL_CONTENT_TYPES

    @memoize
    def content_types(self):
        context = aq_inner(self.context)
        request = self.request
        portal_state = getMultiAdapter((context, request), name='plone_portal_state')
        site = portal_state.portal()
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
                # if cssClass in self.all_content_types.keys():
                #     del(self.all_content_types[cssClass])
                try:
                    icon = fti.getIconExprObject()
                    if icon:
                        icon = icon(expr_context)
                except AttributeError: # we are using plone 3
                    icon = "%s/%s" % (site.absolute_url(), fti.getIcon())
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

    def other_content_types(self):
        """returns other content types
        """
        #return self.all_content_types.sort(key=lambda x: x[1]) 
        return sorted(self.all_content_types.items(), key=itemgetter(1))