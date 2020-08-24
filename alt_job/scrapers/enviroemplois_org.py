import urllib
from bs4 import BeautifulSoup
from .base import Scraper
from ..items import Job

# This site seems

class Scraper_enviroemplois_org(Scraper):
    name = "enviroemplois.org"
    allowed_domains = ["webcache.googleusercontent.com", name]
    start_urls = ["https://www.enviroemplois.org/offres-d-emploi?sector=&region=&job_kind=&employer="]
    
    def parse(self, response):
        """
        @auto_url enviroemplois.org
        @returns items 10 10
        @scrape_not_none url title
        """
        return super().parse(response)

    def get_jobs_list(self, response):
        """
        @auto_url enviroemplois.org
        @returns_valid_selectorlist
        """
        return response.xpath('/html/body/main/div[2]/div[2]/div')

    def get_job_dict(self, selector):
        return {
            'url':urllib.parse.urljoin('https://enviroemplois.org/', selector.xpath('div/div[contains(@class,"job-offer-card__footer")]/div[contains(@class,"job-offer-card__actions")]/a/@href').get()),
            'apply_before':selector.xpath('div/div[contains(@class,"job-offer-card__footer")]/div[contains(@class,"job-offer-card__timelimit")]/text()').get().split('Date limite de candidature: ',1)[-1],
            'title':selector.xpath('div/div[contains(@class,"job-offer-card__header")]/div/h2/text()').get(),
            'location':selector.xpath('div/div[contains(@class,"job-offer-card__header")]/div[contains(@class,"job-offer-job-offer-card__filters")]/a[2]/text()').get(),
            'job_type':selector.xpath('div/div[contains(@class,"job-offer-card__header")]/div[contains(@class,"job-offer-job-offer-card__filters")]/a[3]/text()').get()
        }

    def parse_full_job_page(self, response, job_dict):
        """
        @auto_job_url enviroemplois.org
        @scrape_not_none url title description
        @returns items 1 1  
        """
        job_dict['description']=BeautifulSoup(response.xpath('/html/body/main/div[4]/div/div/div[1]').get()).get_text()
        job_dict['week_hours']=response.xpath('/html/body/main/div[4]/div/div/div[1]/div/div[3]/div/span/text()').get() # None sometimes
        job_dict['salary']=response.xpath('/html/body/main/div[4]/div/div/div[1]/div/div[2]/div/span/text()').get() # None sometimes
        return Job(job_dict)

    def get_next_page_url(self, response):
        """
        @auto_url enviroemplois.org
        @returns_valid_link
        """
        return urllib.parse.urljoin('https://enviroemplois.org/', response.xpath('/html/body/main/div[2]/div[3]/div/nav/span[9]/a/@href').get())