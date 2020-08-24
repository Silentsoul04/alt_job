
import scrapy
from bs4 import BeautifulSoup
from .base import Scraper
from ..items import Job

class Scraper_engages_ca(Scraper):
    name = "engages.ca"
    allowed_domains = ["webcache.googleusercontent.com", name]
    start_urls = ["https://www.engages.ca/emplois"]

    def parse(self, response):
        """
        @auto_url engages.ca
        @returns items 1
        @scrape_not_none url title organisation location job_type
        """
        return super().parse(response)

    def get_jobs_list(self, response):
        """
        @auto_url engages.ca
        @returns_valid_selectorlist
        """
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
        """
        @auto_job_url engages.ca
        @cb_kwargs {"job_dict":{"url":"https://...", "title":"Job title"}}
        @scrape_not_none url title description date_posted
        @returns items 1 1  
        """
        job_dict['description']=BeautifulSoup(response.xpath('//*[@id="single"]/div[3]').get()).get_text()
        job_dict['date_posted']=response.xpath('//*[@id="single"]/div[1]/span/b/text()').get()
        return Job(job_dict)