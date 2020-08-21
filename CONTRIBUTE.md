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
The new Scraper must extend `alt_job.scrapers.Scraper` which extends `scrapy.Spider`.  
Read carefully the [template Scraper class](https://github.com/tristanlatr/alt_job/blob/master/alt_job/scrapers/__init__.py).  
Fork the repo, hack hack hack and Pull request.  

Easy !

**A scraper looks like this:**

```python
from bs4 import BeautifulSoup
import alt_job.scrapers
from alt_job.jobs import Job

class Scraper_arrondissement_com(alt_job.scrapers.Scraper):
    name = "arrondissement.com"
    allowed_domains = ["webcache.googleusercontent.com", name]
    
    def get_jobs_list(self, response):
        # HTML <div class="listing"> contains all dic of postings
        return response.xpath('//div[contains(@class,"listing")]/div')

    def get_job_dict(self, selector):
        return {
            'url':selector.xpath('a/@href').get(),
            'date_posted':selector.xpath('text()').get(),
            'organisation':selector.xpath('a[@class="fromDirLink"]/text()').get(),
            'title':selector.xpath('a[@class="title"]/text()').get()
        }

    def parse_full_job_page(self, response, job_dict):
        job_dict['description']=BeautifulSoup(response.xpath('//div[@id="fiche"]/div[contains(@class,"publication")]').get()).get_text()
        job_dict['apply_before']=response.xpath('//*[@id="fiche"]/div[2]/div[2]/div[6]/text()').get()
        job_dict['job_type']=response.xpath('//*[@id="fiche"]/div[2]/div[2]/div[4]/text()').get()
        job_dict['week_hours']=response.xpath('//*[@id="fiche"]/div[2]/div[2]/div[2]/text()').get()
        job_dict['salary']=response.xpath('//*[@id="fiche"]/div[2]/div[2]/div[3]/text()').get()
        return Job(job_dict)

    def get_next_page_url(self, response):
        return response.xpath('//table[contains(@class,"pager-nav")]//tr/td[last()]/a/@href').get()
```


