import asyncio,functools
class Rlist(list):
    def sortBy(self,key,reverse=True):
        li=sorted(self,key=lambda x: x[key] ,reverse=reverse)
        return li
    def sliceBy(self,func):
        copy=[]
        for i in self:
            if func(i):
                copy.append(i)
        return Rlist(copy)
    def hi(self):
        print("hi,I'm rlist.")
    def find(self,**kws):
        if len(self)<1:
            return
        for item in self:
            assert isinstance(item,dict)
            if InfoBody(item).met(**kws):
                return item
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
def rlist(func):
    iscoroutine=asyncio.iscoroutine(func)
    if iscoroutine:
        @functools.wraps(func)
        def wrapper(*args,**kwargs):
            loop=asyncio.get_event_loop()
            result=loop.run_until_complete(func(*args,**kwargs))
            if isinstance(result,list):
                return Rlist(result)
            return result
        return wrapper
    else:
        @functools.wraps(func)
        def wrapper(*args,**kwargs):
            result=func(*args,**kwargs)
            if isinstance(result,list):
                return Rlist(result)
            return result
        return wrapper