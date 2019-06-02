import json,pickle,time,os,uuid,hashlib,shutil,re

def writeJsonFile(obj,fpath):
    with open(fpath,'w') as f:
        json.dump(obj,f)
def loadJsonFile(fpath):
    with open(fpath,'r') as f:
        obj=json.load(f)
    return obj
def writeTextFile(fn, s, encoding='utf-8'):
    f = open(fn, 'wb')
    a = f.write(bytes(s, encoding=encoding))
    f.close()
    return a


def loadTextFile(file):
    import chardet
    f = open(file, 'rb')
    text = f.read()
    f.close()
    encoding = chardet.detect(text)['encoding']
    if text:
        text = text.decode(encoding=encoding)
    else:
        text = ''
    return text

def forceRemoveDir(fpath):
    shutil.rmtree(fpath)

def formatTime( t):
    t = time.localtime(t)
    return time.strftime('%Y/%m/%d  %H:%M:%S', t)

def encrypt(*args):
    text=':'.join(args)
    encrypted=hashlib.sha1(text.encode('utf-8')).hexdigest()
    return encrypted
def textToHTML(text):
    text,dic=renderDocument(text)
    format=dic.get('format',None)
    format=format or 'text/plain'

    if format=='text/plain' :
        text=text.split('\n')
        new_text = []
        for i in text:
            new_text.append('<p>' + i + '</p>')
        return '\n'.join(new_text)
    elif format=='md' or format=='markdown':
        return mdToHTML(text)
def textToDic(text,divider=';',equal_char='='):
    text=text.strip().strip(divider)
    fields=text.split(divider)
    dic={}
    for f in fields:
        [name,value]=f.strip().split(equal_char)
        name=name.strip()
        value=value.strip()
        dic[name]=value
    return dic
def getHeadAndBody(text):
    text=text.strip()
    pat=re.compile('^/\*.*\*/',re.DOTALL)
    m=re.match(pat,text)
    if not m:
        return None,text
    body=re.sub(pat,'',text,count=1).strip()
    head=m.group(0).strip('/*').strip('*/')
    return head,body

from markdown import markdown
def mdToHTML(md):
    md=markdown(md)
    return md
def renderDocument(text):
    head,body=getHeadAndBody(text)
    if not head:
        return body,{}
    dic=textToDic(head)
    return body,dic

