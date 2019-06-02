
from .supported_classes import InfoBody
from .table import Table,DBError
import uuid,time
from .utils import log,tlog




class Field(object):
    def __init__(self,name,column_type,primary_key,default,searchable,limit_size):
        self.name=name
        self.column_type=column_type
        self.primary_key=primary_key
        self.default=default
        self.limit_size=limit_size
        self.searchable=searchable
    def __str__(self):
        return '<%s,%s:%s>'%(self.__class__.__name__,self.column_type,self.name)

class StringField(Field):
    def __init__(self,name=None,primary_key=False,default='',searchable=True,limit_size=None):
        super().__init__(name,'string',primary_key,default,searchable,limit_size)

class IntegerField(Field):
    def __init__(self,name=None,primary_key=False,default=None,searchable=True,limit_size=None):
        super().__init__(name,'integer',primary_key,default,searchable,limit_size)

class FloatField(Field):
    def __init__(self,name=None,primary_key=False,default=None,searchable=True,limit_size=None):
        super().__init__(name,'float',primary_key,default,searchable,limit_size)

class TextField(Field):
    def __init__(self,name=None,primary_key=False,default=None,searchable=True,limit_size=None):
        super().__init__(name,'text',primary_key,default,searchable,limit_size)

class BooleanField(Field):
    def __init__(self,name=None,primary_key=False,default=False,searchable=True,limit_size=None):
        super().__init__(name,'booleans',primary_key,default,searchable,limit_size)
class ObjectField(Field):
    def __init__(self,name=None,primary_key=False,default=False,searchable=True,limit_size=None):
        super().__init__(name,'object',primary_key,default,searchable,limit_size)

class ModelMetaclass(type):
    '''
        fields.
    '''
    def __new__(cls, name,bases,attrs):
        if name=='Model':
            return type.__new__(cls,name,bases,attrs)
        tableName=attrs.get('__table__',None) or name
        print('Found model:%s (table : %s)'%(name,tableName))   
        fields=dict()
        all_keys = []
        primaryKey = None
        searchable_keys=[]
        base_fields={}
        base_name=bases[0].__name__
        for base in bases:
            if  hasattr(base,'__fields__') :
                if '__fields__' in base.__fields__.keys():
                    base_fields=base.__fields__['__fields__']
                    while(1):
                        if '__fields__' in base_fields.keys():
                            base_fields=base_fields['__fields__'] 
                        else:
                            break
                    base.__fields__=base_fields
                else:
                    base_fields=base.__fields__
                # print('extending attrs from base %s:'%base,base_fields.keys())
                break
            break
        base_fields.update(attrs)
        attrs=base_fields
        for k,v in attrs.items():
            # 收集主键和键
            if isinstance(v,Field):
                # print('Found mapping :%s==>%s'%(k,v))
                v.name=k  ## in case that v has not been given a name.
                if v.searchable:
                    searchable_keys.append(k)
                fields[k]=v
                if v.primary_key:
                    # 找到主键
                    if primaryKey:
                        raise RuntimeError('Duplicate primary key for %s'%k)
                    primaryKey=k
                all_keys.append(k)
        if not primaryKey:
            log(bases[0])
            raise RuntimeError('Primary key not found.')
        for k in fields.keys():
            attrs.pop(k)
        
        attrs['__fields__']=fields
        attrs['__table__']=tableName
        attrs['__primary_key__']=primaryKey
        attrs['__searchable_keys__']=searchable_keys
        attrs['__all_keys__']=all_keys
        new_class=type.__new__(cls,name,bases,attrs)
        return new_class


class Model(InfoBody,metaclass=ModelMetaclass):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
    def _checkDefault(self):
        self.checkAllFieldsByDefault()
    def checkDefault(self):
        self.checkAllFieldsByDefault()
    def getValue(self,key):
        return getattr(self,key,None)
    def checkAllFieldsByDefault(self):
        for key in self.__all_keys__:
            self.getValueOrDefault(key)
    def getValueOrDefault(self,key):
        value=self.__getattr__(key,None)
        if value is None:
            try:
                field=self.__fields__[key]
            except KeyError:
                return value
            if field.default is not None:
                value=field.default() if callable(field.default) else field.default
                log(r'Set default value for %s: %s'%(field.name,value))
            setattr(self,key,value)    ##仅当default 不为 None 时才将该字段设置为属性，否则不能！！！
        return value


#------------------------------------------------------------
#------------------------------------------------------------

class DefaultTableClass(InfoBody,metaclass=ModelMetaclass):
    id=StringField(primary_key=True,default=time.time)





#------------------------------------------------------------
#------------------------------------------------------------


