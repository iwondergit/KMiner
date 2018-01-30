from lxml import etree
from Utils.Scraper import Scraper

class HTMLScraper(Scraper):

  def parse(self):
    if(self.xpath != ""):
      tree = etree.HTML(self.page)
      data = tree.xpath(self.xpath)
    else:
      data = self.parseFunc(self.page)
    return data
  

if __name__ == '__main__':
  url = 'http://www.163.com/'
  xpath = '//a[contains(text(),"网易首页")]'
  
  S = HTMLScraper(url, xpath = xpath)
  data = S.getRealTimeData()
  print(data[0].text)
