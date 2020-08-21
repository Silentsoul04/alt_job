import scrapy
from bs4 import BeautifulSoup
import alt_job.scrapers
from alt_job.jobs import Job

class Scraper_chantier_qc_ca(alt_job.scrapers.Scraper):
    name = "chantier.qc.ca"
    allowed_domains = ["webcache.googleusercontent.com", name]

    def get_jobs_list(self, response):
        # HTML <ul> contains all li of postings
        return response.xpath('//*[@id="menu_ajax_gris"]/div[@class="ajax_menu_nav"]/a')

    def get_job_dict(self, selector):
        return {
            'url':selector.xpath('@href').get(),
            'title':selector.xpath('div/h3/text()').get()
        }

    def parse_full_job_page(self, response, job_dict):
        job_dict['description']=BeautifulSoup(response.xpath('//*[contains(@id,"single-post")]').get()).get_text()
        job_dict['organisation']=response.xpath('//*[contains(@id,"single-post")]/div[3]/strong[1]/text()').get()
        job_dict['date_posted']=response.xpath('//*[contains(@id,"single-post")]/div[1]/text()[1]').get(), 
        job_dict['apply_before']=response.xpath('//*[contains(@id,"single-post")]/div[3]/strong[3]/text()').get(),
        job_dict['location']=response.xpath('//*[contains(@id,"single-post")]/div[3]/strong[2]/text()').get()
        return Job(job_dict)