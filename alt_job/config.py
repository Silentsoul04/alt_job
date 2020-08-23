import configparser
import collections
import os
import json
import copy
from .utils import parse_timedelta, log
from .scrape import get_all_scrapers
import argparse

# Configuration handling
class AltJobOptions(collections.UserDict):
    """
    Wrap argparse and configparser objects into one configuration dict object
    """
    def __init__(self):
        # overwriting arguments
        parser1 = argparse.ArgumentParser(
             # Turn off help, so we print all options in response to -h
            add_help=False)

        # CLI only arguments
        parser1.add_argument('-c','--config_file', help='configuration file(s). Default locations will be checked and loaded if file exists: `~/.alt_job/alt_job.conf`, `~/alt_job.conf` or `./alt_job.conf`', metavar='<File path>', nargs='+')
        parser1.add_argument('-t','--template_conf', action='store_true', help='print a template config file and exit. ')
        parser1.add_argument('-V','--version', action='store_true', help='print Alt Job version and exit. ')

        args1, remaining_argv = parser1.parse_known_args()

        if args1.config_file:
            config_file = ConfigurationFile(files=args1.config_file)
        else:
            config_file = ConfigurationFile()

        # Determine enlabled scrapers
        config_file['alt_job']['enabled_scrapers'] = [ w for w in get_all_scrapers() if w in config_file ]
        
        # Determine the default arguments
        defaults_args=config_file['alt_job']

        # Parse rest of arguments
        # Don't suppress add_help here so it will handle -h
        parser2 = argparse.ArgumentParser(
            # Inherit options from config_parser
            parents=[parser1],
            description="""Atl Job scrapes a bunch of green/social/alternative websites to send digest of new job posting by email.""",
            prog='python3 -m alt_job', formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            )

        parser2.set_defaults(**defaults_args)

        # Arguments that overwrites [alt_job] config values
        parser2.add_argument("-x", "--xlsx_output", metavar='<File path>', help='Write all NEW jobs to Excel file')
        parser2.add_argument("-s", "--enabled_scrapers", metavar='<Website>', help="List of enabled scrapers. By default it's all scrapers configured in config file(s)", nargs='+')
        parser2.add_argument("--jobs_datafile", metavar='<File path>', 
            help="""JSON file to store ALL jobs data. Default is '~/jobs.json'. 
            Use 'null' keyword to disable the storage of the datafile, all jobs will be considered as new and will be loaded""")
        parser2.add_argument("--workers", metavar='<Number>', help="Number of websites to scrape asynchronously", type=int)
        parser2.add_argument("--quick", "--no_load_all_jobs", action='store_true', help='Do not load the full job description page to parse additionnal data (Much more faster). This settings is applied to all scrapers')
        parser2.add_argument("--first_page_only", "--no_load_all_new_pages", action='store_true', help='Do not load new job listing pages until older jobs are found. This settings is applied to all scrapers')
        parser2.add_argument("--mailto", metavar="<Email>", help='Emails to notify of new job postings', nargs='+')
        parser2.add_argument("--log_level", metavar='<String>', help='Alt job log level. Exemple: DEBUG')
        parser2.add_argument("--scrapy_log_level", metavar='<String>', help='Scrapy log level. Exemple: DEBUG')
        
        args2 = parser2.parse_args(remaining_argv)

        # Update 'alt_job' section witll all parsed arguments
        config_file['alt_job'].update(vars(args2))
        config_file['alt_job'].update(vars(args1))

        # Overwriting load_all_new_pages and load_full_jobs if passed --first_page_only or --quick
        if args2.first_page_only:
            for website in [ k for k in config_file.keys() if k in get_all_scrapers() ]:
                config_file[website]['load_all_new_pages']=False
        if args2.quick:
            for website in [ k for k in config_file.keys() if k in get_all_scrapers() ]:
                config_file[website]['load_full_jobs']=False

        
        self.data=config_file

# Config default values
DEFAULT_CONFIG={
    'alt_job':{
        'log_level':'INFO',
        'scrapy_log_level':'ERROR',
        'jobs_datafile':'',
        'workers':5,
        'smtphost':'',
        'mailfrom':'',
        'smtpuser':'',
        'smtppass':'',
        'smtpport':'587',
        'smtptls':'Yes',
        'mailto':'[]'
    }
}

BOOL_VALUES=['use_google_cache', 'smtptls', 'load_full_jobs', 'load_all_new_pages', 'attach_jobs_description']
JSON_VALUES=['mailto']
INT_VALUES=['smtpport', 'workers']

class ConfigurationFile(collections.UserDict):
    '''Build config dict from file.  Parse the config file(s) and return dict config.  
        Return a tuple (config dict, read files list).  
        The dict returned contain all possible config values. Default values are applied if not specified in the file(s) or string.
    '''

    def __init__(self, data=None, files=None, string=None):
        super().__init__(data)
        self.files=files if files else []
        # Init config parser
        self.parser=configparser.ConfigParser()
        # Load default configuration
        self.parser.read_dict(DEFAULT_CONFIG)

        if string: 
            self.parser.read_string(string)
        else:
            if not self.files:
                self.files=find_config_files()
                if not self.files:
                    log.info("Could not find default config: `~/.alt_job/alt_job.conf`, `~/alt_job.conf` or `./alt_job.conf`")
            else:
                for f in self.files:
                    try :
                        with open(f,'r') as fp:
                            self.parser.read_file(fp)
                    except (FileNotFoundError, OSError) as err :
                       raise ValueError("Could not read config %s. Make sure the file exists and you have correct access right."%(f)) from err
        
        self.data=copy.deepcopy(self.parser._sections)
        self.data['alt_job']['config_file']=self.files
        # casting int, booleans and json data sctructure
        for scraper in self.data:
            for config_option in self.data[scraper]:
                # List of BOOL config values
                if config_option in BOOL_VALUES:
                    self.data[scraper][config_option]=getbool(self.parser, scraper, config_option)
                # list of JSON config values
                if config_option in JSON_VALUES:
                    self.data[scraper][config_option]=getjson(self.parser, scraper, config_option)
                # List of INT config values
                if config_option in INT_VALUES:
                    self.data[scraper][config_option]=getint(self.parser, scraper, config_option)

def getjson(conf, section, key):
    '''Return json loaded structure from a configparser object. Empty list if the loaded value is null.   
    Arguments:  
    - `conf`: configparser object  
    - `section`: config section
    - `key`: alt_job config key
    '''
    try:
        loaded=json.loads(conf.get(section, key))
        return loaded if loaded else []
    except ValueError as err:
        raise ValueError("Could not read JSON value in config file for key '{}' and string: '{}'".format(key, conf.get(section,key))) from err

def getbool(conf, section, key):
    '''Return bool value from a configparser object.  
    Arguments:  
    - `conf`: configparser object  
    - `section`: config section
    - `key`: alt_job config key
    '''
    try:
        return conf.getboolean(section, key)
    except ValueError as err:
        raise ValueError("Could not read boolean value in config file for key '{}' and string '{}'. Must be Yes/No".format(key, conf.get(section,key))) from err

def getint(conf, section, key):
    '''Return int value from a configparser object.  
    Arguments:  
    - `conf`: configparser object  
    - `section`: config section
    - `key`: alt_job config key
    '''
    try:
        return conf.getint(section, key)
    except ValueError as err:
        raise ValueError("Could not read int value in config file for key '{}' and string '{}'. Must be an integer".format(key, conf.get(section,key))) from err

# Configuration template -------------------------
TEMPLATE_FILE="""

[alt_job]

##### General config #####

# Logging
log_level=INFO
scrapy_log_level=ERROR

# Jobs data file, default is ~/jobs.json
# jobs_datafile=/home/user/Jobs/jobs-mtl.json

# Asynchronous workers, number of site to scan at the same time
# Default to 5.
# workers=10

##### Mail sender #####

# Email server settings
smtphost=smtp.gmail.com
mailfrom=you@gmail.com
smtpuser=you@gmail.com
smtppass=password
smtpport=587
smtptls=Yes

# Email notif settings
mailto=["you@gmail.com"]

##### Scrapers #####

# Scraper name
[goodwork.ca]
# URL to start the scraping, required for all scrapers
url=https://www.goodwork.ca/jobs.php?prov=QC

[cdeacf.ca]
url=http://cdeacf.ca/recherches?f%5B0%5D=type%3Aoffre_demploi

# Load all jobs: If supported by the scraper,
#   this will follow each job posting link in listing and parse full job description.
# Default to True!
load_all_jobs=False

[arrondissement.com]
url=https://www.arrondissement.com/tout-list-emplois/

# Load all new pages: If supported by the scraper,
#   this will follow each "next page" links and parse next listing page
#   until older (in database) job postings are found.
# Default to True!
load_all_new_pages=False

[chantier.qc.ca]
url=https://chantier.qc.ca/decouvrez-leconomie-sociale/offres-demploi
# Special case of chantier.qc.ca wich does not have paging
load_all_new_pages=False

# Disabled scraper
# [engages.ca]
# url=https://www.engages.ca/emplois?search%5Bkeyword%5D=&search%5Bjob_sector%5D=&search%5Bjob_city%5D=Montr%C3%A9al

"""

def find_files(env_location, potential_files, default_content="", create=False):
    '''Find existent files based on folders name and file names.  

    Arguments:  
    - `env_location`: list of environment variable to use as a base path. Exemple: ['HOME', 'XDG_CONFIG_HOME', 'APPDATA', 'PWD']  
    - `potential_files`: list of filenames. Exemple: ['.alt_job/alt_job.conf', 'alt_job.conf']  
    - `default_content`: Write default content if the file does not exist  
    - `create`: Create the file in the first existing env_location with default content if the file does not exist  
    '''
    potential_paths=[]
    existent_files=[]
    # build potential_paths of config file
    for env_var in env_location:
        if env_var in os.environ:
            for file_path in potential_files:
                potential_paths.append(os.path.join(os.environ[env_var],file_path))
    # If file exist, add to list
    for p in potential_paths:
        if os.path.isfile(p):
            existent_files.append(p)
    # If no file foud and create=True, init new template config
    if len(existent_files)==0 and create:
        os.makedirs(os.path.dirname(potential_paths[0]), exist_ok=True)
        with open(potential_paths[0],'w') as config_file:
            config_file.write(default_content)
        print("Init new file: %s"%(p))
        existent_files.append(potential_paths[0])
    return(existent_files)

def find_config_files(create=False):
    '''
    Returns the location of existing `alt_job.conf` file at `./alt_job.conf` and/or `~/alt_job.conf` or under `~/.alt_job/` folder
    '''
    files=['.alt_job/alt_job.conf', 'alt_job.conf']
    env=['HOME', 'XDG_CONFIG_HOME', 'APPDATA', 'PWD']
    
    return(find_files(env, files))
