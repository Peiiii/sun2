

from bs4 import BeautifulSoup
import requests,os
def log(*args, num=20, str='*'):
    print(str * num, end='')
    print(*args, end='')
    print(str * num)
class InfoBody(dict):
    def __getattr__(self, item):
        try:
            return self[item]
        except:
            raise Exception('InfoBody object has no attribute %s'%item)
    def __setattr__(self, key, value):
        self[key]=value
class Site:
    def __init__(self,base_rul='https://www.nfcmag.com'):
        self.base_url=base_rul
        self.page_urls=['https://www.nfcmag.com/category/10.html']
        self.articles_dir='data/articles'
        self.article_hrefs=self.getArticleHrefs()
        self.articles=self.getAllArticles()
        self.saveArticles()
    def getArticleHrefs(self):
        links=[]
        for url in self.page_urls:
            links+=Page(url).hrefs
        links=list(set(links))
        links=[self.getFullHref(href) for href in links]
        return links
    def getFullHref(self,href):
        return self.base_url+href
    def getAllArticles(self):
        articles=[]
        for href in self.article_hrefs:
            article=self.getArticleContent(href)
            if article:
                articles.append(article)
        return articles
    def getArticleContent(self,url):
        r=requests.get(url)
        bs=BeautifulSoup(r.text)
        article=bs.find(class_='article-content-box')
        if(not article):
            log('article not found: %s'%url)
            return
        title=article.find(class_='subject').text
        intro=article.find(class_='intro').text
        info=article.find(class_='info').text
        content=article.find(class_='content').text
        return InfoBody(
            title=title,intro=intro,info=info,content=content
        )
    def saveArticles(self):
        for a in self.articles:
            self.saveArticle(a)
    def saveArticle(self,article):
        filename=self.articles_dir+os.sep+article.title+'.txt'
        divider='<$$$$$>'
        text=divider.join([article.title,article.intro,article.info,article.content])
        self.writeFile(filename,text)
    def writeFile(self,fpath,content):
        f=open(fpath,'wb')
        f.write(content.encode('utf-8'))
        f.close()




class Page:
    def __init__(self,url):
        self.url=url
        self.r=requests.get(self.url)
        self.bs=BeautifulSoup(self.r.text)
        self.hrefs=self.getHrefs()
    def getHrefs(self):
        def is_article_link(tag):
            if(not tag.name=='a'):
                return False
            return True
        article_items=self.bs.find_all(class_='article-items')
        links=[]
        for i in article_items:
            try:
                link=i.a
                links.append(link.attrs['href'])
            except:
                pass
        return links

def makeArticles():
    base_url = 'https://www.nfcmag.com'
    url='https://www.nfcmag.com/category/10.html'
    site=Site(base_url)

if __name__=="__main__":
    makeArticles()