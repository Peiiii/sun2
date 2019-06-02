import piudb,uuid,time,config,asyncio,markdown,bs4,os,jinja2
from utils.btools import writeJsonFile,loadJsonFile,writeTextFile,loadTextFile
from  jinja2 import  Template,Environment, PackageLoader
import utils.btools as btools


from piudb import (
    Model,StringField,TableManager,TextField,ObjectField,
    BooleanField,IntegerField,Field,FloatField,Piu,InfoBody,
    Piu
)
def flag():
    print('*'*20,'FLAG HERE','*'*20)
class Collection(list):
    def sortBy(self,key,reverse=True):
        li=sorted(self,key=lambda x: x[key] ,reverse=reverse)
        return li
def openAll():
    from config import db
    helper=Helper()
    helper.blog_tb=Piu(db.path.blogs, Blog, auto_update_fields=True, overwrite_fields=True)
    helper.cate_tb=Piu(db.path.categories, Category, auto_update_fields=True, overwrite_fields=True)
    helper.tag_tb=Piu(db.path.tags, Cluster, auto_update_fields=True, overwrite_fields=True)
    helper.archieve_tb=Piu(db.path.archieves, Cluster, auto_update_fields=True, overwrite_fields=True)
    helper.env=Environment(loader=PackageLoader(config.other_config.templates_dir,''))
    helper.json_articles_dir=config.json_articles_dir
    helper.html_articles_dir=config.articles_dir
    helper.article_template=config.page_templates.article
    return helper
class Helper(InfoBody):
    def __init__(self,blog_tb=None,visible_only=True,**kwargs):
        if blog_tb:
            self.blog_tb=blog_tb
            self.tb=blog_tb
            assert isinstance(blog_tb,Piu)
        super().__init__(**kwargs)
        self.visible_only=visible_only
    def open(self,name,**kws):
        self[name]=Piu(**kws)
    def reBuild(self):
        self._reloadBlogTable()
        self.rectifyArchieves()
        self.rectifyTags()
        self.rectifyCategories()
        self.convertBlogsToJsonFiles()
        self.saveAllBlogsToHtmlFile()

    def _reloadBlogTable(self):
        blogs = self.blog_tb._findAll_()
        num = self.blog_tb._deleteAll_()
        print('num: %s' % num)
        for b in blogs:
            print('Blog deleted: %s' % b.title)
            self.blog_tb._insert_(b)
    async def upsertBlogSafe(self,blog):
        blog.checkDefault()
        blog_ret=self.blog_tb._upsert_(blog)
        archieve=blog_ret['archieve']
        tags=blog_ret['tags']
        tags=list(set(tags))
        category=blog_ret['category']
        self.archieve_tb._upsert_(Cluster(name=archieve))
        for tag in tags:
            if not tag or tag=='':
                continue
            self.tag_tb._upsert_(Cluster(name=tag))
        self.cate_tb._upsert_(Cluster(name=category))
        blog.checkDefault()
        self.saveBlogToJsonFile(blog)
        self.saveBlogToHtmlFile(blog)
    def getArticleHtml(self,blog):
        template=self.article_template
        tem = self.env.get_template(template)
        tem = tem.render(blog=blog)
        return tem
    def saveBlogToHtmlFile(self,b):
        fpath=self.html_articles_dir+'/'+b.id+'.html'
        html=self.getArticleHtml(b)
        writeTextFile(fpath,html)
    def saveAllBlogsToHtmlFile(self):
        for b in self.blog_tb._findAll_():
            self.saveBlogToHtmlFile(b)
    def saveBlogToJsonFile(self,b):
        fpath = self.json_articles_dir + '/' + b.id + '.json'
        writeJsonFile(b.toJson(), fpath)
        print('save %s  as %s' % (b.title, fpath))
    def convertBlogsToJsonFiles(self):
        dpath=self.json_articles_dir
        blogs = self.blog_tb._findAll_()
        if not os.path.exists(dpath):
            os.makedirs(dpath)
        for b in blogs:
            fpath = dpath + '/' + b.id + '.json'
            writeJsonFile(b.toJson(), fpath)
            print('save %s  as %s' % (b.title, fpath))
    async def getArchieves(self):
        archs=self.archieve_tb._findAll_()
        archs2=[]
        for a in archs:
            archs2.append(self.getCluster(cluster_name=a.name,visible_only=self.visible_only,archieve=a.name))
        return archs2

    def getCategoryNames(self):
        return self.getAllFieldValues('category')
    def getAllFieldValues(self,key,list_item=False):
        tb = self.blog_tb
        ibs = tb._select_([key])
        values = [ib[key] for ib in ibs]
        if not list_item and  not isinstance(values[0],list):
            values=list(set(values))
            print(values)
            return values
        vs=[]
        for v in values:
            vs+=v
        return vs
    def quikInsert(self,blog):
        self.blog_tb._insert_(blog)
    def getCluster(self,cluster_name,checker=None,visible_only=True,**kws):
        if checker and callable(checker):
            kws['__checker__']=checker
        if visible_only:
            kws['visible']='true'
            print(kws)
        blogs=self.blog_tb._findAll_(**kws)
        for b in blogs:
            print('test:visible:',b.visible)
        length=len(blogs)
        return Cluster(name=cluster_name,blogs=blogs,length=length)

    async def getTags(self):
        assert isinstance(self.tag_tb,Piu)
        tags=self.tag_tb._findAll_()
        new_tags=[]
        for t in tags:
            def checker(record):
                if t.name in record['tags']:
                    return True
                else:
                    return False
            tag=self.getCluster(cluster_name=t.name,visible_only=self.visible_only,checker=checker)
            if not tag.length:
                continue
            new_tags.append(tag)
        return new_tags

    async def getCategories(self):
        cs = self.cate_tb._findAll_()
        print('get_cates:',cs)
        cates = []
        for c in cs:
            cate = self.getCluster(cluster_name=c.name,visible_only=self.visible_only, category=c.name)
            if not cate.length:
                continue
            cates.append(cate)
        return cates
    def fixAll(self):
        self.rectifyCategories()
        self.rectifyTags()
        self.rectifyArchieves()
    def rectifyCategories(self):
        cates=self.getCategoryNames()
        print('get cate names:',cates)
        for name in cates:
            self.cate_tb._upsert_(Category(name=name))
            # self.tb.raiseError()

    def rectifyTags(self):
        tags_lists = self.getAllFieldValues('tags', list_item=True)
        tag_names = []
        for tags in tags_lists:
            print('tags:', tags)
            tag_names.append(tags)
        tag_names = list(set(tag_names))
        for name in tag_names:
            if not name or name=='':
                continue
            self.tag_tb._upsert_(Cluster(name=name))
            # self.tb.raiseError()
    def rectifyArchieves(self):
        archs = self.getAllFieldValues('archieve')
        print('rtf archieves:',archs)
        for a in archs:
            arch=Cluster(name=a)
            self.archieve_tb._upsert_(arch)

class Category(Model):
    name=StringField(primary_key=True)
    length=IntegerField()
    blogs=ObjectField(default=[])

    def getLength(self):
        self.length=len(self.blogs)

class Cluster(Model):
    name=StringField(primary_key=True)
    length=IntegerField()
    blogs=ObjectField(default=[])

    def __init__(self,**kws):
        super().__init__(**kws)
    def getLength(self):
        self.length=len(self.blogs)




def next_id():
    t=time.gmtime()
    id=str(t.tm_year)+str(t.tm_mon)+str(t.tm_mday)+(uuid.uuid4().hex)
    return id
def get_year():
    return time.gmtime().tm_year
def get_month():
    return time.gmtime().tm_mon
def get_mday():
    return time.gmtime().tm_mday
class Blog(Model):

    id=StringField(primary_key=True,default=next_id)
    title=StringField()
    text=TextField(searchable=False)
    html=TextField(searchable=False)
    md=TextField(searchable=False)

    format_used=StringField(default='plain-text')
    content=TextField(searchable=False)
    digest=TextField()
    category=StringField()
    tags=ObjectField(default=[])
    archieve=StringField()
    author=StringField(default='WP')
    created_at=FloatField(default=time.time)
    location=StringField(default='')


    date=StringField()
    keywords=StringField()
    url=StringField()
    mood=StringField()
    status=StringField()
    visible=StringField(default='true')
    description=StringField()
    length=IntegerField()
    num_words=IntegerField()
    public=BooleanField(default=True)

    rank=IntegerField(default=0)
    views=IntegerField(default=0)
    stars=IntegerField(default=0)
    year=IntegerField(default=get_year)
    month=IntegerField(default=get_month)
    day=IntegerField(default=get_mday)
    fields=ObjectField()
    info=ObjectField()
    default_template=StringField(config.page_templates.article)

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def checkDefault(self):
        self.checkAllFieldsByDefault()
        self.addID()
        self.addArchieve()
        self.addDigest()
        self.addDate()
        self.addHtml()
        self.addKeywords()
        self.addDescription()
    def addHtml(self):
        if not self.html or self.html=='':
            if self.format_used=='plain-text':
                self.html=btools.textToHTML(self.text)
            elif self.format_used=='markdown':
                self.html=btools.mdToHTML(self.md)
            elif self.format_used=='html':
                self.html=self.text

    def addDate(self):
        if not self.date or self.date=='':
            t=self.created_at
            self.date=self.convertDate(t)
    def addArchieve(self):
        if self.archieve=='':
            t=time.localtime(self.created_at)
            self.archieve=str(self.year)+'年'+str(self.month)+'月'
    def addID(self):
        t = time.gmtime()
        id = str(t.tm_year) + str(t.tm_mon) + str(t.tm_mday)+self.title
        self['id'] =id
    def addDigest(self):
        if not self.digest or self.digest == '':
            text=bs4.BeautifulSoup(self.html).text
            digest=text[:500] if len(text)>=500 else text
            self.digest=digest
    def addKeywords(self):
        if self.isEmpty(self.keywords):
            keywords=self.digest.split()
            if len(keywords)>=5:
                self.keywords=';'.join(keywords[:5])
            self.keywords=';'.join(keywords)
    def addDescription(self):
        if self.isEmpty(self.description):
            self.description=self.digest[:200] if len(self.digest)>=200 else self.digest
    def isEmpty(self,s):
        if not s or s.strip()=='':
                return True
        return False
    def convertDate(self,t):
        t=time.strftime('%Y-%m-%d',time.localtime(t))
        return t
    def toJson(self):
        dic=self.__fields__
        json={}
        for k in dic:
            json[k]=self.__getattr__(k)
        return json
    def shortCut(self):
        return piudb.InfoBody(
            title=self.title,id=self.id,archieve=self.archieve,author=self.author,description=self.description
        )
