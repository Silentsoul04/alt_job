import argparse
import json
from shutil import copyfile
from .__version__ import __version__
from .scrape import scrape, get_all_scrapers
from .config import AltJobOptions, TEMPLATE_FILE
from .db import  JsonDataBase
from .mail import MailSender
from .items import Job
from .utils import log, init_log, perform, get_xlsx_file

class AltJob(object):

    def __init__(self):

        self.config=AltJobOptions()

        if self.config['alt_job']['version'] :
            self.print_version()
            exit(0)

        if self.config['alt_job']['template_conf']:
            print(TEMPLATE_FILE)
            exit(0)

        init_log(self.config['alt_job']['log_level'])

        self.print_version()
        log.debug('Configuration\n'+json.dumps(dict(self.config), indent=4))

        # init database
        self.db=None
        if self.config['alt_job']['jobs_datafile']:
            self.db=JsonDataBase(jobs_filepath=self.config['alt_job']['jobs_datafile'])
        else:
            self.db=JsonDataBase()

        if len(self.config['alt_job']['enabled_scrapers'] )>0:
            log.info("Scraping websites: {}".format(', '.join(self.config['alt_job']['enabled_scrapers'])))
        else:
            print("No website to scrape! Please configure at least one scraper in your config file")
            exit(1)

        # Run all scrapers
        scraped_data=[]

        # Old synchronous iteration
        # for scraper in enabled_scrapers:
        #     scraped_jobs=self.process_scrape(scraper)
        #     scraped_data.extend(scraped_jobs)

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
        
        log.debug('Older jobs are\n{}'.format(older_jobs))
        log.debug('New jobs are\n{}'.format(new_jobs))

        log.info("Found {} new jobs".format(len(new_jobs)))
        
        # Write all jobs to database
        self.db.update_and_write_jobs(older_jobs+new_jobs)
        if self.db.filepath!='null':
            log.info('Jobs write to file: {}'.format(self.db.filepath))

        if new_jobs:

            if self.config['alt_job']['xlsx_output']:
                file = get_xlsx_file(new_jobs)
                copyfile(file.name, self.config['alt_job']['xlsx_output'])
                log.info("XLSX file wrote at {}".format(self.config['alt_job']['xlsx_output']))
            
            if self.config['alt_job']['smtphost']:
                mail=MailSender(**self.config['alt_job'])
                mail.send_mail_alert(new_jobs)
            else:
                log.info("Configuration 'smtphost' not configured, not sending email")
        else:
            log.info("No new jobs, not sending email")

    def process_scrape(self, website):
        log_level=self.config['alt_job']['scrapy_log_level']
        scraper_config=self.config[website]
        db=self.db
        return scrape(website, scraper_config, log_level, db)

    
    @staticmethod
    def print_version():
        print('Alt Job version {}'.format(__version__))