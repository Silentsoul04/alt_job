import os
import json
import time
import threading
import datetime
from shutil import copyfile
from .config import find_files

# Database default files
DEFAULT_JOBS_FILE='jobs.json'
# Writing into the database file is thread safe
job_file_write_lock = threading.Lock()

class JsonDataBase():
    '''Interface to JSON database file. Work to write all nice to file in a thread safe way'''
    def __init__(self, jobs_filepath=""):
        
        if not jobs_filepath : 
            jobs_filepath=self.find_jobs_file(create=True)
        self.filepath=jobs_filepath
        if self.filepath=='null':
            self._data=[]
        else:
            self._data=self.build_jobs(self.filepath)

            try: 
                self.update_and_write_jobs(self._data)
            except:
                print("Could not write jobs database: {}".format(self.filepath))
                raise

    def find_jobs_file(self, create=False, daemon=False):
        files=[DEFAULT_JOBS_FILE]
        env=['HOME', 'PWD', 'XDG_CONFIG_HOME', 'APPDATA']
        return(find_files(env, files, "[]", create=True)[0])

    # Read jobs database
    def build_jobs(self, filepath):
        '''Load reports database and return the complete structure'''
        jobs=[]
        if os.path.isfile(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as jobs_fd:
                    jobs=json.load(jobs_fd)
                print("Load jobs database: %s"%filepath)
            except Exception:
                print("Could not read jobs database: {}. Backing up current DB and creating new database...".format(filepath))
                db_back= filepath+'.error{}'.format(datetime.datetime.now())
                copyfile(filepath, db_back)
                print("Your DB backup is {}".format(db_back))
                with open(filepath, 'w', encoding='utf-8') as out:
                    out.write('[]')
                return self.build_jobs(filepath)

        else:
            print("The database file %s do not exist. It will be created."%(filepath))
        return jobs

    def update_and_write_jobs(self, job_list=None):
        '''Update the jobs that have been scraped based on job_list.  
        Keep same report order add append new jobs at the bottom.  '''
        if not job_list: return
        if self.filepath=='null': return
        
        for newjob in job_list:
            newjob=dict(newjob)
            new=True
            for r in self._data:
                if r['url']==newjob['url']:
                    self._data[self._data.index(r)].update(newjob)
                    new=False
                    break
            if new: 
                self._data.append(newjob)
        
        # Write method thread safe
        while job_file_write_lock.locked():
            time.sleep(0.01)
        job_file_write_lock.acquire()
        with open(self.filepath,'w', encoding='utf-8') as jobs_fd:
            json.dump(self._data, jobs_fd, indent=4)
            job_file_write_lock.release()

    def find_job(self, job):
        '''Find the job in DB is it's there based on the url .  
        Return a job or None'''
        last_job=[r for r in self._data if r['url'] ==job['url'] ]
        if len(last_job)>0: 
            last_job=last_job[0]
        else: last_job=None
        return last_job
