from bs4 import BeautifulSoup
from .base import Scraper
from ..items import Job

class Scraper_arrondissement_com(Scraper):
    name = "arrondissement.com"
    allowed_domains = ["webcache.googleusercontent.com", name]
    # start_urls = ['https://www.arrondissement.com/tout-list-emplois/']

    def parse(self, response):
        """ Contract:  

        @url https://www.arrondissement.com/tout-list-emplois/
        @returns items 15 15
        @parses url title
        """
        return super().parse(response)

    def get_jobs_list(self, response):
        return response.xpath('//div[contains(@class,"listing")]/div')

    def get_job_dict(self, selector):
        return {
            'url':selector.xpath('a/@href').get(),
            'date_posted':selector.xpath('text()').get(),
            'organisation':selector.xpath('a[@class="fromDirLink"]/text()').get(),
            'title':selector.xpath('a[@class="title"]/text()').get()
        }

    def parse_full_job_page(self, response, job_dict):
        """ This parses the full job page

        @url https://web.archive.org/web/20200824020247/https://www.arrondissement.com/tout-get-emplois/t1/u75815-direction-generale-adjointe-organisme-lucratif
        @returns items 1 1  
        """
        job_dict['description']=BeautifulSoup(response.xpath('//div[@id="fiche"]/div[contains(@class,"publication")]').get()).get_text()
        job_dict['apply_before']=response.xpath('//*[@id="fiche"]/div[2]/div[2]/div[6]/text()').get()
        job_dict['job_type']=response.xpath('//*[@id="fiche"]/div[2]/div[2]/div[4]/text()').get()
        job_dict['week_hours']=response.xpath('//*[@id="fiche"]/div[2]/div[2]/div[2]/text()').get()
        job_dict['salary']=response.xpath('//*[@id="fiche"]/div[2]/div[2]/div[3]/text()').get()
        return Job(job_dict)

    def get_next_page_url(self, response):
        return response.xpath('//table[contains(@class,"pager-nav")]//tr/td[last()]/a/@href').get()