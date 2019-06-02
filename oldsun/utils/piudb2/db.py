from .supported_classes import InfoBody,Rlist,rlist
from .table import Table,House
from .utils import *
from .basic_models import StringField,DefaultTableClass,Model
import os,time,shutil
class DBOperator:
    pass
def existsDB(dbpath):
    mf=DB.mapfilename
    mpath=dbpath+'/'+mf
    if os.path.exists(dbpath) and os.path.exists(mpath):
        return True
    return False
def createDB(dbpath):
    path=dbpath
    mf=DB.mapfilename
    mpath=path+'/'+mf
    if not os.path.exists(path):
        os.makedirs(path)
    mf=InfoBody(tables=[],houses=[])
    jsonDump(obj=mf,fpath=mpath)
    db=DB(dbpath=path)
    db.createHouse('myhouse')
    return db
def loadDB(dbpath):
    return DB(dbpath=dbpath)
class DB:
    mapfilename='mapfile.map'
    def __init__(self,dbpath):
        self.path=dbpath
        self.mpath=self._joinPath(DB.mapfilename)
        self._loadMap()
        self._loadTables()
        self._loadHouses()
    def createTable(self,cls,name=None):
        name =name or cls.__table__
        dic=dict(
            primary_key=cls.__primary_key__,searchable_keys=cls.__searchable_keys__,
            all_keys=cls.__all_keys__,fields=cls.__fields__
        )
        tb=self._createTable(name=name,**dic)
        return tb
    def createRawTable(self,name,primary_key):
        pk_field=StringField()
        dic=dict(
            primary_key=primary_key,searchable_keys=[primary_key],
            all_keys=[primary_key],fields={primary_key:pk_field}
        )
        return self._createTable(name,**dic)
    def _createTable(self,name,**kws):
        tpath=self._joinPath(name)
        kws['tpath']=tpath
        tb=Table._create_whatever(**kws)
        self.map.tables.append(name)
        self._saveMap()
        self.tables[name]=tb
        return tb
    def dropTable(self,name):
        assert name in self.map.tables
        tb=self.tables.pop(name)
        self.map.tables.remove(name)
        self._saveMap()
        shutil.rmtree(self._joinPath(name))
    def pable(self,name,cls,auto_update_fields=True,\
        overwrite_fields=True,delete_fields_ok=False):
        assert name in self.map.tables
        return Piu(
            tpath=self._joinPath(name),cls=cls,auto_update_fields=auto_update_fields,
            overwrite_fields=overwrite_fields,delete_fields_ok=delete_fields_ok
            )
    def createHouse(self,name):
        house=House(self._joinPath(name),name=name,init=True)
        self.map.houses.append(name)
        self._saveMap()
        self.houses[name]=house
        return house
    def dropHouse(self,name):
        assert name in self.map.houses
        ho=self.houses.pop(name)
        self.map.houses.remove(name)
        self._saveMap()
        os.remove(self._joinPath(name))
        return ho
    def _saveMap(self):
        jsonDump(self.map,self.mpath)
    def _joinPath(self,childpath):
        path=self.path+'/'+childpath
        return path
    def _loadMap(self):
        dic=jsonLoad(self.mpath)
        self.map=InfoBody(dic)
    def _loadTables(self):
        tables=InfoBody()
        for t in self.map.tables:
            tb=Table(self._joinPath(t))
            tables[t]=tb
        self.tables=tables
    def _loadHouses(self):
        houses=InfoBody()
        for h in self.map.houses:
            ho=House(self._joinPath(h))
            houses[h]=ho
        self.houses=houses



class Piu:
    def __init__(self,tpath,cls=None,auto_update_fields=False,delete_fields_ok=False,i_am_sure=False,create_force=False,overwrite_fields=False):
        self.tpath=tpath
        self.delete_fields_ok = delete_fields_ok
        self.i_am_sure = i_am_sure
        self.auto_update_fields = auto_update_fields
        self.overwrite_fields = overwrite_fields
        self.create_force = create_force
        self._open(cls)
        if auto_update_fields:
            self._checkFields()
    def _parseClass(self):
        self.fields = self.cls.__fields__
        self.all_keys = self.cls.__all_keys__
        self.searchable_keys = self.cls.__searchable_keys__
        self.primary_key = self.cls.__primary_key__
    def _open(self,cls):
        if Table._existsATable(self.tpath) and not self.create_force:
            if not cls:
                raise Exception('Cannot open an existed table with no class specified.')
            self.cls = cls or DefaultTableClass
            self._parseClass()
            self.tb=Table(self.tpath)
            return

        self.cls = cls or DefaultTableClass
        self._parseClass()
        self.tb=Table._create_whatever(self.tpath,primary_key=self.primary_key,searchable_keys=self.searchable_keys,
                                       fields=self.fields,all_keys=self.all_keys,test_mode=True,create_force=self.create_force
                                       )
    def _checkFields(self):
        tb_fields=self.tb.fields
        cls_fields=self.cls.__fields__
        for k,v in cls_fields.items():
            if not k in tb_fields.keys():
                self.tb._addField(name=k,fdef=v,exist_ok=self.overwrite_fields,searchable=v.searchable)
                tlog('Add new field "%s" to table .'%(k))
        if not self.delete_fields_ok ==True:
            return
        if not self.i_am_sure ==True:
            return
        if self.delete_fields_ok:
            for k in tb_fields.keys:
                if not k in cls_fields:
                    self.tb._deleteField(k)
                    tlog('Delete field "%s" from table.'%k)
    def _objToDic(self,obj):
        dic = {k: v for k, v in obj.items()}
        return dic
    def _checkObj(self,obj):
        obj.checkDefault()
        obj._checkDefault()
        return obj
    async def insert(self, obj):
        return self._insert_(obj)
    def _insert_(self, obj):
        assert isinstance(obj, Model)
        self._checkObj(obj)
        dic = self._objToDic(obj)
        return self.tb._insert_(**dic)
    async def upsert(self,obj):
        return self._upsert_(obj)
    def _upsert_(self,obj):
        dic=self._objToDic(obj)
        return self.tb._upsert_(**dic)
    async def select(self, selected_keys=[], **kws):
        '''  Assume that you only use select when you only need some brief info. '''
        return self._select_(selected_keys=selected_keys, **kws)
    def _select_(self, selected_keys=[], **kws):
        '''  Assume that you only use select when you only need some brief info. '''
        return self.tb._select_(selected_keys=selected_keys, **kws)

    async def updateByPK(self, pk, **kws):
        await self._updateByPK_(pk, **kws)

    def _updateByPK_(self, pk, **kws):
        return self.tb._updateByPK_(pk,**kws)

    async def update(self, kws, where):
        return self._update_(kws, where)

    def _update_(self, kws, where):
       return self.tb._update_(kws=kws,where=where)

    async def delete(self, pk):
        return self._delete_(pk)

    def _delete_(self, pk):
        return self.tb._delete_(pk=pk)

    async def deleteAll(self, **where):
        return self._deleteAll_(**where)

    def _deleteAll_(self, **where):
        return self.tb._deleteAll_(**where)

    async def findAll(self, **kws):
        return self._findAll_(**kws)
        
    @rlist
    def _findAll_(self, **kws):
        records= self.tb._findAll_(**kws)
        objs=[self.cls(**record) for record in records]
        return objs

    async def find(self, **kws):
        return self._find_(**kws)

    def _find_(self, **kws):
        record=self.tb._find_(**kws)
        return self.cls(**record)

    async def findByPK(self, pk):
        return self._findByPK_(pk)

    def _findByPK_(self, pk):
        record=self.tb._findByPK_(pk)
        return self.cls(**record)

    async def existsPK(self, pk):
        return self._existsPK_(pk)

    def _existsPK_(self, pk):
        return self.tb._existsPK_(pk)

    async def exists(self, **kws):
        return self._exists_(**kws)
    def raiseError(self):
        print('flag')
        raise Exception('This is a flag')
    def _exists_(self, **kws):
        '''
            Assume that only one map object is running at one time ,
            which assures the map obj is always identical width the mapfile.
        '''
        return self.tb._exists_(**kws)
