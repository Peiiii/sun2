import os,time,chardet,pickle,json
from pathlib import Path
class InfoBody(dict):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
    def hi(self):
        print('hi')
    def __getattr__(self, key,default='DEFAULT'):
        try:
            value=self[key]
            return value
        except KeyError as k:
            if not default=="DEFAULT":
                return default
            raise Exception('No attribute %s'%key)
    def __setattr__(self, key, value):
        self[key]=value
    def __getstate__(self):
        return self.__dict__
    def __setstate__(self, state):
        self.__dict__=state
    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            return None
    def met(self,**kws):
        for k,v in kws.items():
            if self.get(k,'notfound')=='notfound':
                return False
            if self[k] != v:
                return False
        return True
    def gets(self,keys):
        assert isinstance(keys,list)
        dic={}
        for k in keys:
            dic[k]=self[k]
        return InfoBody(dic)
    @classmethod
    def fromObj(cls,obj,keys=None):
        dic={}
        if not keys:
            for k in obj.__dict__:
                v=getattr(obj,k)
                if not callable(v):
                    dic[k]=v
            return cls(dic)
        for k in keys:
            dic[k]=obj.get(k,None)
        return cls(dic)

class PathTypes:
    def __init__(self):
        self.F = 'FILE'
        self.D = 'DIR'
        self.L = 'LINK'
        self.M = 'MOUNT'
        self.S = 'SOCKET'
        self.U = 'UNKNOWN'
PT=PathTypes()
class Qpath(InfoBody):
    def __init__(self,path):
        super().__init__()
        self.create_str=str(path)
        self.path=self.abspath()
        self.type=self.getType()
        path=self.path
        self.name = os.path.basename(path)
        self.size = os.path.getsize(path)
        self.atime = os.path.getatime(path)
        self.ctime = os.path.getctime(path)
        self.mtime = os.path.getmtime(path)
        self.fatime=self.getFatime()
        self.fctime=self.getFctime()
        self.fmtime=self.getFmtime()
    def shortInfo(self):
        return self.__dict__
    def info(self):
        children=self.getChildren()
        files=self.getFileChildren()
        dirs=self.getDirChildren()
        links=self.getChildrenByType(type=PT.L)
        mounts=self.getChildrenByType(type=PT.M)
        dic=InfoBody(
            children=children,files=files,dirs=dirs,links=links,mounts=mounts
        )
        dic.update(self)
        return dic
    def getFatime(self):
        return self.formatTime(self.atime)
    def getFctime(self):
        return self.formatTime(self.ctime)
    def getFmtime(self):
        return self.formatTime(self.mtime)
    def formatTime(self,t,format='%Y-%m-%d %H:%M:%S'):
        return time.strftime(format,time.gmtime(t))
    def getChildren(self):
        children=[Qpath(self/p) for p in self.listdir()]
        return children
    def getFileChildren(self):
        return self.getChildrenByType(type=PT.F)
    def getDirChildren(self):
        return self.getChildrenByType(type=PT.D)
    def getChildrenByType(self,type):
        children=self.getChildren()
        ch_typed=[]
        for c in children:
            ch_typed.append(c) if c.type==type else None
        return ch_typed
    def getType(self):
        path=self
        if path.isdir():
            return PT.D
        if path.isfile():
            return PT.F
        if path.islink():
            return PT.L
        if path.ismount():
            return PT.M
        else:
            return PT.U
    def abspath(self):
        return os.path.abspath(self.create_str)
    def listdir(self):
        return os.listdir(self.create_str)
    def isdir(self):
        return os.path.isdir(self.create_str)
    def isfile(self):
        return os.path.isfile(self.create_str)
    def islink(self):
        return os.path.islink(self.create_str)
    def ismount(self):
        return os.path.ismount(self.create_str)
    def __truediv__(self, other):
        return self.create_str+'/'+other
class MyOSResponse(InfoBody):
    def __init__(self,success=True,code=0,message='Operation succeeded.',*args,**kwargs):
        super().__init__(success=success,code=code,message=message,*args,**kwargs)
class MyOS:
    def __init__(self,static_path='./static'):
        self.static_path=Qpath(static_path)
    def do(self,dic):
        dic=self.wrap(dic)
        return self.eval(dic)
    def wrap(self,dic):
        return InfoBody(dic)
    def eval(self,dic):
        resp=MyOSResponse()
        try:
            data=self.execute(dic,resp)
            resp.data=data
        except:
            resp.success=False
            resp.code=1
            resp.message='Opration failed.'
            raise
        return resp
    def execute(self,dic,resp=None):
        optype = dic.optype
        if optype == 'getdirinfo':
            return self.getDirInfo(dic.path)
        if optype == 'mkdir':
            return self.mkdir(dic.path)
        if optype =='mkfile':
            return self.mkfile(dic.path)
        if optype == 'readfile':
            return self.readFile(dic.path)
        if optype == 'writefile':
            return self.writeFile(dic.path, dic.content)
        if optype == 'rename':
            return self.rename(dic.src,dic.dst)
        if optype == 'remove':
            return self.remove(dic.path)
        if optype == 'rmdir':
            return self.rmdir(dic.path)
        if optype == 'removedirs':
            return self.removedirs(dic.path)
        if optype == 'upload':
            file_data=dic.file_data
            return self.upload(file_data,resp)
        raise Exception('optype illeagal: %s'%optype)
    def upload(self,file_data,resp):
        fn=file_data.filename
        content_type=file_data.content_type
        file=file_data.file
        type=content_type.split('/')[0]
        fpath=self.getDefaultUploadPath(fn,content_type)
        bytes=file.read()
        self.writeFile(fpath,content=bytes)
        resp.error='File link here:%s'%fpath.split(self.static_path.create_str)[-1]
        return  fpath
    def getDefaultUploadPath(self,fn,content_type='text/plain'):
        content_type=content_type.lower()
        types=content_type.split('/')
        [type1,type2]=types
        fpath=self.static_path/'upload/%s/'+fn
        if content_type=='text/plain':
            fpath=fpath%'txts'
        elif content_type=='text/markdown':
            fpath=fpath%'mds'
        elif content_type=='text/html':
            fpath=fpath%'htmls'
        elif type1=='image':
            fpath=fpath%'imgs'
        else:
            fpath=fpath%'unknown'
        return fpath
    def removedirs(self,path):
        return os.removedirs(path)
    def rmdir(self,path):
        return os.rmdir(path)
    def remove(self,path):
        return os.remove(path)
    def rename(self,src,dst):
        print(src,dst)
        return os.rename(src,dst)
    def renames(self,src,dst):
        return os.renames(src,dst)
    def getDirInfo(self,path):
        return Qpath(path).info()
    def mkdir(self,name):
        return os.mkdir(name)
    def makedirs(self,path):
        return self.makedirs(path)
    def readFile(self,path,mode='rb'):
        with open(path,mode=mode) as f:
            return f.read()
    def writeFile(self,path,content,mode='wb'):
        with open(path ,mode=mode) as f:
            f.write(content)
    def mkfile(self,path):
        if os.path.exists(path):
            base=os.path.basename(path)
            dir=os.path.dirname(path)
            newpath=dir+'/u'+base
            return self.mkfile(newpath)
        return self._makefile(path)
    def _makefile(self,path):
        f=open(path,'w')
        f.close()

def test1():
    p=Qpath('.')
    cs=p.getChildren()
    info=p.info()
    print(info.files)
if __name__=="__main__":
    test1()
    pass