import os, time,hashlib,markdown,re,json,shutil
import asyncio
import  utils.spider as spider
from orm import InfoBody
from models import getDB,Blog
import config
from  jinja2 import  Template,Environment, PackageLoader


















def initTools():
    pass
# templates_dir=config.other_config.templates_dir
# env = Environment(loader=PackageLoader(templates_dir,''))

def templateToHTML(template,env,fpath,**kws):
    tem=env.get_template(template)
    tem=tem.render(**kws)
    writeFile(fpath,tem)

def blogToHTML(blog,template,env,fpath):
    templateToHTML(template=template,env=env,fpath=fpath,blog=blog)

def allBlogsToHTML(tb,path,env,template=None,force=False):
    blogs=tb._findAll_()
    if not os.path.exists(path):
        os.makedirs(path)
    for  b in blogs:
        fpath=path+'/'+b.id+'.html'
        if template:
            blogToHTML(blog=b,template=template,fpath=fpath,env=env)
        else:
            blogToHTML(blog=b,template=b.default_template,fpath=fpath,env=env)
##------------------------------------------------------------------------------------##
def writeJsonFile(obj,fpath):
    with open(fpath,'w') as f:
        json.dump(obj,f)
def loadJsonFile(fpath):
    with open(fpath,'r') as f:
        obj=json.load(f)
    return obj
def saveBlogsToJsonFiles(tb,dpath):
    blogs=tb._findAll_()
    if not os.path.exists(dpath):
        os.makedirs(dpath)
    for b in blogs:
        fpath=dpath+'/'+b.id+'.json'
        writeJsonFile(b.toJson(),fpath)
        log('save %s  as %s'%(b.title,fpath))
def loadBlogsFromJsonFiles(dpath):
    fns=os.listdir(dpath)
    ids=[fn.split('.')[0] for fn in fns]
    fpaths=[dpath+'/'+fn for fn in fns]
    dic={}
    for i in range(len(fpaths)):
        obj=loadJsonFile(fpaths[i])
        dic[ids[i]]=obj
        log('load %s from %s'%(obj['title'],fns[i]))
    return dic


##----------------End Specific Tools----------##
def log(*args, num=20, str='*'):
    print(str * num, end='')
    print(*args, end='')
    print(str * num)
def getLineNum(text):
    return text.find('\n')
def getLine(text,n):
    num=getLineNum(text)
    if n>=num:
        return False
    else:
        return text.split('\n')[n]
def writeFile(fn, s, encoding='utf-8'):
    f = open(fn, 'wb')
    a = f.write(bytes(s, encoding=encoding))
    f.close()
    return a


def loadText(file):
    import chardet
    f = open(file, 'rb')
    text = f.read()
    f.close()
    encoding = chardet.detect(text)['encoding']
    if text:
        text = text.decode(encoding=encoding)
    else:
        text = ''
    return text
def forceRemoveDir(fpath):
    shutil.rmtree(fpath)

def formatTime( t):
    t = time.localtime(t)
    return time.strftime('%Y/%m/%d  %H:%M:%S', t)

def encrypt(*args):
    text=':'.join(args)
    encrypted=hashlib.sha1(text.encode('utf-8')).hexdigest()
    return encrypted
def textToHTML(text):
    text,dic=renderDocument(text)
    format=dic.get('format',None)
    format=format or 'text/plain'

    if format=='text/plain' :
        text=text.split('\n')
        new_text = []
        for i in text:
            new_text.append('<p>' + i + '</p>')
        return '\n'.join(new_text)
    elif format=='md' or format=='markdown':
        return mdToHTML(text)
def textToDic(text,divider=';',equal_char='='):
    text=text.strip().strip(divider)
    fields=text.split(divider)
    dic={}
    for f in fields:
        [name,value]=f.strip().split(equal_char)
        name=name.strip()
        value=value.strip()
        dic[name]=value
    return dic
def getHeadAndBody(text):
    text=text.strip()
    pat=re.compile('^/\*.*\*/',re.DOTALL)
    m=re.match(pat,text)
    if not m:
        return None,text
    body=re.sub(pat,'',text,count=1).strip()
    head=m.group(0).strip('/*').strip('*/')
    return head,body

from markdown import markdown
def mdToHTML(md):
    md=markdown(md)
    return md
def renderDocument(text):
    head,body=getHeadAndBody(text)
    if not head:
        return body,{}
    dic=textToDic(head)
    return body,dic


##---------------------------------------##

##-------------------Specific Tools------------##
def loadTestBlogs():
    files=os.listdir(config.text_articles_dir)
    articles=[]
    for f in files:
        art=loadBlogFromTextFile(config.text_articles_dir+os.sep+f)
        articles.append(art)
    return articles
def loadBlogFromTextFile(f):
    with open(f,'r',encoding='utf-8') as f:
        content=f.read()
        f.close()
    items=content.split('<$$$$$>')
    [title,intro,info,content]=items
    blog=InfoBody(title=title,intro=intro,info=info,content=content)
    # print(blog)
    return blog
async def addTestBlogs(tb,force=False):
    articles=loadTestBlogs()
    for a in articles:
        if not force and tb._exists(title=a.title):
            print('blog exists: %s'%a.title)
            continue
        blog=Blog(title=a.title,description=a.intro,info=a.info,text=a.content,
                  category='Demo',html=textToHTML(a.content),created_at=time.time(),
                  tags=['demo']
                  )
        # print('Blog __dict__:',Blog.__dict__)
        await tb.insert(blog)
        blog=await tb.find(title=blog.title)
        print(blog.__class__)
        log('insert blog %s and id=%s'%(blog['title'],blog.id))
        # await blman.saveBlog(blog,identified_by_title=True)
def loadBlogsFromTextFiles(tb,force=False):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(addTestBlogs(tb,force))
    loop.close()
if __name__=="__main__":
    # spider.makeArticles()
    # initTest()
    pass

##----------------------------------------------------------------------------##
##----------------------------------------------------------------------------##

#####专用小工具
def parsePapers(text):
    lines=text.split('\n')
    lines=[l.strip() for l in lines]
    new_lines=[]
    for i in lines:
        if i == '' or i == '\n' or i[0]=='#':
            continue
        else:
            new_lines.append(i)
    lines=new_lines
    lines=[l.title() for l in lines]
    lines.sort()
    print('records: %s'%len(lines))
    return lines
def getPaperList(pfile):
    text=loadText(pfile)
    lines=parsePapers(text)
    return lines


