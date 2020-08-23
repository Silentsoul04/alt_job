import scrapy
import urllib
from bs4 import BeautifulSoup
from .base import Scraper
from ..items import Job

class Scraper_goodwork_ca(Scraper):
    name = "goodwork.ca"
    allowed_domains = ["webcache.googleusercontent.com", name]

    def get_jobs_list(self, response):
        # HTML <ul> contains all li of postings
        return response.xpath('//*[@id="page"]/div[contains(@class,"listingthumb row")]')

    def get_job_dict(self, selector):
        return {
            'url':urllib.parse.urljoin('http://goodwork.ca/', selector.xpath('div[1]/span/a/@href').get()),
            'title':selector.xpath('div[1]/span/a').css('::text').get()
        }

    def parse_full_job_page(self, response, job_dict):
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
        next_link=[a.xpath('@href').get() for a in response.xpath('//*[@id="page"]/p/a') if 'Next' in a.css('::text').get() ]
        if len(next_link)==1:
            return urllib.parse.urljoin('http://goodwork.ca/', next_link[0])
        else:
            return None

    # TODO parse search form: http://fr.goodwork.ca/search
    # Add theme, province, city/town(s), country, job type, other options, keyword 
    # As config [goodwork.ca] values