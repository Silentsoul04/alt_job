import re
from datetime import timedelta

# Python version check

import sys
if sys.version_info[0] < 3: 
    print("Sorry, you must use Python 3")
    sys.exit(1)

# Loggin setter
import logging
import os

# Global log handler
log = logging.getLogger('alt_job')

# Utility methods

def init_log(verb_level, logfile=None, nostd=False):
    format_string='%(asctime)s [alt_job] %(levelname)s: %(message)s'
    # Add stdout: configurable
    log.setLevel(verb_level)
    std = logging.StreamHandler(sys.stdout)
    std.setLevel(verb_level)
    std.setFormatter(logging.Formatter(format_string))
    log.handlers=[]
    if not nostd: log.addHandler(std)
    else: log.addHandler(logging.StreamHandler(open(os.devnull,'w')))
    if logfile :
        fh = logging.FileHandler(logfile)
        fh.setLevel(verb_level)
        fh.setFormatter(logging.Formatter(format_string))
        log.addHandler(fh)
    return (log)

def parse_timedelta(time_str):
    """
    Parse a time string e.g. (2h13m) into a timedelta object.  Stolen on the web
    """
    regex = re.compile(r'^((?P<days>[\.\d]+?)d)?((?P<hours>[\.\d]+?)h)?((?P<minutes>[\.\d]+?)m)?((?P<seconds>[\.\d]+?)s)?$')
    time_str=replace(time_str,{
        'sec':'s',
        'second': 's',
        'seconds': 's',
        'minute':'m',
        'minutes':'m',
        'min':'m',
        'mn':'m',
        'days':'d',
        'day':'d',
        'hours':'h',
        'hour':'h'})
    parts = regex.match(time_str)
    if parts is None: raise ValueError("Could not parse any time information from '{}'.  Examples of valid strings: '8h', '2d8h5m20s', '2m4s'".format(time_str))
    time_params = {name: float(param) for name, param in parts.groupdict().items() if param}
    return timedelta(**time_params)

def replace(text, conditions):
    '''Multiple replacements helper method.  Stolen on the web'''
    rep=conditions
    rep = dict((re.escape(k), rep[k]) for k in rep ) 
    pattern = re.compile("|".join(rep.keys()))
    text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)
    return text

def get_valid_filename(s):
    '''Return the given string converted to a string that can be used for a clean filename.  Stolen from Django I think'''
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)