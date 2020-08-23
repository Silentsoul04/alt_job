import urllib
from bs4 import BeautifulSoup
from .base import Scraper
from ..jobs import Job

# This site seems

class Scraper_enviroemplois_org(Scraper):
    name = "enviroemplois.org"
    allowed_domains = ["webcache.googleusercontent.com", name]
    
    def get_jobs_list(self, response):
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
        job_dict['description']=BeautifulSoup(response.xpath('/html/body/main/div[4]/div/div/div[1]').get()).get_text()
        job_dict['week_hours']=response.xpath('/html/body/main/div[4]/div/div/div[1]/div/div[3]/div/span/text()').get()
        job_dict['salary']=response.xpath('/html/body/main/div[4]/div/div/div[1]/div/div[2]/div/span/text()').get()
        return Job(job_dict)

    def get_next_page_url(self, response):
        return response.xpath('/html/body/main/div[2]/div[3]/div/nav/span[9]/a/@href').get()