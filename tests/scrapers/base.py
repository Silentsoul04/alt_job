import unittest
import abc

class TestScraper(abc.ABC, unittest.TestCase):
    SUPPORT_LOAD_ALL_JOBS=False
    SUPPORT_LOAD_ALL_NEW_PAGES=False
    GET_JOB_DICT_LOADED_KEYS=['url', 'title']
    PARSE_FULL_JOB_PAGE_LOADED_KEYS=['description']
    
    def test_scraper(self):
        pass