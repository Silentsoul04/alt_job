import abc
import re
import scrapy
from ..items import Job
from ..utils import log

class Scraper(abc.ABC, scrapy.Spider):
    """
    Base class for all scrapers.  
    Include: 
    - a template method parse()
    - abstarct methods that must be rewrote by subclasses.  
            - get_jobs_list(response)
            - get_job_dict(selector)
    - abstarct methods that can be rewrote by subclasses to implement full features
            - parse_full_job_page()
            - get_next_page_url()

    Sub classes must overwrite the 'name' and 'allowed_domains', 'start_urls' constants
        "webcache.googleusercontent.com" should be included in allowed_domains
    """

    allowed_domains = ["webcache.googleusercontent.com"]
    start_urls=[]
    name=None

    # TODO use google cache by default and retry request with real site if website snapshot is older than 24 hours
    def start_requests(self):
        for url in self.start_urls:
            if self.use_google_cache:
                url='https://webcache.googleusercontent.com/search?q=cache:{}'.format(url)
            # Allow loading options to be set by cb_kwargs too fo better testing with scrapy contrats
            yield scrapy.Request(url, callback=self.parse )

    def __init__(self, url=None, start_urls=None, 
        use_google_cache=False, db=None, load_full_jobs=False, load_all_new_pages=False):

        self.start_urls=[url] if url else start_urls if start_urls else type(self).start_urls
        self.db=db
        self.use_google_cache=use_google_cache
        self.load_full_jobs=load_full_jobs
        self.load_all_new_pages=load_all_new_pages

    def parse(self, response):
        """
        Template method for all scrapers.  
        Return a generator iterable for parsed jobs (Job objects).  
        This method is called automatically by scrapy buring the scrape process.  
        TODO: User global log handler instead of print, find the issue why log isn't working 
        """
        page_jobs=[]
        jobs_div_list=self.get_jobs_list(response)
        for div in jobs_div_list:
            # At least url, title data is loaded from the list of job posting ...
            job_dict=self.get_job_dict(div)
            if not job_dict['url'] or not job_dict['title'] :
                raise ValueError( "Could not find valid job information ('url' and 'title') in data:\n" + 
                        str(div.get()) + "\nScraped infos:\n" + str(job_dict) + "\nReport this issue on github!" )
            
            # Store source as the name of the spider aka website
            job_dict['source']=self.name
            page_jobs.append(job_dict)
            
            """
            Load full job page only if:
            - it's a new job (not in database)
            - load_full_jobs=Yes
            - the method parse_full_job_page() has been re-wrote by the Scraper subclass
            """
            if ( (not self.db or self.db.find_job(job_dict)==None)
                and self.load_full_jobs ):
                if type(self).parse_full_job_page != Scraper.parse_full_job_page:
                    # then load_full_jobs is called with url of the full job post
                    yield response.follow(job_dict['url'], 
                        callback=self.parse_full_job_page, # Parse all other data (optionnal)
                        cb_kwargs=dict(job_dict=job_dict))
                else:
                    yield Job(job_dict)
            else:
                yield Job(job_dict)

        # Just printing
        if self.load_full_jobs:
            if type(self).parse_full_job_page == Scraper.parse_full_job_page:
                if self.load_all_new_pages==False:
                    print("Scraped {} jobs from {}. Scraper {} does not support load_full_jobs=True and load_all_new_pages=False, some new job postings and job informations might be missing".format(len(page_jobs), response.url, self.name))
                else:
                    print("Scraped {} jobs from {}. Scraper {} does not support load_full_jobs=True, some informations might be missing".format(len(page_jobs), response.url, self.name))
            else:
                print("Scraping {} jobs from {}...".format(len(page_jobs), response.url))
        else:
            if self.load_all_new_pages==False:
                print("Scraped {} jobs from {}. load_all_new_pages=False and load_full_jobs=False, some new job postings and job informations might be missing".format(len(page_jobs), response.url))
            else:
                print("Scraped {} jobs from {}. load_full_jobs=False, some informations might be missing".format(len(page_jobs), response.url))
       
        """
        If all page jobs are new and 
        The method get_next_page_url() has been re-wrote by the Scraper subclass
        Scrape next page
        """
        if self.load_all_new_pages==True:
            if self.db and any( [self.db.find_job(job_dict)!=None for job_dict in page_jobs] ):
                # All new job postings loaded
                pass
            else:
                if self.get_next_page_url(response)!=None :
                    # Loading next page...
                    yield response.follow(self.get_next_page_url(response),
                        callback=self.parse)
                else:
                    if type(self).get_next_page_url != Scraper.get_next_page_url:
                        # Last page loaded
                        pass
                    else:
                        print("Scraper {} does not support load_all_new_pages=True, some new job postings might be missing".format(self.name))

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

        The dict must at least contain : url and title. The rest of the Job fields are optionnal but recommended
        """
        pass

    def parse_full_job_page(self, response, job_dict):
        """
        Scrapers can re write this method. 
        This method must be re-wrote to use Scraper(load_full_jobs=True)

        Arguments:  
        - response: scrapy response object for the job page 
        - job_dict: dict containing job raw data,  
            this function must return a new Job() FROM this  
            data and any other relevant info from the job page  

        This method is called by `Scraper.parse()` method if load_full_jobs==True  
        Must return a Job()  
        """
        return Job(job_dict)

    def get_next_page_url(self, response):
        """
        Scrapers can re write this method. 
        This method must be re-wrote to use Scraper(load_all_new_pages=True)

        Arguments:  
        - response: scrapy response object for the listing page

        This method is called by `Scraper.parse()` method if load_all_new_pages==True  
        Must return a URL string or None if there no more pages to load    
        """
        return None