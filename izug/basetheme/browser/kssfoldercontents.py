from izug.basetheme.browser.foldercontents import IzugFolderContentsTable
from plone.app.content.browser.tableview import TableKSSView


class FolderContentsKSSView(TableKSSView):
    table = IzugFolderContentsTable
