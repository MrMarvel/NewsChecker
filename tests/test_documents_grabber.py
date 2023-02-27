from unittest import TestCase
from grabber import documents_grabber

class GrabberTest(TestCase):
    def test_get_information_news_from_page_exceptions(self):
        for page_num in [-100, -10, -1, 0]:
            with self.assertRaises(Exception) as cm:
                documents_grabber.get_information_news_from_site(2023, page_num)

    def test_get_information_news_from_page_no_exception(self):
        for year in range (2015, 2023):
            got = documents_grabber.get_information_news_from_site(year, 1)
