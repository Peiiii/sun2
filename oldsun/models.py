
from utils.piudb2 import *
import utils.piudb2.models.blogsite as blogsite
import config
class Blog(blogsite.Blog):
    pass
class User(blogsite.User):
    pass
class Comment(blogsite.Comment):
    pass

def initDB():
        if existsDB(config.dbpath):    
            return
        db=createDB(config.dbpath)
        db.createTable(name='blogs',cls=Blog)
        db.createTable(name='users',cls=User)
        db.createTable(name='comments',cls=Comment)
def getDB():
    db=loadDB(config.dbpath)
    cotb=db.pable(name='comments',cls=Comment)
    bltb=db.pable(name='blogs',cls=Blog)
    urtb=db.pable(name='users',cls=User)
    myho=db.houses['myhouse']
    mydb=InfoBody(
        db=db,bltb=bltb,urtb=urtb,cotb=cotb,myho=myho
    )
    return mydb
if __name__=="__main__":
    initDB()
    # db=loadDB(config.dbpath)
    pass
    