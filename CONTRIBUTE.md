**Thank to show interest into contributing to Alt Job.**

If you like the project and think you could help with making it better, there are many ways you can do it:

- Create a new issue for new feature proposal or a bug
- Write a new Scraper
- Implement existing issues 
- Help with improving the documentation
- Set up a demo server
- Spread a word about the project to your friends, blogs or any other channels
- Any other things you could imagine

Any contribution would be of great help and I will highly appreciate it! If you have any questions, please create a new issue, or contact me via trislatr@gmail.com

This Python module is build on top of [Scrapy](https://scrapy.org). If you don't know about it, get familliar with how Scrapy works.

**Writing a new scraper**

The only thing you have to do to support a new website is to drop the the new scraper file in `alt_job/scrapers/` folder.  
The new Scraper must extend `alt_job.scrapers.base.Scraper` which extends `scrapy.Spider`.  
Read carefully the [base Scraper class](https://github.com/tristanlatr/alt_job/blob/master/alt_job/scrapers/base.py).  
Fork the repo, hack hack hack and pull request.  
I recommend [xpath-helper](https://chrome.google.com/webstore/detail/xpath-helper/hgimnogjllphhhkhlmebbmlgjoejdpjl?hl=en) to check the validity of your xpaths.  

Easy !

**A scraper looks like this:**  

This includes automatic docstrings testing, [Contracts](https://docs.scrapy.org/en/latest/topics/contracts.html).  

Run tests with `scrapy check exemple.coma`

```python
import scrapy
import urllib
from bs4 import BeautifulSoup
from .base import Scraper
from ..items import Job

class Scraper_goodwork_ca(Scraper):
    name = "goodwork.ca"
    allowed_domains = ["webcache.googleusercontent.com", name]
    start_urls = ["https://www.goodwork.ca/jobs"]

    def parse(self, response):
        """
        @auto_url goodwork.ca
        @returns items 50 50
        @scrape_not_none url title
        """
        return super().parse(response)

    def get_jobs_list(self, response):
        """
        @auto_url goodwork.ca
        @returns_valid_selectorlist
        """
        # HTML <ul> contains all li of postings
        return response.xpath('//*[@id="page"]/div[contains(@class,"listingthumb row")]')

    def get_job_dict(self, selector):
        return {
            'url':urllib.parse.urljoin('http://goodwork.ca/', selector.xpath('div[1]/span/a/@href').get()),
            'title':selector.xpath('div[1]/span/a').css('::text').get()
        }

    def parse_full_job_page(self, response, job_dict):
        """
        @auto_job_url goodwork.ca
        @scrape_not_none url title description organisation location
        @returns items 1 1  
        """
        job_dict['description']=BeautifulSoup(response.xpath('//*[@id="page"]/div[1]').get()).get_text()
        job_dict['organisation']=response.xpath('//*[@id="page"]/div[1]/div[1]/p[1]/a/text()').get()
        job_dict['location']=response.xpath('//*[@id="page"]/div[1]/div[1]/p[1]/text()[3]').get()
        date=response.xpath('//*[@id="page"]/div[2]/p[2]/small/text()[1]').get()
        if date:
            d_splited = date.split('Date posted:', 1)
            if len(d_splited)>0:
                job_dict['date_posted']=d_splited[1]
        return Job(job_dict)

    def get_next_page_url(self, response):
        """
        @auto_url goodwork.ca
        @returns_valid_link
        """
        next_link=[a.xpath('@href').get() for a in response.xpath('//*[@id="page"]/p/a') if 'Next' in a.css('::text').get() ]
        if len(next_link)==1:
            return urllib.parse.urljoin('http://goodwork.ca/', next_link[0])
        else:
            return None
```