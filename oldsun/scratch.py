
from utils.piudb2 import createDB,DB,loadDB,existsDB
import utils.piudb2.models as dbmodels
# import utils.piudb2.basic_models as basic_models
from utils.piudb2.basic_models import *
# from utils.mydb import TableManager




def test1():
    blogs = tb1._findAll_()
    [print(i.title) for i in blogs]
    for b in blogs:
        dic={}
        for k in b.__fields__:
            dic[k]=b.get(k)
        b2=Blog2(**dic)
        tb2._insert_(b2)
def test2():
    global tb2
    a=tb2._insert_(Blog(title='hu'))
    print(a)
    blogs=tb2._findAll_()
    [print(i.title) for i in blogs]
    print(tb2.tb.map.dic)
    tb2=Piu(test_dir,Blog)
    print(tb2.tb.map.dic)

Blog=dbmodels.Blog
# Comment1=dbmodels.Comment
# User=dbmodels.User
class Comment(dbmodels.Comment):
    id=StringField(primary_key=True,default=dbmodels.next_id)
class User(dbmodels.User):
    id=StringField(primary_key=True,default=dbmodels.next_id)
def initdb():
    db=createDB(dbpath='./testdb')
    db.createTable(name='comments',cls=Comment)
    db.createTable(name='blogs',cls=Blog)
    db.createTable(name='users',cls=User)
    ho=db.houses['myhouse']
from utils.piudb2.utils import jsonLoad,jsonDump
from models import getDB
def do1():
    import os
    blog_dir='data/json/articles'
    
    db=getDB()
    for a in os.listdir(blog_dir):
        path=blog_dir+'/'+a
        ar=jsonLoad(path)
        b=Blog(ar)
        db.bltb._upsert_(b)
def rm():
    db=getDB()
    bs=db.bltb._select_(selected_keys=['id','created_at','date'])
    for b in bs:
        print(b)
        if b.date=='' or int(b.date[-2:])<21 :
            db.bltb._delete_(b.id)
if __name__ == "__main__":
    pass
    # do1()
    # rm()



    #--------------------------------