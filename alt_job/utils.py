import re
from datetime import timedelta
import sys

import xlsxwriter
import tempfile

# Loggin setter
import logging
import os

import functools
import concurrent.futures

# Utility methods
def init_log(verb_level='INFO', name='alt_job', logfile=None, nostd=False):
    log = logging.getLogger(name=name)
    format_string='%(asctime)s [{}] %(levelname)s: %(message)s'.format(name)
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

def perform(func, data, func_args=None, asynch=False,  workers=None , progress=False, desc='Loading...'):
        """
        Wrapper arround executable and the data list object.
        Will execute the callable on each object of the list.

        Parameters:  
        
        - `func`: callable stateless function. func is going to be called like `func(item, **func_args)` on all items in data.
        - `data`: if stays None, will perform the action on all rows, else it will perfom the action on the data list.
        - `func_args`: dict that will be passed by default to func in all calls.
        - `asynch`: execute the task asynchronously
        - `workers`: mandatory if asynch is true.
        - `progress`: to show progress bar with ETA (if tqdm installed).  
        - `desc`: Message to print if progress=True  

        Returns a list of returned results
        """
        if not callable(func) :
            raise ValueError('func must be callable')
        #Setting the arguments on the function
        func = functools.partial(func, **(func_args if func_args is not None else {}))
        #The data returned by function
        returned=list() 
        elements=data
        try: import tqdm
        except ImportError: progress=False
        tqdm_args=dict()
        #The message will appear on loading bar if progress is True
        if progress is True :
            tqdm_args=dict(desc=desc, total=len(elements))
        #Runs the callable on list on executor or by iterating
        if asynch == True :
            if isinstance(workers, int) :
                if progress==True :
                    returned=list(tqdm.tqdm(concurrent.futures.ThreadPoolExecutor(
                    max_workers=workers ).map(
                        func, elements), **tqdm_args))
                else:
                    returned=list(concurrent.futures.ThreadPoolExecutor(
                    max_workers=workers ).map(
                        func, elements))
            else:
                raise AttributeError('When asynch == True : You must specify a integer value for workers')
        else :
            if progress==True:
                elements=tqdm.tqdm(elements, **tqdm_args)
            for index_or_item in elements:
                returned.append(func(index_or_item))
        return(returned)