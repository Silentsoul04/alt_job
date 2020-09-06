
NAME="aqoci.qc.ca"
START_URL="https://www.aqoci.qc.ca/?-emplois-et-benevolat-"

JOBS_LIST="""//*[@id="contenu-sans-extra"]/div[contains(@class, "emplois")]/ul/li"""

JOB_DICT_TITLE="div/a/text()"
JOB_DICT_ORG="div/small[1]/a/text()"
JOB_DICT_APPLY_BEFORE="div/text()[2]" # TODO . split("Date limite: ")
JOB_DICT_LOCATION="div/small[5]/a/text()"

JOB_DICT_URL="div/a/@href"

JOB_PAGE_TYPE="""//*[@id="contenu"]/div[1]/div[2]/small[3]/a/text()"""
JOB_PAGE_DESCRIPTION="""//*[@id="contenu"]/div[2]/div""" #with bs4

import scrapy
import urllib
from bs4 import BeautifulSoup
from .base import Scraper
from ..items import Job

class Scraper_aqoci_qc_ca(Scraper):
    name = NAME
    allowed_domains = ["webcache.googleusercontent.com", name]
    start_urls = [START_URL]

    def parse(self, response):
        """
        @auto_url aqoci.qc.ca
        @returns items 1
        @scrape_not_none url title organisation apply_before location
        """
        return super().parse(response)

    def get_jobs_list(self, response):
        """
        @auto_url aqoci.qc.ca
        @returns_valid_selectorlist
        """
        return response.xpath(JOBS_LIST)

    def get_job_dict(self, selector):
        # TODO "Date limite" split for "apply_before"
        return {
            'url':urllib.parse.urljoin('http://aqoci.qc.ca/', selector.xpath(JOB_DICT_URL).get()),
            'title':selector.xpath(JOB_DICT_TITLE).get(),
            'organisation':selector.xpath(JOB_DICT_ORG).get(),
            'apply_before':selector.xpath(JOB_DICT_APPLY_BEFORE).get(),
            'location':selector.xpath(JOB_DICT_LOCATION).get()
        }

    def parse_full_job_page(self, response, job_dict):
        """
        @auto_job_url aqoci.qc.ca
        @scrape_not_none url title organisation apply_before location
        @returns items 1 1  
        """
        job_dict['description']=BeautifulSoup(response.xpath(JOB_PAGE_DESCRIPTION).get()).get_text() if response.xpath(JOB_PAGE_DESCRIPTION).get() else None
        job_dict['job_type']=response.xpath(JOB_PAGE_TYPE).get()
        return Job(job_dict)

    # def get_next_page_url(self, response):
    #     """
    #     @auto_url aqoci.qc.ca
    #     @returns_valid_link
    #     """
    #     return None