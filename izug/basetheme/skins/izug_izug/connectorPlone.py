## Script (Python) "connectorPlone"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=Command='',Type='',CurrentFolder='',NewFolderName=''
##title=
##


from Products.PythonScripts.standard import html_quote
from Products.CMFCore.utils import getToolByName
from Products.FCKeditor.utils import fckCreateValidZopeId, decodeQueryString, encodeString



request = context.REQUEST
session = request.get('SESSION', None)
RESPONSE =  request.RESPONSE
dicoRequest = request.form
queryString = decodeQueryString(request.QUERY_STRING)
message_error=""
sCurrentFolder =""
portal = context.portal_url.getPortalObject()
portal_url = portal.absolute_url()
server_url = request.SERVER_URL
portal_path = portal_url.replace(server_url,'')

# 1. get config

# Path to user files relative to the document root.
# change it to force browser and upload path
ConfigUserFilesPath=""

# get fck Plone params
field_name = session and session.get('field_name', None) or ''
    
macro="rich"
if field_name :
    try:
        field = context.schema[field_name]
    except:
        # some plone products (ex : PloneBoard) are using wysiwyg support without AT field
        field = None
    if field :    
        widget = field.widget
        macro = widget.macro    
if macro == 'fckwidget':  
   fckParams = widget.getBrowserValues(context)
else:
   fckParams=context.getFck_params()



# special review_states 
# (unpublished states for contents which need to be hidden to local_roles
# not in fck prefs rolesSeeUnpublishedContent even with View permission )
unpublishedStates=fckParams['fck_unpublished_states']

# special local_roles who can see unpublished contents according to permissions
# by default set to fck unpublished view roles (fck prefs) 
rolesSeeUnpublishedContent = fckParams['fck_unpublished_view_roles']

# PloneArticle based meta_types
pa_meta_types = fckParams['pa_meta_types']

# RichDocumented based portal types
rd_portal_types = fckParams['rd_portal_types']

# Folder portal type
folder_portal_type = fckParams['folder_portal_type']

# Allowed and denied extensions dictionaries

ConfigAllowedExtensions = {"File":None,
                           "Image":("jpg","gif","jpeg","png"),
                           "Flash":("swf","fla"),
                           "Media":("flv",
                                    "avi",
                                    "mpg",
                                    "mpeg",
                                    "mp1",
                                    "mp2",
                                    "mp3",
                                    "mp4",
                                    "wma",
                                    "wmv",
                                    "wav",
                                    "mid",
                                    "midi",
                                    "rmi",
                                    "rm",
                                    "ram",
                                    "rmvb",
                                    "mov",
                                    "qt")}
ConfigDeniedExtensions =  {"File":("py",
                                   "cpy",
                                   "pt",
                                   "cpt",
                                   "dtml",
                                   "php",
                                   "asp",
                                   "aspx",
                                   "ascx",
                                   "jsp",
                                   "cfm",
                                   "cfc",
                                   "pl",
                                   "bat",
                                   "exe",
                                   "com",
                                   "dll",
                                   "vbs",
                                   "js",
                                   "reg"),
                          "Image":None,
                          "Flash":None,
                          "Media":None}

# set link by UID for AT content Types 
linkbyuid = test(fckParams['allow_link_byuid'],1,0)
# resolveUid redirection problems with mediaplayer.swf (temp. removed)
if dicoRequest.get('Type','')=='Media' :
    linkbyuid = 0

# check if upload allowed for Links Image and internal links

allow_file_upload=test(fckParams['allow_server_browsing'],test(fckParams['allow_file_upload'],1,0),0)
allow_image_upload=test(fckParams['allow_server_browsing'],test(fckParams['allow_image_upload'],1,0),0)
allow_flash_upload=test(fckParams['allow_server_browsing'],test(fckParams['allow_flash_upload'],1,0),0)


# check for portal_types when uploading internal links, images and flashs animations

file_portal_type = test(fckParams['file_portal_type'],fckParams['file_portal_type'],'File')
image_portal_type = test(fckParams['image_portal_type'],fckParams['image_portal_type'],'Image')
flash_portal_type = test(fckParams['flash_portal_type'],fckParams['flash_portal_type'],'File')

# check for portal_types when browsing images and flashs
browse_images_portal_types = list(fckParams['browse_images_portal_types'])
browse_flashs_portal_types = fckParams['browse_flashs_portal_types']

# find Plone Site charset 

try:
  prop   = getToolByName(context, "portal_properties")
  charsetSite = prop.site_properties.getProperty("default_charset", "utf-8")
except:
  charsetSite ="utf-8"
  
if charsetSite.lower() in ("utf-8", "utf8"):
    charsetSite ="utf-8"

# 2. utils

def utf8Encode(chaine) :
    # encode in utf8 string
    return encodeString(chaine, charsetSite, "utf-8")

def utf8Decode(chaine) :
    # decode from utf8 (fck forms) to charset
    return encodeString(chaine, "utf-8", charsetSite)


def ConvertToXmlAttribute( value ):
  return utf8Encode(value).replace("\"", "&quot;").replace("'","&rsquo;").replace("&", "&amp;")




# 3. io



def GetUrlFromPath( folderPath ) :

    return '%s%s' %(portal_path,folderPath.rstrip("/"))


def RemoveExtension( fileName ):

   if "." in fileName :
       sprout=fileName.split(".")
       return '.'.join(sprout[:len(sprout)-1])
   return fileName    

def  IsAllowedExt( extension, resourceType ) :
  
   sAllowed = ConfigAllowedExtensions[resourceType]
   sDenied = ConfigDeniedExtensions[resourceType]

   if (sAllowed is None or extension in sAllowed) and (sDenied is None or extension not in sDenied) :
     return 1
   else :
     return 0

def FindExtension (fileName):

   sprout=fileName.split(RemoveExtension(fileName))
   return ''.join(sprout).lstrip('.')

  
def FilterResultsOnType(results, resourceType) :
    """return only some results depending on extension or medias types
       TODO : will be change in future with better integration (a portal_type in fck control panel)"""
    if resourceType=='Media' :
        sAllowed = ConfigAllowedExtensions[resourceType]
        results = [r for r in results if FindExtension(r.getId) in sAllowed]
    return results    
        


# 4. basexml

def CreateXmlHeader( command, resourceType, currentFolder ):
    header = ['<?xml version="1.0" encoding="utf-8" ?>']
    header.append('\r<Connector command="%s" resourceType=" %s ">'% (command,resourceType))
    header.append('\r    <CurrentFolder path="%s" url="%s/" />'\
                   % (ConvertToXmlAttribute(currentFolder),
                      ConvertToXmlAttribute(GetUrlFromPath(currentFolder))))
    return ''.join(header)


def CreateXmlFooter():
    return '\r</Connector>'



def xmlString(results, resourceType, foldersOnly, isPA):

    user=context.REQUEST['AUTHENTICATED_USER']
    # traitement xml
    xmlFiles=['\r        <Files>']
    xmlFolders=['\r        <Folders>']


    # traitement folderish standard non PloneArticle
    if isPA ==0:
        for result in results :
            titre = result.title_or_id()
            if linkbyuid and hasattr(result.aq_explicit, 'UID'):               
               tagLinkbyuid="yes"
               uid = result.UID()
            else :
               tagLinkbyuid="no"
               uid=""
            if result.isPrincipiaFolderish or result.meta_type in pa_meta_types :
                if result.meta_type in pa_meta_types:
                   meta_type_string ='PloneArticle'
                else:
                   meta_type_string = ConvertToXmlAttribute(result.meta_type)
                xmlFolders.append('''
            <Folder name="%s"
                    title="%s"
                    linkbyuid="%s"
                    uid="%s"
                    type="%s"
                    metatype="%s" />'''%(ConvertToXmlAttribute(result.getId()),
                                         ConvertToXmlAttribute(titre),
                                         tagLinkbyuid, uid,
                                         resourceType,
                                         meta_type_string))
            else :
                if result.meta_type in ('CMF ZPhoto', 'CMF Photo'):
                   tagPhoto="yes"
                else:
                   tagPhoto= "no"
                isAttach = "no"
                attachId=""
                xmlFiles.append('''
            <File name="%s"
                  size="%s"
                  title="%s"
                  photo="%s"
                  linkbyuid="%s"
                  uid="%s"
                  type="%s"
                  isPAimg="0"
                  isattach="%s"
                  attachid="%s" />'''%(ConvertToXmlAttribute(result.getId()),
                                       str(context.getObjSize(result)),
                                       ConvertToXmlAttribute(titre),
                                       tagPhoto,
                                       tagLinkbyuid,
                                       uid,
                                       resourceType,
                                       isAttach,
                                       attachId))
    # PloneArticle big bontang treatment
    elif user.has_permission('View', results) :
        # find Plone Article contents for PA v3 or v4
        if hasattr(results.aq_explicit,'getImageBrains'):
              image_brains =results.getImageBrains()  
              attachment_brains=results.getAttachmentBrains()
              versionPA=3
        elif hasattr(results.aq_explicit,'getImages'):
              # return all images (references and attached images - why not)
              images = results.getImages()
              # return all files (references and attachments)
              files=results.getFiles()
              versionPA=4              


        # Plone Article v4 treatment
        if versionPA == 4:
            #  PloneArticle 3.x images and attachements
            # images
            for image in images :
                image_field = image.getField('image')
                image_name = image.getId()
                image_id = image.getId()
                image_title = image.title_or_id()
                image_size = results.getObjSize(image)
                if linkbyuid and hasattr(image.aq_explicit, 'UID'):               
                    tagLinkbyuid="yes"
                    uid = image.UID()
                else:
                    tagLinkbyuid="no"
                    uid=""
                # no more used in next versions
                tagPhoto= "no"
                isAttach = "no"                    
                xmlFiles.append('''
            <File name="%s"
                  size="%s"
                  title="%s"
                  photo="%s"
                  linkbyuid="%s"
                  uid="%s"
                  type="%s"
                  isPAimg="4"
                  isattach="%s"
                  attachid="%s" />'''%(ConvertToXmlAttribute(image_id), 
                                       image_size,
                                       ConvertToXmlAttribute(image_title),
                                       tagPhoto,
                                       tagLinkbyuid,
                                       uid,
                                       resourceType,
                                       isAttach,
                                       ConvertToXmlAttribute(image_name)))

            # files and other resource types
            if resourceType!='Image':
                for file in files :
                    file_name = file.getId()
                    file_id = file.getId()
                    file_title = file.title_or_id()
                    # big syntax mystery
                    file_size = results.getObjSize(file, size=None)
                    if linkbyuid and hasattr(file.aq_explicit, 'UID'):               
                        tagLinkbyuid="yes"
                        uid = file.UID()
                    else:
                        tagLinkbyuid="no"
                        uid=""
                    # no more used in next versions
                    tagPhoto= "no"
                    isAttach = "no"                        
                    xmlFiles.append('''
            <File name="%s"
                  size="%s"
                  title="%s"
                  photo="%s"
                  linkbyuid="%s"
                  uid="%s"
                  type="%s"
                  isPAimg="0"
                  isattach="%s"
                  attachid="%s" />'''%(ConvertToXmlAttribute(file_id),
                                       file_size,
                                       ConvertToXmlAttribute(file_title),
                                       tagPhoto,
                                       tagLinkbyuid,
                                       uid,
                                       resourceType,
                                       isAttach,
                                       ConvertToXmlAttribute(file_name)))

        # Plone Article v3 treatment
        else:
            atool = context.portal_article
            #  PloneArticle 3.x images and attachements
            # images
            for image_brain in image_brains :
                image = image_brain.getObject()
                image_field = image.getField('image')
                image_name = atool.getFieldFilename(image, image_field)
                image_id = image.getId()
                image_title = image.title_or_id()
                image_size = context.plonearticle_format_size(image.get_size())
                tagPhoto= "no"
                isAttach = "no"
                if linkbyuid and hasattr(image.aq_explicit, 'UID'):               
                    tagLinkbyuid="yes"
                    uid = image.UID()
                else:
                    tagLinkbyuid="no"
                    uid=""
                xmlFiles.append('''
            <File name="%s"
                  size="%s"
                  title="%s"
                  photo="%s"
                  linkbyuid="%s"
                  uid="%s"
                  type="%s"
                  isPAimg="3"
                  isattach="%s"
                  attachid="%s" />'''%(ConvertToXmlAttribute(image_id), 
                                       image_size,
                                       ConvertToXmlAttribute(image_title),
                                       tagPhoto,
                                       tagLinkbyuid,
                                       uid,
                                       resourceType,
                                       isAttach,
                                       ConvertToXmlAttribute(image_name)))

            # files and other resource types
            if resourceType!='Image':
                for attach_brain in attachment_brains :
                    attach = attach_brain.getObject()
                    attach_field = attach.getField('file')
                    attach_name = atool.getFieldFilename(attach, attach_field)
                    attach_id = attach.getId()
                    attach_title = attach.title_or_id()
                    attach_size = context.plonearticle_format_size(attach.get_size())
                    tagPhoto= "no"
                    isAttach = "no"
                    if linkbyuid and hasattr(attach.aq_explicit, 'UID'):               
                        tagLinkbyuid="yes"
                        uid = attach.UID()
                    else:
                        tagLinkbyuid="no"
                        uid=""
                    xmlFiles.append('''
            <File name="%s"
                  size="%s"
                  title="%s"
                  photo="%s"
                  linkbyuid="%s"
                  uid="%s"
                  type="%s"
                  isPAimg="0"
                  isattach="%s"
                  attachid="%s" />'''%(ConvertToXmlAttribute(attach_id),
                                       attach_size,
                                       ConvertToXmlAttribute(attach_title),
                                       tagPhoto,
                                       tagLinkbyuid,
                                       uid,
                                       resourceType,
                                       isAttach,
                                       ConvertToXmlAttribute(attach_name)))
                     



    xmlFiles.append('\r        </Files>')
    xmlFolders.append('\r        </Folders>')
    if foldersOnly:
        stringXml=''.join(xmlFolders)
    else :
        stringXml=''.join(xmlFolders)+''.join(xmlFiles)
    return stringXml


def CreateXmlErrorNode (errorNumber,errorDescription):

    return '''
        <Error number="%s"
               originalNumber="%s"
               originalDescription="%s" />'''%(errorNumber,
                                               errorNumber,
                                               ConvertToXmlAttribute(errorDescription))


# 5. commands
# Specific Plone - for others CMS (CPS ...), for special folderish (Plone Article, doc flexible ...) change these lines

def GetFoldersAndFiles( resourceType, currentFolder ):
    results=[]
    user=context.REQUEST['AUTHENTICATED_USER']
    if currentFolder != "/" :
        obj = portal.restrictedTraverse(currentFolder.lstrip('/'))
    else :
        obj = portal
    # obj is standard folderish
    if obj.meta_type not in pa_meta_types:
        if resourceType in ('Image','Flash','Media'):
          if resourceType=="Image" :
            browse_images_portal_types.extend(['Photo', 'ZPhoto'])
            filter={'portal_type':browse_images_portal_types, 'sort_on':'sortable_title'}
          elif resourceType=="Flash" :
            filter={'portal_type':browse_flashs_portal_types, 'sort_on':'sortable_title'}  
          elif resourceType=="Media" :
            #XXX : to improve with good portal_type or interface
            filter={'object_provides':'OFS.interfaces.ISimpleItem', 'sort_on':'sortable_title'}       
          contents = list(obj.getFolderContents(contentFilter={'is_folderish':True, 'sort_on':'sortable_title'}))
          if len(pa_meta_types):
              contents.extend(list(obj.getFolderContents(contentFilter={'meta_type':pa_meta_types, 'sort_on':'sortable_title'})))
          nonFolderishContents = list(obj.getFolderContents(contentFilter=filter))   
          # temp usage for medias until we get a better integration 
          nonFolderishContents = FilterResultsOnType (nonFolderishContents, resourceType)
          contents.extend(nonFolderishContents)
        else :
          # getFolderContents return nothing with no contentFilter
          contents = obj.getFolderContents(contentFilter={'portal_type':'', 'sort_on':'sortable_title'})
        for brain in contents :
          object=brain.getObject()
          review_state=container.portal_workflow.getInfoFor(object, 'review_state', '')
          if review_state!='' and (review_state not in unpublishedStates) :
            results.append(object)
          elif user.has_role(rolesSeeUnpublishedContent,object) :
            results.append(object)
        return xmlString(results,resourceType,0,0)

    # Plone article find attachements and images
    else:
        # specific request
        return xmlString(obj,resourceType,0,1)



def GetFolders( resourceType, currentFolder ):
    results=[]
    user=context.REQUEST['AUTHENTICATED_USER']
    types=context.portal_types
    all_portal_types = [ctype.content_meta_type for ctype in types.objectValues()]
    if currentFolder != "/" :
        obj = portal.restrictedTraverse(currentFolder.lstrip('/'))
    else :
        obj = portal 
    folders = list(obj.getFolderContents(contentFilter={'is_folderish':True, 'sort_on':'sortable_title'}))
    if len(pa_meta_types):
        pa_folders= list(obj.getFolderContents(contentFilter={'meta_type':pa_meta_types, 'sort_on':'sortable_title'})) 
        folders.extend(pa_folders)
    for brain in folders :
      object = brain.getObject()
      review_state=container.portal_workflow.getInfoFor(object, 'review_state', '')
      if review_state and (review_state not in unpublishedStates) :
        results.append(object)
      elif user.has_role(rolesSeeUnpublishedContent,object) :
        results.append(object)
    return xmlString(results,resourceType,1,0)


def CreateFolder(currentFolder, folderName ):

    user=context.REQUEST['AUTHENTICATED_USER']
    if currentFolder != "/" :
        obj = portal.restrictedTraverse(currentFolder.lstrip('/'))
    else :
        obj = portal
    sErrorNumber=""

    # error cases
    if not user.has_permission('Add portal content', obj) and not user.has_permission('Modify portal content', obj):
       sErrorNumber = "103"
       sErrorDescription = "folder creation forbidden"

    if obj.meta_type in pa_meta_types :
       sErrorNumber = "103"
       sErrorDescription = "folder creation forbidden"

    if not folderName:
       sErrorNumber = "102"
       sErrorDescription = "invalid folder name"

    if not sErrorNumber :
      try :
        folderTitle=utf8Decode(folderName)
        folderName = fckCreateValidZopeId(utf8Encode(folderTitle))
        new_id = obj.invokeFactory(id=folderName, type_name=folder_portal_type, title=folderTitle)
        sErrorNumber = "0"
        sErrorDescription = "success"
      except :
        sErrorNumber = "103"
        sErrorDescription = "folder creation forbidden"

    return CreateXmlErrorNode(sErrorNumber,sErrorDescription)
       



# 6. upload

def UploadFile(resourceType, currentFolder, data, title) :

        user=context.REQUEST['AUTHENTICATED_USER']
        if currentFolder != "/" :
            obj = portal.restrictedTraverse(currentFolder.lstrip('/'))
        else :
            obj = portal
        error=""
        idObj=""
        
        if obj.meta_type not in pa_meta_types:
            # define Portal Type to add

            if resourceType == 'File':
              if obj.meta_type in rd_portal_types :
                typeToAdd = 'FileAttachment'
              else:
                typeToAdd = file_portal_type
            elif resourceType == 'Flash':
                typeToAdd = flash_portal_type
            elif resourceType == 'Image' :
                if obj.meta_type=="CMF ZPhotoSlides":
                    typeToAdd = 'ZPhoto'
                elif obj.meta_type=="Photo Album":
                    typeToAdd = 'Photo'
                elif obj.meta_type=="ATPhotoAlbum":
                    typeToAdd = 'ATPhoto'
                elif obj.meta_type in rd_portal_types :
                    typeToAdd = 'ImageAttachment'
                else:
                    typeToAdd = image_portal_type
        

            if not user.has_permission('Add portal content', obj) and not user.has_permission('Modify portal content', obj):
               error = "103"

            if resourceType == 'Image' and not allow_image_upload:
               error = "103"

            if resourceType == 'Flash' and not allow_flash_upload:
               error = "103"

            if resourceType not in ('Flash','Image') and not allow_file_upload:
               error = "103"

            if not data:
              #pas de fichier 
              error= "202"


            titre_data=''
            filename=utf8Decode(getattr(data,'filename', ''))
            titre_data=filename[max(string.rfind(filename, '/'),
                            string.rfind(filename, '\\'),
                            string.rfind(filename, ':'),
                            )+1:]                  

            idObj=fckCreateValidZopeId(utf8Encode(titre_data))

            if title :
               titre_data=title
            

            if not IsAllowedExt( FindExtension(idObj), resourceType ):
                  error= "202"

            if not error :              
                error="0"
                indice=0
                exemple_titre=idObj
                while exemple_titre in obj.objectIds():
                  indice=indice+1
                  exemple_titre=str(indice) + idObj
                if indice!=0:
                    error= "201"
                    idObj = exemple_titre

                try:
                    obj.invokeFactory(id=idObj, type_name=typeToAdd, title=titre_data )
                    newFile = getattr(obj, idObj)
                    newFile.edit(file=data)

                except:
                    error = "103"

        #Plone Article treatment
        else :
            if hasattr(obj.aq_explicit,'getImageBrains'):
                versionPA=3
            elif hasattr(obj.aq_explicit,'getImages') :
                versionPA=4
            else:
                error="103"

            if not data:
                #pas de fichier 
                error= "1"        
                customMsg="no file uploaded"
            if not error :
                filename=utf8Decode(getattr(data,'filename', ''))
                titre_data=filename[max(string.rfind(filename, '/'),
                                string.rfind(filename, '\\'),
                                string.rfind(filename, ':'),
                                )+1:]                  

                idObj=fckCreateValidZopeId(utf8Encode(titre_data))
                if title :
                    titre_data=title
                
                if resourceType == 'Image' :
                    # Upload file
                    if not user.has_permission('Modify portal content', obj):
                        error = "103"
                    elif not allow_image_upload:
                        error = "103"
                    elif not IsAllowedExt( FindExtension(idObj), resourceType ):
                        error= "202"        
                        customMsg="Invalid file type"
                    else :
                        if versionPA==3 :
                          if  obj.portal_article.checkImageSize(data):
                             obj.addImage(title=titre_data, description='', image=data)
                             error="0"
                          else:
                             error="104"    
                        
                        else :
                           # PA bontang treatment
                           # get size and check against max allowed size
                           data.seek(0, 2)
                           size = data.tell()
                           data.seek(0)
                           max_size = obj.getTypeInfo().getProperty('imageMaxSize', None)
                           if max_size is not None and size > max_size :
                             error='104'
                           else :
                             images = obj.getImages() 
                             imgIds =[img.getId() for img in images]
                             unikId = idObj
                             i=0
                             while unikId in imgIds :
                                i = i+1
                                unikId = str(i) + idObj
                             new_value = { 
                                          "attachedImage": (data, {}),
                                          "title": (titre_data, {}),
                                          "description": ('', {}),
                                          "id": (unikId, {}),
                                         }
                             if images:            
                               images.append(new_value)  
                             else:
                               images=[new_value]            
                             obj.setImages (images)
                             error='0'
                else:
                    # Upload file
                    if not user.has_permission('Modify portal content', obj):
                        error = "103"
                    elif not allow_file_upload:
                        error = "103"
                    elif not IsAllowedExt( FindExtension(idObj), resourceType ):
                        error= "202"        
                        customMsg="Invalid file type"
                    else :
                        if versionPA==3 :
                          if  obj.portal_article.checkAttachmentSize(data):
                             obj.addAttachment(title=titre_data, description='', file=data)
                             error="0"
                          else:
                             error="104"    
                        
                        else :
                           # PA bontang treatment
                           # get size and check against max allowed size
                           data.seek(0, 2)
                           size = data.tell()
                           data.seek(0)
                           max_size = obj.getTypeInfo().getProperty('attachmentMaxSize', None)
                           if max_size is not None and size > max_size :
                             error='104'
                           else :
                             files = obj.getFiles() 
                             fileIds =[f.getId() for f in files]
                             unikId = idObj
                             i=0
                             while unikId in fileIds :
                                i = i+1
                                unikId = str(i) + idObj
                             new_value = { 
                                          "attachedFile": (data, {}),
                                          "title": (titre_data, {}),
                                          "description": ('', {}),
                                          "id": (unikId, {}),
                                         }
                             if files:
                                files.append(new_value)
                             else:
                                files=[new_value]   
                             obj.setFiles (files)
                             error= '0'


        d= '''
        <script type="text/javascript">
        window.parent.frames['frmUpload'].OnUploadCompleted(%s,"%s") ;
        </script>
        '''% (error,idObj)
        return d


#7. connector 


if ConfigUserFilesPath != "" :
   sUserFilesPath = ConfigUserFilesPath
elif dicoRequest.has_key('ServerPath'):
   sUserFilesPath = dicoRequest ['ServerPath']
else :
   sUserFilesPath = "/"


if dicoRequest.has_key('CurrentFolder'):
   sCurrentFolder = dicoRequest ['CurrentFolder']
   if sUserFilesPath!='/' and sUserFilesPath.rstrip('/') not in sCurrentFolder:
        sCurrentFolder = sUserFilesPath
else :
   message_error="No CurrentFolder in request"



if dicoRequest.has_key('Command'):
    sCommand = dicoRequest ['Command']
else :
    message_error="No Command in request"

if dicoRequest.has_key('Type'):
    sResourceType = dicoRequest ['Type']
else :
    message_error="No Type in request"


if dicoRequest.has_key('NewFolderName'):
    sFolderName = dicoRequest ['NewFolderName']


# interception File Upload
if sCommand=='FileUpload' and dicoRequest.has_key('NewFile'):
    sData = dicoRequest ['NewFile']
    sTitle = utf8Decode(dicoRequest ['Title'])
    chaineHtmlUpload = UploadFile(sResourceType, sCurrentFolder, sData, sTitle)
    RESPONSE.setHeader('Content-type', 'text/html; charset=%s' % charsetSite)
    return chaineHtmlUpload

else :

    # Creation response XML
    if not message_error :

        RESPONSE.setHeader('Cache-control','pre-check=0,post-check=0,must-revalidate,s-maxage=0,max-age=0,no-cache')
        RESPONSE.setHeader('Content-type', 'text/xml; charset=utf-8')
        xmlHeader = CreateXmlHeader (sCommand, sResourceType, sCurrentFolder)

        if sCommand=="GetFolders":
            xmlBody = GetFolders (sResourceType, sCurrentFolder)
        elif sCommand=="GetFoldersAndFiles":
            xmlBody = GetFoldersAndFiles (sResourceType, sCurrentFolder)
        elif sCommand=="CreateFolder":
            xmlBody = CreateFolder (sCurrentFolder,sFolderName)

        xmlFooter = CreateXmlFooter()
        return xmlHeader + xmlBody + xmlFooter

    # creation response error request
    else :
        sErrorNumber="218"
        sErrorDescription="Browser Request exception : " + message_error
        xmlHeader = CreateXmlHeader (sCommand, sResourceType, sCurrentFolder)
        xmlFooter = CreateXmlFooter()
        return xmlHeader + CreateXmlErrorNode(sErrorNumber,sErrorDescription) + xmlFooter
