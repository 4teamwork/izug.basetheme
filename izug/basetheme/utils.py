from Products.CMFCore.utils import getToolByName
from plone.memoize import ram
from zope.app.component.hooks import getSite
import ConfigParser
import os


@ram.cache(lambda *a, **kw: True)
def get_version_and_config():
    infos = []

    # find buildout config file
    path = os.path.abspath('.')
    buildoutcfg = None
    while path and path != '/':
        buildoutcfg = os.path.join(path, 'buildout.cfg')
        bindir = os.path.join(path, 'bin')
        if os.path.isfile(buildoutcfg) and os.path.isdir(bindir):
            break
        else:
            buildoutcfg = None
            path, foo = os.path.split(path)

    if not buildoutcfg:
        return

    # lets load the buildout config recursively and find the kgs url
    # which is used. there may be several!
    parser = ConfigParser.SafeConfigParser()
    loaded = []
    http_loads = []

    def load_extends(file_, dir_):
        path = os.path.join(dir_, file_)
        if path in loaded:
            return

        loaded.append(path)

        if file_.startswith('http'):
            http_loads.append(file_)
            return

        parser.read(path)
        if parser.has_option('buildout', 'extends'):
            extend_files = parser.get('buildout', 'extends').split()
            parser.remove_option('buildout', 'extends')
            for ext in extend_files:
                load_extends(ext, os.path.dirname(path))

    load_extends(os.path.basename(buildoutcfg),
                 os.path.abspath(os.path.dirname(buildoutcfg)))

    # lets get the last entry from http_loads which containts kgs and
    # extract the version from that url.
    http_loads.reverse()
    kgs_urls = filter(lambda url: 'kgs.4teamwork.ch' in url, http_loads)
    version = ''
    if kgs_urls:
        foo, version = os.path.split(kgs_urls[0])

        site = getSite()
        mtool = getToolByName(site, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        if 'Manager' in member.getRolesInContext(site):
            infos.append('<a href="%s" target="_blank">%s</a>' % (
                    kgs_urls[0], version))

    # also include the buildout.cfg effective name if it is a symlink
    try:
        effective_url = os.readlink(buildoutcfg)
    except OSError:
        pass
    else:
        infos.append(os.path.basename(effective_url))

    return infos

