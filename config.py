

class Config(dict):
    def __getattr__(self, item):
        try:
            r=self.__getitem__(item)
            return r
        except:
            raise AttributeError('No attribute %s'%item)

dbpath='../db'