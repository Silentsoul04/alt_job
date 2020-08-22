import scrapy
import urllib
from .base import Scraper
from ..jobs import Job

class Scraper_cdeacf_ca(Scraper):
    name = "cdeacf.ca"
    allowed_domains = ["webcache.googleusercontent.com", name]
    def get_jobs_list(self, response):
        # HTML <ul> contains all li of postings
        return response.xpath('//div[@id="main-content"]//div[@class="view-content"]/div/ul/li')

    def get_job_dict(self, selector):
        return {
            'url':urllib.parse.urljoin('http://cdeacf.ca/', selector.xpath('div[contains(@class,"views-field-title")]//a/@href').get()),
            'date_posted':selector.xpath('div[contains(@class,"views-field-created")]//span[@class="field-content-inner"]/text()').get(),
            'organisation':selector.xpath('div[contains(@class,"views-field-field-organisme")]//span[@class="field-content"]/text()').get(),
            'title':selector.xpath('div[contains(@class,"views-field-title")]//a/text()').get(),
            'apply_before': selector.xpath('div[9]/span[2]/span/text()').get(),
            'location': selector.xpath('div[8]/span/text()').get()
        }
    
    def get_next_page_url(self, response):
        return response.xpath('//*[@id="block-system-main"]/div/div[2]/ul/li[contains(@class,"pager-next")]/a/@href').get()


