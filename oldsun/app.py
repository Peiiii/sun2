import logging;logging.basicConfig(level=logging.INFO)
import asyncio,uuid,tools,config,models,utils.qpath as qpath
from framework import Application,jsonResponse,apiError,pageResponse
from config import net,paths,dirs,pages,other_config
from models import Blog,Comment,User,getDB,InfoBody
from tools import log
from aiohttp import web
from  jinja2 import  Template,Environment, PackageLoader
from utils.qpath import MyOS,Qpath


##---------------------Initialization-------------------------------
TEST_MODE=True
templates_dir=config.other_config.templates_dir
env = Environment(loader=PackageLoader(templates_dir,''))

loop=asyncio.get_event_loop()
app=Application(loop=loop)

mydb=getDB()
urtb=mydb.urtb;cotb=mydb.cotb;bltb=mydb.bltb;myho=mydb.myho;
mos=MyOS()

base_link='http://127.0.0.1:'+str(net.port)
quik_links=['/','/manage','/wp']
##----------------------------End Initialization------------------------------------
##--------------------Permanent links-----------------------
for k,v in config.permanent_links.items():
    @app.get3(k)
    async def handler():
        blogs=await bltb.findAll(visible='true')
        blogs=blogs.sortBy('created_at')
        return pageResponse(template=v,config=config,blogs=blogs)

##--------------------End Permanent links-----------------------

##---------------------Make handlers------------------
@app.get2(paths.root,timer=True)
async def do_root():
    # await blman.rebuild()
    blogs=await bltb.findAll(visible='true')
    blogs=blogs.sortBy('created_at')
    return pageResponse(template=config.page_templates.root,blogs=blogs,config=config.site)
@app.get2('/wp')
async def do_wp():
    headers={'location':'http://oneday.red:8000'}
    return web.Response(status=308,headers=headers)
@app.post5('/proxy/get',wrap=False)
async def do_proxy_get(json):
    import requests
    url=json['url']
    re=requests.get(url).text
    return web.Response(body=re.encode('utf-8'),content_type='text/html')
@app.get2(paths.about,timer=True)
async def do_about():
    return pageResponse(template=pages.about,config=config.site)
@app.get2(paths.tags)
async def do_tags():
    tags=await mydb.getTags()
    return pageResponse(template=pages.tags,cluster=tags,config=config.site)
@app.get2(paths.categories)
async def do_categories():
    cates=await mydb.getCategories()
    return pageResponse(template=pages.categories,cluster=cates,config=config.site)
@app.get2(paths.archieves)
async def do_archieves():
    archieves=await mydb.getArchieves()
    return pageResponse(template=pages.archieves,cluster=archieves,config=config.site)
@app.get2(paths.search)
async def do_search():
    return pageResponse(template=pages.search,config=config.site)
@app.get2(paths.manage)
async def do_manage_get():
    blogs=await bltb.findAll()
    return pageResponse(template=pages.manage,blogs=blogs,config=config.site)
##----------------------Manage Pages---------------------##
## editor
import  time
@app.get2(paths.editor)
async def do_editor_get():
    return pageResponse(template=pages.editor,config=config.site)
@app.post5(paths.editor)
async def do_editor_post(
        opr_type,title,text,md,html,description,author,info,category,tags,id,
        digest,keywords,fields,format_used,mood,status,visible
):
    # 数据检查和处理
    created_at=time.time()
    b=Blog(
        title=title,text=text,md=md,format_used=format_used,html=html,
        created_at=created_at,category=category,tags=tags,id=id,author=author,
        description=description,info=info,digest=digest,keywords=keywords,fields=fields,
        mood=mood,status=status,visible=visible
    )
    await bltb.upsert(b)
    return jsonResponse(success=True,message='上传成功！')

## alter
@app.post5('/manage/alter')
async def do_manage_alter(json,opr_type):
    id=json['id']
    if opr_type=='delete':
        s=bltb._delete_(id)
        if s:
            return jsonResponse(message='删除成功')
        return apiError(message='删除失败')
    if opr_type=='add_category':
        cate=Category(name=json['name'])
        s = await man.cate_tb.insert(cate)
        if s:
            return jsonResponse(message='操作成功')
        return apiError(message='操作失败')
@app.post5('/manage/get_blog')
async def do_get_blog(blog_id):
    blog=await bltb.findByPK(blog_id)
    if blog:
        return jsonResponse(data=blog.toJson())
    return apiError(message='blog not found.')
@app.post5('/manage/fs',timer=True)
async def do_fs(json,optype,file_data):
    if optype=='upload':
        json['path']='./static/upload'
        json['file_data']=file_data
        json['optype']='upload'
    # print(file_data)
    resp=mos.do(json)
    return web.json_response(data=resp)
##------------------Make Handlers Details----------------##

@app.get2('/quit')
async def do_quit():
	exit();
##---------------------End Make Handlers---------------------------##
app.router.add_static('/', 'static', show_index=other_config.show_index)
async def init(loop):
    server = await loop.create_server(app.make_handler(), net.ip, net.port)
    return server
loop.run_until_complete(init(loop))
for i in quik_links:
    print(base_link+i)
loop.run_forever()