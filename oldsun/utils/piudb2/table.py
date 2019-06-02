from .supported_classes import InfoBody,Rlist,rlist
from .utils import jsonLoad,jsonDump,pickleDump,pickleLoad,log
import os,functools,asyncio,inspect

class DBError:
    def __init__(self):
        pass
    def NotFound(self,msg):
        self.log('NotFoundError',msg)
    def ExistedPK(self,msg):
        self.log('PrimaryKeyAlreadyExisted',msg)
    def TypeError(self,msg):
        self.log('TypeError',msg)
    def NotFoundPK(self,msg):
        self.log('NotFoundPrimaryKey',msg)
    def FieldError(self,msg):
        self.log('FieldError','Field not exists or unsearchable: %s'%msg)
    def Error(self,msg):
        self.log('Error',msg)
    def log(self,error_name,info):
        return '%s  : %s'%(error_name,info)

def preload(func):
    iscoroutine=asyncio.iscoroutine(func)
    if iscoroutine:
        @functools.wraps(func)
        def wrapper(self,*args,**kwargs):
            self.load()
            loop=asyncio.get_event_loop()
            result=loop.run_until_complete(func(self,*args,**kwargs))
            return result
        return wrapper
    else:
        @functools.wraps(func)
        def wrapper(self,*args,**kwargs):
            self.load()
            result=func(self,*args,**kwargs)
            if isinstance(result,list):
                return Rlist(result)
            return result
        return wrapper
class Record(dict):
    def slice(self,keys):
        assert isinstance(keys,list)
        dic={}
        for k in keys:
            dic[k]=self[k]
        return Record(dic)

    def met(self, **kws):
        for k, v in kws.items():
            if self.get(k, 'notfound') == 'notfound':
                return False
            if self[k] != v:
                return False
        return True

    def gets(self, keys):
        assert isinstance(keys, list)
        dic = {}
        for k in keys:
            dic[k] = self[k]
        return InfoBody(dic)
class Table:
    '''
        Like a database,doesn't store records, but store objects directly .
        apis:
           find, findAll, insert, update, delete,exist:  => Record object
           select: =>InfoBody
        Record: primary_key(:str), searchable_keys(:[str]), keys(i.e. "id","name")

        ### API的异常处理逻辑：所有的参数检查由顶层API完成，下层方法的原则是，只要求最少的信息，且不做任何参数检查，假设上层会完成这些工作
        #### 模型的接口应该干净，明确。不要冗余，方便的操作可以单独提供方法。
        我将重构本模块的代码，对于Table类，修改为，上层调用只允许输入key-value键值对。
        操作类型：增、删、改、查
        调用insert,update时将对输入的键值对做参数检查。
        对于查询操作也有参数检查。
        参数检查： _checkParameters()

        原则：
        1、顶层API做参数检查，下层API不作检查，或者用assert语句排除。
        2、下层API输入输出力求精简，只要求提供最少的信息
        3、命名规则：顶层API普通命名，下层API采取下划线命名。异步方法和同步方法采取不同命名
        4、同时提供同步和异步两种API。
        5、添加或修改记录时，把输入的键值对集合封装成Record。
        6、操作对象：Record。方法：dump,load。具体采用的方式：JSON or Pickle.
        7、支撑方法：

    '''

    mapfilename='mapfile.map'
    confiurefilename='configure.cfg'
    records_dirname='records'
    apis=[]
    def __init__(self,tpath):
        '''  A table was created under the assumption of : an existed dir ; a map file;'''
        self.tpath=tpath
        self.mpath=self._joinPath(Table.mapfilename)
        self.cpath=self._joinPath(Table.confiurefilename)
        self.rpath=self._joinPath(Table.records_dirname)
        self.errors = DBError()
        self._load()
    def _load(self):
        '''
        load map file and confiure file, add attibutes: primary_key,searchable_keys,keys.
        :return:
        '''
        self._loadMap()
        self._loadConfigure()
    def _loadMap(self):
        self.map=self._pickleLoad(self.mpath)
        self.map.mpath=self.mpath
    def _loadConfigure(self):
        self.configure = self._pickleLoad(self.cpath)
        self.configure.cpath=self.cpath
        self.primary_key = self.configure.primary_key
        self.searchable_keys = self.configure.searchable_keys
        self.all_keys = self.configure.all_keys
        self.fields = self.configure.fields
        self.TEST_MODE = self.configure.test_mode
    @classmethod
    def api(cls,func):
        cls.apis.append(func.__name__)
        return func
        
##------------------------------------代码重构----------------------------------------##
    async def insert(self, **kws):
        return self._insert_(**kws)
    def _insert_(self,**kws):
        record = Record(**kws)
        record = self._checkRecord(record)
        pk = record[self.primary_key]
        assert not self.map.existsPK(pk)
        self._dumpRecord(record)
        self.map.insert(pk, self._getMappedRecord(record))
        return record
    async def upsert(self,**kws):
        return self._upsert_(**kws)
    def _upsert_(self,**kws):
        record=self._dicToRecord(**kws)
        pk=record.get(self.primary_key,None)
        if pk == None:
            print('record:',record)
            raise Exception('Primary key %s is not given'%(self.primary_key))
        if self.map.existsPK(pk):
            return self._updateByPK_(pk,**kws)
        kws[self.primary_key]=pk
        return self._insert_(**kws)
    async def upsertByPK(self,pk,**kws):
        return self._updateByPK_(pk,**kws)
    def _upsertByPK_(self,pk,**kws):
        if self.map.exists(pk):
            return self.updateByPK(pk,**kws)
        kws[self.primary_key]=pk
        return self._insert_(**kws)
    @rlist
    async def select(self,selected_keys=[],**kws):
        '''  Assume that you only use select when you only need some brief info. '''
        return self._select_(selected_keys=selected_keys,**kws)
    @rlist
    def _select_(self,selected_keys=[],**kws):
        '''  Assume that you only use select when you only need some brief info. '''
        if selected_keys==[]:
            selected_keys=self.searchable_keys
        ibs=self.map.select(wanted_keys=selected_keys,**kws)
        return ibs
    async def updateByPK(self,pk,**kws):
        return self._updateByPK_(pk,**kws)
    def _updateByPK_(self,pk,**kws):
        if not self.map.existsPK(pk):
            raise self.errors.NotFoundPK(pk)
        record=self._findByPK_(pk)
        record.update(**kws)
        self._dumpRecord(record)
        dic=self._getMappedRecord(record)
        self.map.update(pk,**dic)
        return record
    async def update(self,kws,where):
        return self._update_(kws,where)
    def _update_(self,kws,where):
        assert isinstance(kws,dict)
        assert isinstance(where,dict)
        recs=self._findAll_(**where)
        for r in recs:
            r.update(kws)
            self._replace(r[self.primary_key],r)
        return len(recs)
    @rlist
    async def delete(self,pk):
        return self._delete_(pk)
    @rlist
    def _delete_(self,pk):
        if not self.map.existsPK(pk):
            raise self.errors.NotFoundPK(pk)
        record=self._findByPK_(pk)
        self._removeRecordFile(pk)
        self.map.delete(pk)
        self._log('Successfully delete record width %s = %s'%(self.primary_key,pk))
        return record
    @rlist
    async def deleteAll(self,**where):
        return self._deleteAll_(**where)
    @rlist
    def _deleteAll_(self,**where):
        self._verifySearchableKeys(where)
        pks=self.map.findAll(**where)
        for pk in pks:
            self._delete_(pk)
        return len(pks)

    @rlist
    async def findAll(self,**kws):
        return self._findAll_(**kws)
    @rlist
    def _findAll_(self, **kws):
        ''' You may specify your  own  checker here'''
        checker= kws.pop('__checker__') if '__checker__' in kws.keys() else None
        if checker:
            all_met=[]
            pks=self.map.findAll()
            for pk in pks:
                record=self._loadRecord(pk)
                if checker(record):
                    all_met.append(record)
            return all_met
        pks = self.map.findAll(**kws)
        return [self._loadRecord(pk) for pk in pks]
    async def find(self,**kws):
        return self._find_(**kws)
    def _find_(self, **kws):
        pk = self.map.find(**kws)
        return self._loadRecord(pk)
    async def findByPK(self,pk):
        return self._findByPK_(pk)
    def _findByPK_(self,pk):
        if self.map.existsPK(pk):
            return self._loadRecord(pk)
        return None
    async def existsPK(self,pk):
        return self._existsPK_(pk)
    def _existsPK_(self,pk):
        return self.map.existsPK(pk)
    async def exists(self,**kws):
        return self._exists_(**kws)
    def _exists_(self,**kws):
        '''
            Assume that only one map object is running at one time ,
            which assures the map obj is always identical width the mapfile.
        '''
        self._verifySearchableKeys(kws)
        return self.map.exists(**kws)

##-------------------------------------divider------------------------------------------##
    # manage methods
    def _addField(self,name,fdef,exist_ok=False,searchable=True):
        self.configure.addField(name,fdef,exist_ok=exist_ok,searchable=searchable)
        self._loadConfigure()
        records=self._findAll_()
        for r in records:
            r=self._autoFillByDefault(r)
            self._replace(r[self.primary_key],r)
            self.map.replace(r[self.primary_key],self._getMappedRecord(r))
        self._log('Add field %s'%name)
        return len(records)
    def _addFields(self,fields,exist_ok=False,searchable=True):
        assert isinstance(fields,dict)
        for k,v in fields.items():
            self._addField(name=k,fdef=v,exist_ok=exist_ok,searchable=searchable)
    def _deleteField(self,name):
        self.configure.deleteField(name)
        self._loadConfigure()
        records = self._findAll_()
        for r in records:
            r=self._removeUnsupportedKeys(r)
            self._replace(r[self.primary_key], r)
            self.map.replace(r[self.primary_key],self._getMappedRecord(r))
        self._log('Delete field %s' % name)
        return len(records)
    def _deleteFields(self,names):
        assert isinstance(names,list)
        for n in names:
            self._deleteField(name=n)
    ##-------------------------------------divider------------------------------------------##

    def _replace(self,pk,record):
        self._delete_(pk)
        self._insert_(**record)
    def _saveMap(self):
        return pickleDump(self.map,self.mpath)

    def _joinPath(self,fname):
        return self.tpath+'/'+fname
    def _joinRecordPath(self,fname):
        return self.rpath+'/'+fname
    def _getRecordFileName(self,pk):
        return pk+'.rcd'
    def _getRecordPath(self,pk):
        return self.rpath+'/'+pk+'.rcd'
    def _log(self,text,type='Info'):
        print('***** {} ==>: {}'.format(type,text))
    def _warning(self,text,type='warning'):
        print('****Table {}****==>: {}'.format(type,text))
    def _addErrors(self):
        self.ErrorNotFound=Exception('not found.')
        self.ErrorPrimaryKeyExisted=Exception('Primary_key existed')

##-------------------------------------代码重构------------------------------------------##


    ##------------------------------------------------------------------------##
    def _dicToRecord(self,**kws):
        record=Record(**kws)
        record=self._autoFillByDefault(record)
        return record
    def _getMappedRecord(self,record):
        record=Record(**record)
        try:
            return record.slice(self.searchable_keys)
        except:
            print(record.__class__)
            raise
    def _removeUnsupportedKeys(self,record):
            keys=[]
            for k in record.keys():
                if not k in self.all_keys:
                   keys.append(k)
            [record.pop(k) for k in keys]
            return record
    def _autoFillByDefault(self,record):
        for name,fdef in self.fields.items():
            if record.get(name,'notfound')=='notfound':
                # if can't find the value, the give one by default
                value= fdef.default() if callable(fdef.default) else fdef.default
                record[name]=value
                tlog('Set default value for filed: %s = %s'%(name,value))
        return record
    def _checkRecord(self,record):
        record=self._autoFillByDefault(record)
        if self.map.existsPK(record[self.primary_key]):
            self.errors.ExistedPK(record[self.primary_key])
        record=self._removeUnsupportedKeys(record)
        return record
    def _verifySearchableKeys(self,dic):
        for k in dic.keys():
            if not (k in self.searchable_keys):
                self.errors.FieldError(k)
        return True
    ##------------------------------------------------------------------------##
    # API的异常处理逻辑：所有的参数检查由顶层API完成，下层方法的原则是，
    # 只要求最少的信息，且不做任何参数检查，假设上层会完成这些工作
    def _removeRecordFile(self,pk):
        os.remove(self._joinRecordPath(pk))
        self.tlog('Record file removed: %s'%(self._joinRecordPath(pk)))
    def _dumpRecord(self,record):
        pk=record[self.primary_key]
        print(record)
        self._jsonDump(self._recordToJson(record),self._joinRecordPath(pk))
    def _loadRecord(self,pk):
        fpath=self._joinRecordPath(pk)
        dic=self._jsonLoad(fpath)
        return self._jsonToRecord(dic)
    def _recordToJson(self,record):
        ''' if it needs to be transformed ... '''
        return record
    def _jsonToRecord(self,jsonObj):
        ''' if it needs to be transformed ... '''
        return jsonObj
    def _jsonDump(self,obj,fpath):
        jsonDump(obj=obj,fpath=fpath)
    def _jsonLoad(self,fpath):
        return jsonLoad(fpath=fpath)
    @classmethod
    def _pickleDump(self,obj,fpath):
        pickleDump(obj=obj,fpath=fpath)
    @classmethod
    def _pickleLoad(self,fpath):
       return pickleLoad(fpath=fpath)
 ##-------------------------------------divider------------------------------------------##
    def tlog(self,*args, **kwargs):
        try:
            if self.TEST_MODE:
                return self.log(*args, **kwargs)
        except:
            print('********warning , "TEST_MODE" is not setted in the module, which is needed to run "tlog()" ')

    def log(self,*args, num=20, str='*'):
        print(str * num, end='')
        print(*args, end='')
        print(str * num)
    @classmethod
    def _create_whatever(cls,tpath,primary_key,searchable_keys,fields,all_keys,test_mode=True,create_force=False):
        rpath = tpath + '/' + cls.records_dirname
        mpath = tpath + '/' + cls.mapfilename
        cpath = tpath + '/' + cls.confiurefilename
        if not os.path.exists(tpath):
            os.makedirs(tpath)
        if not os.path.exists(rpath):
            os.makedirs(rpath)
        map=Map()
        configure = Configure(primary_key, searchable_keys, all_keys=all_keys, fields=fields,test_mode=True)
        cls._pickleDump(map,mpath)
        cls._pickleDump(configure,cpath)
        return cls(tpath=tpath)
    @classmethod
    def _existsATable(cls,tpath):
        ''' This is not perfect , needs to be fixed. '''
        mpath=tpath+'/'+cls.mapfilename
        if (not os.path.exists(tpath)) or (not os.path.exists(mpath)):
            return False
        return True

class Configure(InfoBody):
    def __init__(self,primary_key,searchable_keys=[],all_keys=[],fields={},test_mode=True):
        assert isinstance(primary_key,str)
        assert isinstance(searchable_keys,list)
        assert isinstance(fields,dict)
        assert len(searchable_keys)>0
        assert fields != {}
        if not searchable_keys:
            searchable_keys=[primary_key]
        if not primary_key in searchable_keys:
            searchable_keys.append(primary_key)
        self.primary_key=primary_key
        self.searchable_keys=searchable_keys
        self.all_keys=all_keys
        self.fields=fields
        self.test_mode=test_mode
    def save(self,cpath=None):
        if not cpath:
            cpath=self.cpath
        pickleDump(self,cpath)
    def addField(self,name,fdef,exist_ok=False,searchable=True):
        assert name!=self.primary_key
        if name in self.fields.keys() and not exist_ok:
            raise Exception('Field "%s" already exists ..'%(name))
        self.all_keys.append(name)
        if searchable:
            self.searchable_keys.append(name)
        self.fields[name] = fdef
        self.save()
    def deleteField(self,name):
        if not name in self.all_keys:
            raise Exception('Field "%s" not existed '%name)
        if name==self.primary_key:
            raise Exception('Primary key %s cannot be deleted.'%self.primary_key)
        self.all_keys.remove(name)
        self.searchable_keys.remove(name) if name in self.searchable_keys else None
        self.fields.pop(name)
        self.save()

##-------------------------------------------------------------------//

class Map:
    def __init__(self,mpath=None):
        self.dic=InfoBody()
        if mpath:
            self.mpath=mpath
    @preload
    def select(self,wanted_keys=[],**kws):
        ''' there is a small problem '''
        ret=[]
        for pk,obj in self.dic.items():
            if pk=="__dict__":
                continue
            if obj.met(**kws):
                ib=obj.gets(wanted_keys)
                ret.append(ib)
        return ret
    @preload
    def delete(self,pk):
        del self.dic[pk]
        self.save()
    @preload
    def insert(self,pk,obj):
        self.dic[pk]= obj
        self.save()
    @preload
    def update(self,pk,**kws):
        self.dic[pk].update(**kws)
        self.save()
    @preload
    def replace(self,pk,rec):
        self.dic[pk]=rec
        self.save()
    @preload
    def findAll(self,**kws):
        ibs=[]
        pks=[]
        for pk,ib in self.dic.items():
            if pk=='__dict__':
                continue
            found=True
            for k,v in kws.items():
                if ib.get(k)!=v:
                    found=False
                    break
            if found:
                ibs.append(ib)
                pks.append(pk)
        return pks
    @preload
    def find(self,**kws):
        for pk,ib in self.dic.items():
            found=True
            for k,v in kws.items():
                if ib.get(k)!=v:
                    found=False
                    break
            if found:
                return pk
        return None
    @preload
    def existsPK(self,pk):
        if self.dic.get(pk,'notfound')!='notfound':
            return True
        return False
    @preload
    def exists(self,**kws):
        for ib in self.dic.values():
            found=True
            for k,v in kws.items():
                if ib.get(k)!=v:
                    found=False
                    break
            if found:
                return True
        return False
    def getRecordFileName(self,pk):
        if isinstance(pk,list):
            return [r+'.rcd' for r in pk]
        return pk+'.rcd'
    def load(self):
        self=pickleLoad(self.mpath)
    def save(self):
        pickleDump(self,self.mpath)
    


class House:
    def __init__(self,hpath,name='a house',init=False):
        self.hpath=hpath
        if init:
            self.init()
        else:
            self.load();
        self.name=name
    def __str__(self):
        s='<house object: %s >--<value: %s>'%(self.name,self.dic)
        return s
    def init(self):
        self.dic=InfoBody()
        self.save()
    
    @preload
    def __getitem__(self,key):
        return self.dic[key]
    @preload
    def __setitem__(self,key,value):
        self.dic[key]=value
        self.save()
    @preload
    def delete(self,k):
        del self.dic[k]
        self.save()
    @preload
    def set(self,k,obj):
        self.dic[k]= obj
        self.save()

    def load(self):
        self.dic=jsonLoad(self.hpath)
    def save(self):
        jsonDump(self.dic,self.hpath)

def tlog(*args,**kwargs):
    try:
        if TEST_MODE:
            return log(*args,**kwargs)
    except:
        print('********warning , "TEST_MODE" is not setted in the module, which is needed to run "tlog()" ')


