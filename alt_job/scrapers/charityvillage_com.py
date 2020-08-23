from bs4 import BeautifulSoup
from .base import Scraper
from ..jobs import Job

# class Scraper_charityvillage_com(Scraper):
#     name = "charityvillage.com"
#     allowed_domains = ["webcache.googleusercontent.com", name]
    
#     #TODO Fix, might need to use Selenium driver to run javascript code
#     def get_jobs_list(self, response):
#         return response.xpath('//ul[contains(@class,"job-search-results")]/li')

#     def get_job_dict(self, selector):
#         return {
#             'url':selector.xpath('div/div[contains(@class, "cl-job-cta")]/a/@href').get(), 
#             'date_posted':selector.xpath('div/div[contains(@class, "cl-job-info-cont")]/div[contains(@class, "cl-job-dates")]/span[1]/text()').get().split("Published: ",1)[-1],
#             'apply_before':selector.xpath('div/div[contains(@class, "cl-job-info-cont")]/div[contains(@class, "cl-job-dates")]/span[2]/text()').get().split("Expiry: ",1)[-1],
#             'organisation':selector.xpath('div/div[contains(@class, "cl-job-info-cont")]/span[contains(@class, "cl-job-company")]/text()').get(),
#             'location':selector.xpath('div/div[contains(@class, "cl-job-info-cont")]/span[contains(@class, "cl-job-location)]/text()').get(),
#             'title':selector.xpath('div/div[contains(@class, "cl-job-info-cont")]/a[contains(@class,"cl-job-link")]/h2/text()').get()
#         }

    # def parse_full_job_page(self, response, job_dict):
    #     # job_dict['description']=BeautifulSoup(response.xpath('//div[@id="fiche"]/div[contains(@class,"publication")]').get()).get_text()
    #     # job_dict['apply_before']=response.xpath('//*[@id="fiche"]/div[2]/div[2]/div[6]/text()').get()
    #     # job_dict['job_type']=response.xpath('//*[@id="fiche"]/div[2]/div[2]/div[4]/text()').get()
    #     # job_dict['week_hours']=response.xpath('//*[@id="fiche"]/div[2]/div[2]/div[2]/text()').get()
    #     # job_dict['salary']=response.xpath('//*[@id="fiche"]/div[2]/div[2]/div[3]/text()').get()
    #     return Job(job_dict)

    # def get_next_page_url(self, response):
        # return response.xpath('//table[contains(@class,"pager-nav")]//tr/td[last()]/a/@href').get()