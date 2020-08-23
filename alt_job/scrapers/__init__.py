
from itemadapter import is_item, ItemAdapter
from scrapy.contracts import Contract
from scrapy.exceptions import ContractFail

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
                    raise ContractFail("Missing or None fields: %s" % missing_str)
                