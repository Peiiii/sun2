import config,tools,time,os,models
from  jinja2 import  Template,Environment, PackageLoader
from models import Blog
import piudb
from piudb import Piu


templates_dir=config.other_config.templates_dir
env = Environment(loader=PackageLoader(templates_dir,''))
pre_make_dirs=config.pre_make_dirs
test_blog_dir='data/db/test_table'

helper=models.openAll()

def convertBlogs():
    # tb=Piu(config.db_dir_blogs,Blog)
    tb=helper.tb
    tools.allBlogsToHTML(tb=tb,env=env,path=config.articles_dir,template=config.page_templates.article,force=True)
    tools.saveBlogsToJsonFiles(tb=tb,dpath=config.json_articles_dir)
def getBlogsFromJsonFiles():
    blogs=tools.loadBlogsFromJsonFiles(config.json_articles_dir)
    [print(b['title']) for b in blogs.values()]
    return blogs
def rebuidFromTextFiles():
    # tools.forceRemoveDir(config.db_dir_blogs)
    # tb=Piu(config.db_dir_blogs,Blog)
    tools.loadBlogsFromTextFiles(helper.blog_tb,force=True)
    tools.allBlogsToHTML(tb=helper.blog_tb, env=env, path=config.articles_dir, template=config.page_templates.article, force=True)
    tools.saveBlogsToJsonFiles(tb=helper.blog_tb, dpath=config.json_articles_dir)
    # b=tb._findAll_()
    # print(b)
    # showAllBlogs(helper.blog_tb)
def reBuildFromDB():
    helper.reBuild()
def showAllBlogs(tb=None):
    if not tb:
        tb=Piu(test_blog_dir,Blog)
    blogs=tb._findAll_()
    print(blogs)
def make_dirs():
    for d in pre_make_dirs:
        if not os.path.exists(d):
            os.makedirs(d)

if __name__=="__main__":
    make_dirs()

    # rebuild()
    # getBlogsFromJsonFiles()
    # rebuidFromTextFiles()
    # showAllBlogs()
    # helper.getCategoryNames()
    reBuildFromDB()
    pass