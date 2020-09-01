import urllib.parse
from bs4 import BeautifulSoup
# from scrapy.http import Request
from .base import Scraper
from ..items import Job

class Scraper_charityvillage_com(Scraper):
    """Enforce use_selenium=True because website require javascript"""

    name = "charityvillage.com"
    allowed_domains = ["webcache.googleusercontent.com", name]
    start_urls=['https://charityvillage.com/search/#results/5f4583ff061c57fc640eb1dc?job_type=-Unpaid+Volunteer+Position&page_num=1&kw=']

    def __init__(self, *args, **kwargs):
        kwargs['use_selenium']=True
        super().__init__(*args, **kwargs)
        
    def parse(self, response):
        """
        @with_selenium
        @auto_url charityvillage.com
        @returns items 20 20
        @scrape_not_none url title date_posted apply_before organisation location
        """
        return super().parse(response)
    
    def get_jobs_list(self, response):
        """
        @with_selenium
        @auto_url charityvillage.com
        @returns_valid_selectorlist
        """
        return response.xpath('//ul[contains(@class,"job-search-results")]/li')

    def get_job_dict(self, selector):
        return {
            'url':selector.xpath('div/div[contains(@class, "cl-job-cta")]/a/@href').get(), 
            'date_posted':selector.xpath('div/div[contains(@class, "cl-job-info-cont")]/div[contains(@class, "cl-job-dates")]/span[1]/text()').get().split("Published: ",1)[-1],
            'apply_before':selector.xpath('div/div[contains(@class, "cl-job-info-cont")]/div[contains(@class, "cl-job-dates")]/span[2]/text()').get().split("Expiry: ",1)[-1],
            'organisation':selector.xpath('div/div[contains(@class, "cl-job-info-cont")]/span[contains(@class, "cl-job-company")]/text()').get(),
            'location':selector.xpath('div/div[contains(@class, "cl-job-info-cont")]/span[contains(@class, "cl-job-location")]/text()').get(),
            'title':selector.xpath('div/div[contains(@class, "cl-job-info-cont")]/a[contains(@class,"cl-job-link")]/h2/text()').get()
        }

    def parse_full_job_page(self, response, job_dict):
        """
        @with_selenium
        @auto_job_url charityvillage.com
        @scrape_not_none url title description organisation date_posted apply_before location
        @returns items 1 1  
        """
        job_dict['description']=BeautifulSoup(response.xpath('//div[contains(@class, "post-content")]').get()).get_text()
        return Job(job_dict)

    def get_next_page_url(self, response):
        """
        @with_selenium
        @auto_url charityvillage.com
        @returns_valid_link
        """
        # The next button doesn't have a href attribute, we need to click it with javascript and extract the page URL
        if 'Next' in response.xpath('//*[@id="cl-jobsearch-results-list"]/div/div[2]/ul/li[last()]/a/text()').get() :
            next_buttons=response.request.meta['driver'].find_elements_by_xpath('//*[@id="cl-jobsearch-results-list"]/div/div[2]/ul/li[last()]/a')
            if len(next_buttons)>0 :
                response.request.meta['driver'].execute_script("arguments[0].click();", next_buttons[0])
            return response.request.meta['driver'].current_url
        else:
            return None
            # # There is another look of the listing page (https://charityvillage.com/jobs)... Wich is not supported.
            # return response.xpath('//ul[contains(@class, "page-numbers")]/li[last()]/a/@href').get()