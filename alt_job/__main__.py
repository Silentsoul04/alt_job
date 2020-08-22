import sys
if sys.version_info[0] < 3: 
    print("Sorry, you must use Python 3")
    sys.exit(1)

import argparse
import json
import multiprocessing

from .__version__ import __version__
from .scrape import scrape, get_all_scrapers
from .config import JobsConfig, TEMPLATE_FILE
from .db import  JsonDataBase
from .mail import MailSender
from .jobs import Job
from .utils import log, init_log, perform

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

        log.debug('Configuration\n'+json.dumps(dict(self.config), indent=4))

        # init database
        self.db=None
        if self.config['alt_job']['jobs_datafile']:
            self.db=JsonDataBase(jobs_filepath=self.config['alt_job']['jobs_datafile'])
        else:
            self.db=JsonDataBase()

        # Run all scrapers asynchronously
        scraped_data=[]
        returned_data=perform(self.process_scrape,
            [ w for w in get_all_scrapers() if w in self.config ], 
            asynch=True, workers=self.config['alt_job']['workers'] )

        # returned_data is a list of lists
        for scraped_jobs in returned_data:
            scraped_data.extend(scraped_jobs)

        # Determine all NEW jobs
        new_jobs = [ Job(job) for job in scraped_data if not self.db.find_job(job) ]
        older_jobs = [ c for c in scraped_data if c not in new_jobs ]
        
        log.debug('Older jobs are\n{}'.format('\n'.join([ str(j['title'])+'\n - URL: '+str(j['url']) for j in older_jobs ])))
        log.debug('New jobs are\n{}'.format('\n'.join([ str(j['title'])+'\n - URL: '+str(j['url']) for j in new_jobs ] or ['None'])))

        # Write all jobs to database
        self.db.update_and_write_jobs(older_jobs+new_jobs)

        log.info('Jobs write to file: {}'.format(self.db.filepath))

        if new_jobs:
            mail=MailSender(**self.config['mail_sender'])
            log.info('Sending email digest')
            mail.send_mail_alert(new_jobs)
        else:
            log.info("No new jobs, not sending email")

    def process_scrape(self, website):
        scraped_data_result=multiprocessing.Manager().list()
        process = multiprocessing.Process(target=scrape,
            kwargs=dict(website=website,
                scraper_config=self.config[website],
                db=self.db,
                log_level=self.config['alt_job']['scrapy_log_level'],
                scraped_data_result=scraped_data_result))
        process.start()
        process.join()
        scraped_data_result=list(scraped_data_result)
        return scraped_data_result

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