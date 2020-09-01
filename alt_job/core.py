import argparse
import json
from shutil import copyfile

from .__version__ import __version__
from .scrape import scrape, get_all_scrapers
from .config import AltJobOptions, TEMPLATE_FILE
from .db import  JsonDataBase
from .mail import MailSender
from .items import Job
from .utils import init_log, perform, get_xlsx_file

class AltJob(object):

    def __init__(self):

        self.config=AltJobOptions()

        if self.config['alt_job']['version'] :
            self.print_version()
            exit(0)

        if self.config['alt_job']['template_conf']:
            print(TEMPLATE_FILE)
            exit(0)

        self.log = init_log(self.config['alt_job']['log_level'])

        self.print_version()
        self.log.debug('Configuration\n'+json.dumps(dict(self.config), indent=4))

        # init database
        self.db=None
        if self.config['alt_job']['jobs_datafile']:
            self.db=JsonDataBase(jobs_filepath=self.config['alt_job']['jobs_datafile'])
        else:
            self.db=JsonDataBase()

        if len(self.config['alt_job']['enabled_scrapers'] )>0:
            self.log.info("Scraping websites: {}".format(', '.join(self.config['alt_job']['enabled_scrapers'])))
        else:
            print("No website to scrape! Please configure at least one scraper in your config file")
            exit(1)

    def run(self):
        # Run all scrapers
        scraped_data=[]

        returned_data=perform(self.process_scrape, self.config['alt_job']['enabled_scrapers'], 
            asynch=self.config['alt_job']['workers']>1,
            workers=self.config['alt_job']['workers'],
            progress=len(self.config['alt_job']['enabled_scrapers'])>1 )

        # returned_data is a list of lists
        for scraped_jobs in returned_data:
            scraped_data.extend(scraped_jobs)

        # Determine all NEW jobs
        new_jobs = [ Job(job) for job in scraped_data if not self.db.find_job(job) ]
        older_jobs = [ c for c in scraped_data if c not in new_jobs ]
        
        self.log.debug('Older jobs are\n{}'.format(older_jobs))
        self.log.debug('New jobs are\n{}'.format(new_jobs))

        self.log.info("Found {} new jobs".format(len(new_jobs)))
        
        # Write all jobs to database
        self.db.update_and_write_jobs(older_jobs+new_jobs)
        if self.db.filepath!='null':
            self.log.info('Jobs write to file: {}'.format(self.db.filepath))

        if new_jobs:

            if self.config['alt_job']['xlsx_output']:
                file = get_xlsx_file(new_jobs)
                copyfile(file.name, self.config['alt_job']['xlsx_output'])
                self.log.info("XLSX file wrote at {}".format(self.config['alt_job']['xlsx_output']))
            
            if self.config['alt_job']['smtphost']:
                mail=MailSender(**self.config['alt_job'])
                mail.send_mail_alert(new_jobs, scraper_configs=self.get_scraper_configs_string(new_jobs))
            else:
                self.log.info("Configuration 'smtphost' not configured, not sending email")
        else:
            self.log.info("No new jobs, not sending email")

    def get_scraper_configs_string(self, new_jobs):
        string=""
        for scraper in self.config['alt_job']['enabled_scrapers']:
            urls = []
            urls.extend([self.config[scraper]['url']] if 'url' in self.config[scraper] else [])
            urls.extend(self.config[scraper]['start_urls'] if 'start_urls' in self.config[scraper] else [])

            string+="{name} (URL: {urls}, Load: {load}) | ".format(
                    name=scraper, 
                    urls=', '.join('<a href="{url}"> {i}</a>'.format(url=url, i=urls.index(url)+1) for url in urls), 
                    load='Full' if ('load_full_jobs' in self.config[scraper] and self.config[scraper]['load_full_jobs'] and 
                        'load_all_new_pages' in self.config[scraper] and self.config[scraper]['load_all_new_pages']) else 'Full, first page only' if (
                        'load_full_jobs' in self.config[scraper] and self.config[scraper]['load_full_jobs']) else 'Quick')
        return string

    def process_scrape(self, website):
        log_level=self.config['alt_job']['scrapy_log_level']
        scraper_config=self.config[website]
        db=self.db
        return scrape(website, scraper_config, log_level, db)

    
    @staticmethod
    def print_version():
        print('Alt Job version {}'.format(__version__))