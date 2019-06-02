import os
class PathType:
    def __init__(self):
        self.F = 'FILE'
        self.D = 'DIR'
        self.L = 'LINK'
        self.M = 'MOUNT'


T = PathType()


class Path:
    def __init__(self, path):
        self.path = path
        self.epath = self.encodePath()
        self.name = os.path.basename(path)
        self.size = os.path.getsize(path)
        self.atime = formatTime(os.path.getatime(path))
        self.ctime = formatTime(os.path.getctime(path))
        self.mtime = formatTime(os.path.getmtime(path))
        self.type = self.getType()

    def getType(self):
        if os.path.isdir(self.path):
            return T.D
        if os.path.isfile(self.path):
            return T.F
        if os.path.islink(self.path):
            return T.L
        if os.path.ismount(self.path):
            return T.M

    def encodePath(self):
        return self.path.replace('/', '%2F')

    def children(self):
        if self.type == T.D:
            list = self.listdir()
            return [Path(i) for i in list]

    def getContent(self):
        if self.type == T.F:
            return loadText(self.path)

    def listdir(self):
        if self.type == T.D:
            l = os.listdir(self.path)
            return [self.path + '/' + i for i in l]

    def fileChildren(self):
        list = self.children()
        return [i for i in list if i.type == T.F]

    def dirChildren(self):
        list = self.children()
        return [i for i in list if i.type == T.D]

    def linkChildren(self):
        list = self.children()
        return [i for i in list if i.type == T.L]

    def mountChildren(self):
        list = self.children()
        return [i for i in list if i.type == T.M]
    def toJson(self):
        return self.__dict__
    def addContent(self):
        self.content=self.getContent()

