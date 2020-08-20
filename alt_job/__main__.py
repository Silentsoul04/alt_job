import argparse

import json
import multiprocessing

from alt_job.__version__ import __version__
from alt_job.config import JobsConfig, TEMPLATE_FILE
from alt_job.db import  JsonDataBase
from alt_job.mail import NewJobsMailSender
from alt_job.jobs import Job
import alt_job.scrape
from alt_job import log, init_log

class AlternativeJob(object):

    def __init__(self):

        exit_code=0
        self.__dict__.update(vars(self.parse_args()))

        if self.version:
            self.print_version()
            exit(0)

        if self.template_conf:
            print(TEMPLATE_FILE)
            exit(0)

        # init config 
        self.config=None
        if self.config_file:
            self.config = JobsConfig(files=self.config_file)
        else:
            self.config = JobsConfig()
        init_log(self.config['alt_job']['log_level'])

        log.info('ALT JOB CONFIGURATION\n'+json.dumps(dict(self.config), indent=4))

        # init database
        self.db=None
        if self.config['alt_job']['jobs_datafile']:
            self.db=JsonDataBase(jobs_filepath=self.config['alt_job']['jobs_datafile'])
        else:
            self.db=JsonDataBase()

        scraped_data=[]

        for website in alt_job.scrape.get_all_scrapers():
            if website in self.config: 
                scraped_data.extend(self.process_scrape(website))

        new_jobs = [ Job(job) for job in scraped_data if not self.db.find_job(job) ]

        older_jobs = [ c for c in scraped_data if c not in new_jobs ]
        
        log.info('OLDER JOBS ARE\n{}'.format('\n'.join([ str(j['title'])+'\n - URL: '+str(j['url']) for j in older_jobs ])))

        log.info('NEW JOBS ARE\n{}'.format('\n'.join([ str(j['title'])+'\n - URL: '+str(j['url']) for j in new_jobs ] or ['None'])))

        self.db.update_and_write_jobs(new_jobs)

        log.info('JOBS WROTE TO FILE: {}'.format(self.db.filepath))

        if new_jobs:
            mail=NewJobsMailSender(**self.config['mail_sender'])
            log.info('SENDING EMAIL ALERT')
            mail.send_mail_alert(new_jobs)

    def process_scrape(self, website):
        scraped_data_result=multiprocessing.Manager().list()
        process = multiprocessing.Process(target=alt_job.scrape.scrape,
            kwargs=dict(website=website,
                scraper_config=self.config[website],
                db=self.db,
                log_level=self.config['alt_job']['scrapy_log_level'],
                scraped_data_result=scraped_data_result))
        process.start()
        process.join()
        return list(scraped_data_result)

    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(description="""Atl Job scrapes a bunch of green/social/alternative websites to send digest of new job posting by email.""", prog='python3 -m alt_job', formatter_class=argparse.RawDescriptionHelpFormatter)

        parser.add_argument('-c','--config_file', help='configuration file(s)', metavar='<File path>', nargs='+')
        parser.add_argument('-t','--template_conf', action='store_true', help='print a template config file and exit. ')
        parser.add_argument('-V','--version', action='store_true', help='print Alt Job version and exit. ')
        return parser.parse_args()

    def print_version(self):
        print('Alt Job version {}'.format(__version__))

def main():
    AlternativeJob()
    
if __name__ == '__main__':
    main()