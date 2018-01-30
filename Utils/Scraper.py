from urllib import request, parse
import gzip
from io import BytesIO
from xml.etree import ElementTree
import json

class Scraper():
  hdr = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate, sdch', 'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4', 'Connection': 'keep-alive', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}

  def __init__(self, url = "", xpath = "", parseFunc = None):
    self.url = url
    self.xpath = xpath
    self.parseFunc = parseFunc
    self.cookieProcessor = request.HTTPCookieProcessor()
    self.opener = request.build_opener(self.cookieProcessor)

  def fetch(self):
    self.req = request.Request(self.url, headers = Scraper.hdr)
    response = self.opener.open(self.req)
    contentType = response.info()['Content-Type']
    encoding = response.info().get('Content-Encoding')
    if encoding != 'gzip' and encoding !=None:
        print('Encoding of {0} is not handled'.format(encoding))
        page = ''
    if (encoding == 'gzip'):
        buf = BytesIO(response.read())
        response = gzip.GzipFile(fileobj = buf)
    if 'json' in contentType:
        page = json.load(response)
    else:
        page = str(response.read())
        if 'html' in page:
            page = page[page.find('<html') : page.find('</html>') + 7]
    return page

  def parse(self):
    if(self.xpath != ""):
        root = ElementTree.fromstring(self.page)
        data = root.findall(self.xpath)
    else:
        data = self.parseFunc(self.page)
    return data

  def getRealTimeData(self):
    self.page = self.fetch()
    self.data = self.parse()
    return self.data
    
  def getCookie(self):
    return self.cookieProcessor.cookiejar
    
  def setCookie(self, cookiejar):
    self.cookieProcessor.cookiejar = cookiejar
    
  def setQuery(self, query):
    self.url = self.url + '?' + parse.urlencode(query)
  

if __name__ == '__main__':
    url1 = 'http://xueqiu.com/'
    url2 = 'https://xueqiu.com/stock/forchartk/stocklist.json'
  
    def parseFunc(instr):
        return instr
  
    S1 = Scraper(url1, parseFunc = parseFunc)
    S1.getRealTimeData()
    cookie = S1.getCookie()
  
    query = {'symbol':'SH600519',
        'period':'1day',
        'type':'before',
        'begin':1508022718363,
        'end':1509022718363,
        '_':1509022718378}
  
    S2 = Scraper(url2, parseFunc = parseFunc)
    S2.setQuery(query)
    S2.setCookie(cookie)
  
    print(S2.getRealTimeData())
