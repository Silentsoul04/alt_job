import abc
import re
import scrapy
import alt_job
import alt_job.db
import alt_job.scrape
from alt_job.jobs import Job

class Scraper(abc.ABC, scrapy.Spider):
    """
    Base class for all scrapers.  
    Include: 
    - a template method parse()
    - abstarct methods that must be rewrote by subclasses.  
            - get_jobs_list(response)
            - get_job_dict(selector)
    """
    # Sub classes must overwrite the 'name' and 'allowed_domains' constant
    # All supported domains
    allowed_domains = ["webcache.googleusercontent.com"]
    

    # TODO use google cache by default and retry request with rela site if website snapshot is older than X hours
    def start_requests(self):
        url=self.url
        if self.use_google_cache:
            url='https://webcache.googleusercontent.com/search?q=cache:{}'.format(self.url)
        yield scrapy.Request(url, callback=self.parse )

    def __init__(self, url, regex=None, parse_full_job_page=False, use_google_cache=False, db=None, turn_listing_pages=False):
        self.url=url
        self.regex=regex
        self.call_parse_full_job_page=parse_full_job_page
        self.use_google_cache=use_google_cache
        self.db=db
        self.turn_listing_pages=turn_listing_pages

    def parse(self, response):
        """
        Template method for all scrapers. Do NOT re write this method.  
        Return a generator iterable for parsed jobs (Job objects).  
        This method is called automatically by scrapy buring the scrape process.  
        """
        page_jobs=[]
        for div in self.get_jobs_list(response):
            # At least url, title data is loaded from the list of job posting ...
            job_dict=self.get_job_dict(div)
            if not job_dict['url'] or not job_dict['title'] :
                raise ValueError("Could not find valid job information ('url' and 'title') in data:\n"+str(div.get())+"\nScraped infos:\n"+str(job_dict)+"\nReport this issue on github!")
            # Store source as the name of the spider aka website
            job_dict['source']=self.name
            page_jobs.append(job_dict)
            # Load job page only if:
            # it's a new job (not in database)
            # and parse_full_job_page=Yes
            # and the method parse_full_job_page() has been re-wrote by the Scraper subclass
            if ( (not self.db or self.db.find_job(job_dict)==None)
                and self.call_parse_full_job_page 
                and type(self).parse_full_job_page != Scraper.parse_full_job_page) :
                # then parse_full_job_page is called with url of the full job post
                yield response.follow(job_dict['url'], 
                    callback=self.parse_full_job_page, # Parse all other data (optionnal)
                    cb_kwargs=dict(job_dict=job_dict))
            else:
                yield Job(job_dict)
        
        # If all page jobs are new and 
        # The method get_next_page_url() has been re-wrote by the Scraper subclass
        # Scrape next page
        if ( self.turn_listing_pages==True 
            and not any([self.db.find_job(job_dict)!=None for job_dict in page_jobs]) 
            and type(self).get_next_page_url != Scraper.get_next_page_url) :
            yield response.follow(self.get_next_page_url(response), callback=self.parse)
    
    @abc.abstractmethod
    def get_jobs_list(self, response):
        """
        Scrapers must re write this method.  

        Arguments:  
        - response: scrapy response object for the listing page
        
        Must return a SelectorList.  
        The result will be automatically iterated in `Scraper.parse()` method.  
        The items will be passed to `Scraper.get_job_dict()`.
        """
        pass

    @abc.abstractmethod
    def get_job_dict(self, selector):
        """
        Scrapers must re write this method.  

        Arguments:  
        - selectorlist: selectorlist object of the job posting in the listing  

        Must return a dict {'url':'https://job-url' , 'title':'Job title', 'organisation':'My community' [...] }

        The dict must at least contain : url, title and organisation. The rest of the Job fields are optionnal but recommended
        """
        pass

    def parse_full_job_page(self, response, job_dict):
        """
        Scrapers can re write this method. 
        This method must be re-wrote to use Scraper(parse_full_job_page=True)

        Arguments:  
        - response: scrapy response object for the job page 
        - job_dict: dict containing job raw data,  
            this function must return a new Job() with this  
            data and any other relevant info from url  

        This method is called by `Scraper.parse()` method if parse_full_job_page==True  
        Must return a Job()  

        """
        return Job(job_dict)

    def get_next_page_url(self, response):
        """
        Scrapers can re write this method. 
        This method must be re-wrote to use Scraper(turn_listing_pages=True)

        Arguments:  
        - response: scrapy response object for the listing page

        This method is called by `Scraper.parse()` method if turn_listing_pages==True  
        Must return a URL string  
        """
        return None