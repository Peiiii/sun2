import json,pickle,os,shutil

def jsonDump(obj,fpath):
        f=open(fpath,'w')
        json.dump(obj,f)
        f.close()
def jsonLoad(fpath):
        with open(fpath,'r') as f:
            dic=json.load(f)
            return dic

##---------------------------------- Supportive functions---------------------

def pickleDump(obj,fpath):
    f=open(fpath,'wb')
    pickle.dump(obj,f)
    f.close()
def pickleLoad(fpath):
    f=open(fpath,'rb')
    try:
        obj=pickle.load(f)
    except:
        print(fpath)
        raise
    return obj

def tlog(*args,**kwargs):
    try:
        if TEST_MODE:
            return log(*args,**kwargs)
    except:
        print('********warning , "TEST_MODE" is not setted in the module, which is needed to run "tlog()" ')
def log(*args, num=20, str='*'):
    print(str * num, end='')
    print(*args, end='')
    print(str * num)