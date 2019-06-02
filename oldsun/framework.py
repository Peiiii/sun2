import functools,inspect,chardet,time,os
import aiohttp,asyncio,jinja2,config
import logging;logging.basicConfig(level=logging.INFO)
from aiohttp import web
from  jinja2 import  Template,Environment, PackageLoader

templates_dir=config.other_config.templates_dir
env = Environment(loader=PackageLoader(templates_dir,''))


def jsonResponse(data=False,success=True,message=False,redirect=False):
    return web.json_response(data={
        'data': data,
        'success': success,
        'message': message,
        'redirect': redirect
    })
def apiError(message='Error',redirect=False,data=False,success=False):
    if data or success:
        raise Exception
    return jsonResponse(
        data=data,
        success=success,
        message=message,
        redirect=redirect
    )

def pageResponse(template,**kws):
    tem=env.get_template(template)
    page=tem.render(**kws)
    return web.Response(body=page,content_type='text/html')
def pageError(template=config.pages.error,**kws):
    return pageResponse(template=template,**kws)
class Application(web.Application):

    def get2(self,path,wrap=False,cookies=False,headers=False,request=False,timer=False):  ## 与get1不同，get2的没有对返回值的包装，因此原函数需自己返回一个web.Responce对象
        def decorator(func):
            args=inspect.getargspec(func).args
            @functools.wraps(func)
            async def wrapper(req):
                if timer:
                    start=time.time()
                logging.info('run %s' % func.__name__)
                args2=args.copy()
                if request:
                    r=args2.pop(-1)
                    if r!='request':
                        raise Exception('参数最后一个应为request')
                elif cookies:
                    co=args2.pop(-1)
                    if co!='cookies':
                        raise Exception('参数最后一个应为cookies')
                elif headers:
                    h=args2.pop(-1)
                    if h!='headers':
                        raise Exception('参数最后一个应为headers')
                params=[]
                for i in args2:
                    try:
                        params.append(req.match_info[i])
                    except:
                        raise Exception('函数%s参数%s定义不匹配' % (func.__name__,i))
                if request:
                    params.append(req)
                elif headers:
                    params.append(req.headers)
                elif cookies:
                    params.append(req.cookies)
                response =await func(*params)
                if wrap:
                    response=self.wrapAsResponse(response)
                if timer:
                    end=time.time()
                    print('Time consumed:%s'%(end -start))
                return response
            self.router.add_route('GET',path,wrapper)
            return wrapper
        return decorator
    def get3(self,path,wrap=False,cookies=False,headers=False,request=False,timer=False):  ## 与get1不同，get2的没有对返回值的包装，因此原函数需自己返回一个web.Responce对象
        def decorator(func):
            args=inspect.getargspec(func).args
            @functools.wraps(func)
            async def wrapper(req):
                if timer:
                    start=time.time()
                logging.info('run %s' % func.__name__)
                args2=args.copy()
                data = {}
                fdata = await req.post()
                cdata = req.cookies
                hdata = req.headers
                if headers:
                    data.update(hdata)
                if cookies:
                    data.update(cdata)
                if 'request' in args:
                    data['request'] = req
                if 'form' in args:
                    data['form'] = fdata
                if 'cookies' in args:
                    data['cookies'] = cdata
                if 'headers' in args:
                    data['headers'] = hdata
                data.update(fdata)
                data.update(req.match_info)
                params = []
                for arg in args:
                    param = data.get(arg, 'not_find')
                    if param == 'not_find':
                        logging.warning('参数%s未找到,将以None替代' % arg)
                        params.append(None)
                    else:
                        params.append(param)
                ret = await func(*params)
                if wrap:  ##函数返回值还需进行包装
                    ret = self.wrapAsResponse(ret)
                if timer:
                    end=time.time()
                    print('Time consumed:%s'%(end -start))
                return ret
            self.router.add_route('GET',path,wrapper)
            return wrapper
        return decorator


    def post4(self,path,request=False,json=False,form=False,cookies=False,headers=False,wrap=False): ##req,json,form同时只能有一个为True
        def decorator(func):
            args1=inspect.getargspec(func).args  ##获取原函数参数            @functools.wraps(func)
            async def wrapper(req):
                logging.info('run %s'%func.__name__)
                args=args1.copy()
                if cookies:
                    last=args.pop()
                    if last!='cookies':
                        raise Exception('函数%s最后一个参数应为cookies,而非%s'%(func.__name__,last))
                elif headers:
                    last=args.pop()
                    if last!='headers':
                        raise Exception('函数%s最后一个参数应为headers,而非%s'%(func.__name__,last))
                elif request:  ##  直接将request作为参数
                    last = args.pop()
                    if last != 'request':
                        raise Exception('函数%s最后一个参数应为request,而非%s' % (func.__name__, last))
                data={}
                if form:  ## 参数来源：表单
                    fd = await req.post()
                    data.update(fd)
                elif json:  ##参数来源： json
                    jd = await req.json()
                    data.update(jd)
                    logging.info('json data:%s' % (data))

                md = req.match_info
                data.update(md)
                params = []
                for i in args:
                    try:
                        params.append(data[i])
                    except:
                        raise Exception('函数%s参数%s定义不匹配' % (func.__name__, i))
                if cookies:
                    co = req.cookies
                    params.append(co)
                elif headers:
                    co = req.headers
                    params.append(co)
                elif request:
                    params.append(req)
                ret = await func(*params)
                if wrap: ##函数返回值还需进行包装
                    ret=self.wrapAsResponse(ret)
                return ret
            self.router.add_route('POST',path,wrapper)
            return wrapper
        return decorator
    def post5(self,path,request=False,json=False,form=False,cookies=False,headers=False,wrap=False,timer=False): ##最新版功能强大
        def decorator(func):
            args1=inspect.getargspec(func).args  ##获取原函数参数            @functools.wraps(func)
            async def wrapper(req):
                if timer:
                    start=time.time()
                logging.info('run %s'%func.__name__)
                args=args1.copy()
                ## gather data
                data={}
                fdata=await req.post()
                try:
                    jdata=await req.json()
                except:
                    jdata={}
                cdata=req.cookies
                hdata=req.headers
                if headers:
                    data.update(hdata)
                if cookies:
                    data.update(cdata)
                if 'request' in args:
                    data['request']=req
                if 'form' in args:
                    data['form']=fdata
                if 'json' in args:
                    data['json'] = jdata
                if 'cookies' in args:
                    data['cookies']=cdata
                if 'headers' in args:
                    data['headers']=hdata
                data.update(fdata)
                data.update(jdata)
                data.update(req.match_info)
                params=[]
                for arg in args:
                    param=data.get(arg,'not_find')
                    if param=='not_find':
                        logging.warning('参数%s未找到,将以None替代'%arg)
                        params.append(None)
                    else:
                        params.append(param)
                ret = await func(*params)
                if wrap: ##函数返回值还需进行包装
                    ret=self.wrapAsResponse(ret)
                if timer:
                    end = time.time()
                    print('Time consumed:%s'%(end - start))
                return ret
            self.router.add_route('POST',path,wrapper)
            return wrapper
        return decorator

    def add_route(self,**kws):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(request):
                return await func(request)
            self.router.add_route(**kws)
            return wrapper
        return decorator
    @classmethod
    def wrapAsResponse(cls,dic):
        found=dic.get('__template__')
        if found:
            file=dic.pop('__template__')
            html=cls.render_template(file,dic)
            return web.Response(body=html,content_type='text/html')
        json=dic.get('json')
        if json:
            return web.json_response(json)
    @classmethod
    def render_template(cls,file, dic):
        tem = env.get_template(file)
        return tem.render(dic)











    # def get(self,path):
    #     def decorator(func):
    #         args=inspect.getargspec(func).args
    #         @functools.wraps(func)
    #         async def wrapper(request):
    #             logging.info('run %s' % func.__name__)
    #             if args!=[]:
    #                 params = []
    #                 req=False
    #                 if args[-1]=='request':
    #                     req=args.pop()
    #                 for i in args:
    #                     try:
    #                         params.append(request.match_info[i])
    #                     except:
    #                         raise Exception('函数%s参数定义不匹配' % func.__name__)
    #                 if req:
    #                     params.append(request)
    #
    #                 retdict =await func(*params)
    #             else:
    #                 retdict =await func()
    #             response=self.wrapAsResponse(retdict)
    #             return response
    #         self.router.add_route('GET',path,wrapper)
    #         return wrapper
    #     return decorator
def render_template(self,file, dic):
    tem = env.get_template(file)
    return tem.render(dic)














class RequestHandler(object):
    def __init__(self,func):
        self.__func=func

def get(path):
    def decorator(func):
        @functools.wraps(func)
        def wapper(*args,**kws):
            rv=func(args,kws)
            return web.Response()
