import scrapy
from bs4 import BeautifulSoup
from .base import Scraper
from ..items import Job

class Scraper_chantier_qc_ca(Scraper):
    name = "chantier.qc.ca"
    allowed_domains = ["webcache.googleusercontent.com", name]
    start_urls = ['https://chantier.qc.ca/decouvrez-leconomie-sociale/offres-demploi']

    def parse(self, response):
        """
        @auto_url chantier.qc.ca
        @returns items 1
        @scrape_not_none url title
        """
        return super().parse(response)

    def get_jobs_list(self, response):
        """
        @auto_url chantier.qc.ca
        @returns_valid_selectorlist
        """
        # HTML <ul> contains all li of postings
        return response.xpath('//*[@id="menu_ajax_gris"]/div[@class="ajax_menu_nav"]/a')

    def get_job_dict(self, selector):
        return {
            'url':selector.xpath('@href').get(),
            'title':selector.xpath('div/h3/text()').get()
        }

    def parse_full_job_page(self, response, job_dict):
        """
        @auto_job_url chantier.qc.ca
        @cb_kwargs {"job_dict":{"url":"https://...", "title":"Job title"}}
        @scrape_not_none url title description organisation date_posted apply_before location
        @returns items 1 1  
        """
        job_dict['description']=BeautifulSoup(response.xpath('//*[contains(@id,"single-post")]').get()).get_text()
        job_dict['organisation']=response.xpath('//*[contains(@id,"single-post")]/div[3]/strong[1]/text()').get()
        job_dict['date_posted']=response.xpath('//*[contains(@id,"single-post")]/div[1]/text()[1]').get(), 
        job_dict['apply_before']=response.xpath('//*[contains(@id,"single-post")]/div[3]/strong[3]/text()').get(),
        job_dict['location']=response.xpath('//*[contains(@id,"single-post")]/div[3]/strong[2]/text()').get()
        return Job(job_dict)