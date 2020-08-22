import configparser
import collections
import os
import json
import copy
from .utils import parse_timedelta, log

# Configuration handling -------------------------------------------------------
class JobsConfig(collections.UserDict):
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

        # casting int, booleans and json data sctructure
        for scraper in self.data:
            for config_option in self.data[scraper]:
                # List of booleans config values
                if config_option in ['use_google_cache', 'smtptls', 'load_full_jobs', 'load_all_new_pages', 'attach_jobs_description']:
                    self.data[scraper][config_option]=getbool(self.parser, scraper, config_option)
                # list of json config values
                if config_option in ['mailto']:
                    self.data[scraper][config_option]=getjson(self.parser, scraper, config_option)
                # List of integer config values
                if config_option in ['smtpport', 'workers']:
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
TEMPLATE_FILE="""[alt_job]
log_level=INFO
scrapy_log_level=WARNING
# jobs_datafile=/home/user/data/jobs.json

[mail_sender]
# Email server settings
smtphost=smtp.gmail.com
mailfrom=user@gmail.com
smtpuser=user@gmail.com
smtppass=p@assw0rd
smtpport=587
smtptls=Yes

# Email notif settings

mailto=["user@gmail.com"]

# Scrapers 

[arrondissement.com]
url=https://www.arrondissement.com/tout-list-emplois/
load_full_jobs=True
load_all_new_pages=True

[cdeacf.ca]
url=http://cdeacf.ca/recherches?f[0]=type:offre_demploi
load_full_jobs=False
load_all_new_pages=False

[chantier.qc.ca]
url=https://chantier.qc.ca/decouvrez-leconomie-sociale/offres-demploi
load_full_jobs=False
load_all_new_pages=False

[charityvillage.com]
url=
load_full_jobs=False
load_all_new_pages=True

[engages.ca]
url=https://www.engages.ca/emplois?search%5Bkeyword%5D=&search%5Bjob_sector%5D=&search%5Bjob_city%5D=Montr%C3%A9al
load_full_jobs=False

[goodwork.ca]
url=https://www.goodwork.ca/jobs.php?prov=QC
load_full_jobs=False

[enviroemplois.org]
url=
load_full_jobs=False
load_all_new_pages=False
"""

# Config default values
#TODO
DEFAULT_CONFIG={
    'alt_job':{
        'log_level':'INFO',
        'scrapy_log_level':'ERROR',
        'jobs_datafile':''
    },

    'mail_sender':{
        'smtphost':'',
        'mailfrom':'',
        'smtpuser':'',
        'smtppass':'',
        'smtpport':'587',
        'smtptls':'Yes'
    }

}


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
