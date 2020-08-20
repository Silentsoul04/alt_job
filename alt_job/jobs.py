import collections
import scrapy
import textwrap

class Job(scrapy.Item):
    # Fields
    url = scrapy.Field()
    title = scrapy.Field()
    source = scrapy.Field()
    organisation = scrapy.Field()
    regex_matched = scrapy.Field()
    description = scrapy.Field()
    date_posted = scrapy.Field()
    date_end_posting = scrapy.Field()
    location = scrapy.Field()
    job_type = scrapy.Field()
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key in Job.fields:
            self.setdefault(key, None)
        
    def get_text(self):
        return """Title: {title}

Organisation: {organisation}

Date posted: {date_posted}

URL: {url}

Regex matched: {regex_matched}

Source: {source}

Description: {description}
""".format(**dict(self))

    # JOB_KEYS=['url', 'title', 'description', 'regex_matched']

    # def __init__(self, data=None, url=None, title=None, description=None, regex_matched=None):
    #     # Init with data dict
    #     super().__init__(data)
    #     # Write values passed in args
    #     if url:
    #         self.data['url']=url
    #     if title:
    #         self.data['title']=title
    #     if description:
    #         self.data['description']=description
    #     if regex_matched:
    #         self.data['regex_matched']=regex_matched
    #     # Init to None if no value passed
    #     for key in self.JOB_KEYS:
    #         if not key in self.data:
    #             self.data[key]=None

# class JobsSummary(scrapy.Item):
#     url = scrapy.Field()
#     jobs = scrapy.Field()

    # SUMM_KEYS=['url', 'jobs']

    # def __init__(self, data=None, url=None, jobs=None):
    #     # Init with data dict
    #     super().__init__(data)
    #     if url:
    #         self.data['url']=url
    #     if jobs:
    #         self.data['jobs']=jobs
    #     # Init to None if no value passed
    #     for key in self.SUMM_KEYS:
    #         if not key in self.data:
    #             self.data[key]=None
