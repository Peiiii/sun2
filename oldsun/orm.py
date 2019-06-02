import os,pickle
class MyDict(dict):
    def __getattr__(self, item):
        try:
            return self[item]
        except:
            raise AttributeError('MyDict object has no attribute %s' % item)

class InfoBody(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as k:
            return None
    def __setattr__(self, key, value):
        self[key]=value
    def __getstate__(self):
        return self.__dict__

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            return None

class Map:
    def __init__(self,path):
        self.path=os.path.abspath(path)
        self.initialize()
    def initialize(self):
        if(os.path.exists(self.path)):
            self.load()
        else:
            self.dic={}
            self.save()
    def _rebuild(self):
        if(os.path.exists(self.path)):
            os.remove(self.path)
        self.initialize()
    def save(self):
        f=open(self.path,'wb')
        pickle.dump(self.dic,f)
        f.close()
    def load(self):
        f=open(self.path,'rb')
        line=f.readline()
        if not line:
            f.close()
            self._rebuild()
        else:
            f.close()
        f=open(self.path,'rb')
        obj=pickle.load(f)
        self.dic=obj
        return obj
    def add(self,key,value):
        self.load()
        re=self.dic.get(key,'notfound')
        if re=='notfound':
            self.dic[key]=value
        else:
            raise Exception('record with primary_key:%s existed.'%key)
        self.save()
    def update(self,pk,**kws):
        self.load()
        self.dic[pk].update(kws)
        self.save()
    def find(self,key):
        self.load()
        re=self.dic.get(key,'notfound')
        if re!='notfound':
            return re
    def exsist(self,key):
        self.load()
        # print(self.dic.keys())
        re = self.dic.get(key, 'notfound')
        if re != 'notfound':
            return True
        return False
    def delete(self,key):
        self.load()
        re = self.dic.get(key, 'notfound')
        if re!='notfound':
            o=self.dic.pop(key)
            self.save()
            return True
    def findAll(self,**kws):
        all=[]
        self.load()
        for pKey,o in self.dic.items():
            found=True
            for k,v in kws.items():
                if getattr(o,k)!=v:
                    found=False
                    break
            if found:
                all.append(o)
        return all
    def deleteAll(self,**kws):
        self.load()
        count=0
        for pKey, o in self.dic.items():
            found = True
            for k, v in kws:
                if getattr(o, k) != v:
                    found = False
                    break
            if found:
                self.delete(pKey)
                count=count+1
        self.save()
        return count





class Table:
    def __init__(self,path,primary_key,searchable_keys=[]):
        self.path=os.path.abspath(path)
        self.primary_key=primary_key
        self.searchable_keys=searchable_keys
        self._checkDirectory()
        self.map=Map(self.path+os.sep+os.path.basename(self.path)+'.map')
    def _checkDirectory(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def initialize(self):
        pass
    async def insert(self,obj):
        if not self._exsist(obj):
            return self._add(obj)
        return False
    async def delete(self,pkey):
        if not self.map.exsist(pkey):
            raise Exception('Failed:  record you want to delete width primary_key:%s not found .'%pkey)
        self.map.delete(pkey)
        self._removeRecord(pkey)
        return True
    async def replace(self,pk,obj):
        await self.delete(pk)
        return await self.insert(obj)
    async def update(self,pk,**kws):
        if not self.map.exsist(pk):
            raise Exception('update failed: record not found. primary_key: %s'%pk)
        self.map.update(pk,**kws)
        record=self._getRecord(pk)
        record=self._updateObj(record,**kws)
        return self._writePickleFile(record,self._abspath(pk+'.rcd'))
    async def exsist(self,pk):
        return self.map.exsist(pk)
    async def select(self,fields,**kws):
        all=self.map.findAll(**kws)
        all2=[]
        for o in all:
            ib={ field:getattr(o,field,None) for field in fields}
            ib=InfoBody(ib)
            all2.append(ib)
        return all2
    async def find(self,pk):
        if not self.map.exsist(pk):
            return False
        return self._getRecord(pk)
    async def findAll(self,**kws):
        all=self.map.findAll(**kws)
        pks=[getattr(obj,self.primary_key) for obj in all]
        all=[self._getRecord(pk) for pk in pks]
        return all
    async def findAllLikeThis(self,func):
        all=self.map.findAll()
        new_all=[]
        for obj in all:
            if(func(obj)):
                new_all.append(self._getRecordByObj(obj))
        return new_all

    def _updateObj(self,obj,**kws):
        ## obj.update()
        for k,v in kws:
            setattr(obj,k,v)
        return obj
    def _toInfoBody(self,obj):
        dic={}
        for k in self.searchable_keys:
            dic[k]=getattr(obj,k)
        return InfoBody(dic)
    def _getObjPK(self,obj):
        return getattr(obj,self.primary_key)
    def _getRecordByObj(self,obj):
        return self._getRecord(self._getObjPK(obj))
    def _getRecord(self,pk):
        return self._loadPickleFile(self._abspath(pk+'.rcd'))
    def _exsist(self,obj):
        return self.map.exsist(getattr(obj,self.primary_key))
    def _add(self,obj):
        pk=getattr(obj,self.primary_key)
        self.map.add(pk,self._toInfoBody(obj))
        self._writePickleFile(obj,self._abspath(pk+'.rcd'))
        return True
    def _abspath(self,fname):
        return self.path+os.sep+os.path.basename(fname)
    def _removeRecord(self,pkey):
        os.remove(self.path+os.sep+pkey+'.rcd')
    def _loadPickleFile(self,fpath):
        f=open(fpath,'rb')
        obj=pickle.load(f)
        f.close()
        return obj
    def _writePickleFile(self,obj,fpath):
        f=open(fpath,'wb')
        ret=pickle.dump(obj,f)
        f.close()
        return ret

class Field:
    def __init__(self,name,default):
        self.name=name
        self.default=default


class ModelMetaclass(type):
    def __new__(cls, name,bases,attrs):
        pass


class DBDirectory:
    def __init__(self,path,initial=False):
        self.path=os.path.abspath(path)
        self.mapfile=self.path+os.sep+os.path.basename(self.path)+'.map'
        if initial==True:
            self.makeSelf()
    def makeSelf(self):
        os.mkdir(self.path)
        map=self._getInitialMap()
        self._writePickleFile(map, self.mapfile)
    def _getInitialMap(self):
        return []
    def addFile(self,content,fname):
        self._writePickleFile(content,self._abspath(fname))
        map=self._getMap()
        map.append(fname)
        self._saveMap(map)
    def removeFile(self,fname):
        os.remove(self._abspath(fname))
        map=self._getMap()
        map.remove(fname)
        self._saveMap(map)
    def _rebuild(self):
        files=os.listdir(self.path)
        files.remove(os.path.basename(self.mapfile))
        self._saveMap(files)
    def _getMap(self):
        map=self._loadPickleFile(self.mapfile)
        return map
    def _saveMap(self,map):
        self._writePickleFile(map,self.mapfile)
    def _abspath(self,fname):
        return self.path+os.sep+os.path.basename(fname)

    def _loadPickleFile(self,fpath):
        f=open(fpath,'rb')
        obj=pickle.load(f)
        f.close()
        return obj
    def _writePickleFile(self,obj,fpath):
        f=open(fpath,'wb')
        ret=pickle.dump(obj,f)
        f.close()
        return ret