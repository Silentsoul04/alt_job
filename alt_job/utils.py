import re
from datetime import timedelta
import sys

import xlsxwriter
import tempfile

# Loggin setter
import logging
import os


# Log handler
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

def get_xlsx_file(items, headers=None):
    """
    Argments:  
    - items: list of dict  
    - headers: dict like {'key':'Key nice title for Excel'}  

    Return excel file as tempfile.NamedTemporaryFile
    """
    log.info("Making Excel file...")
    with tempfile.NamedTemporaryFile(delete=False) as excel_file:
        with xlsxwriter.Workbook(excel_file.name) as workbook:
            if not headers:
                headers={ key:key.title() for key in items[0].keys() }
            worksheet = workbook.add_worksheet()
            worksheet.write_row(row=0, col=0, data=headers.values())
            header_keys = list(headers.keys())
            cell_format = workbook.add_format()
            for index, item in enumerate(items):
                row = map(lambda field_id: str(item.get(field_id, '')), header_keys)
                worksheet.write_row(row=index + 1, col=0, data=row)
                worksheet.set_row(row=index + 1, height=13, cell_format=cell_format)
            worksheet.autofilter(0, 0, len(items)-1, len(headers.keys())-1)
        return excel_file


def get_xlsx_file_bytes(items, headers=None):
    """
        Return excel file as Bytes
    """
    with open(get_xlsx_file(items, headers).name, 'rb') as file:
        return file.read()