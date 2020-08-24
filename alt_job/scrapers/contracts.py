

import re
from itemadapter import is_item, ItemAdapter
from scrapy.contracts import Contract
from scrapy.exceptions import ContractFail
from scrapy import spiderloader
from scrapy.utils import project
from scrapy.selector import Selector
from ..scrape import get_all_scrapers, scrape

class ScrapeNotNone(Contract):

    """ Contract to check presence of fields in scraped items and check if they are None
        e.g.
        @scrape_not_none url title description
    """

    name = 'scrape_not_none'

    def post_process(self, output):
        for x in output:
            if is_item(x):
                missing = [arg for arg in self.args if arg not in ItemAdapter(x) or ItemAdapter(x)[arg]==None]
                if missing:
                    missing_str = ", ".join(missing)
                    raise ContractFail("None fields: %s. Item %s" % (missing_str, x))

class ReturnsValidSelectorList(Contract):
    
    """ Contract to check if the returned output is a Selector list
        e.g.
        @returns_valid_selectorlist
    """

    name = 'returns_valid_selectorlist'

    def post_process(self, output):
        if not isinstance(output, list):
            raise ContractFail("Output is not a valid list. Output is {}".format(output))
        for out in output:
            if not isinstance(out, Selector):
                raise ContractFail("Output is not a valid SelectorList. Output is {}".format(output))

class ReturnsValidLink(Contract):
    
    """ Contract to check presence of fields in scraped items and check if they are None
        e.g.
        @returns_valid_link
    """

    name = 'returns_valid_link'

    def post_process(self, output):
        if output:
            output=output[0]
        if not isinstance(output, str):
            raise ContractFail("Output is not a valid String. Output is {}".format(output))
        if 'http' not in output:
            raise ContractFail("Output is not a valid link. Output is {}".format(output))

class AutoFillUrl(Contract):
    """ Set the url of the request automatically based on start_urls[0]

        @auto_url arrondissement.com
    """

    name = 'auto_url'

    def adjust_request_args(self, args):
        website=self.args[0]
        settings = project.get_project_settings()
        spider_loader = spiderloader.SpiderLoader.from_settings(settings)
        url=spider_loader.load(website).start_urls[0]
        args['url'] = url
        return args

class AutoFillJobUrl(Contract):
    """ Contract to set the url of the request automatically 
        to the first JOB. Loaded the listing and returns the first URL.

        @auto_job_url arrondissement.com
    """

    name = 'auto_job_url'

    def adjust_request_args(self, args):
        website=self.args[0]
        jobs = scrape(website, dict(load_full_jobs=False, load_all_new_pages=False))
        args['url'] = jobs[0]['url']
        print("First {} job posting test URL is: {}".format(website, args['url']))
        return args
                