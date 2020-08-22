
import scrapy
from bs4 import BeautifulSoup
from .base import Scraper
from ..jobs import Job

class Scraper_engages_ca(Scraper):
    name = "engages.ca"
    allowed_domains = ["webcache.googleusercontent.com", name]

    def get_jobs_list(self, response):
        # HTML <section> contains all li of postings
        return response.xpath('//*[@id="content"]/div/div/div[1]/section/div/article')

    def get_job_dict(self, selector):
        return {
            'url':selector.xpath('div/div/h3/a/@href').get(),
            'title':selector.xpath('div/div/h3/a/text()').get(),
            'organisation':selector.xpath('div/div/div/a/text()').get(),
            'location':selector.xpath('div/div/div/text()').get(),
            'job_type':selector.xpath('div/div/div/span[2]/text()').get()
        }

    def parse_full_job_page(self, response, job_dict):
        job_dict['description']=BeautifulSoup(response.xpath('//*[@id="single"]/div[3]').get()).get_text()
        job_dict['date_posted']=response.xpath('//*[@id="single"]/div[1]/span/b/text()').get()
        return Job(job_dict)