from contextlib import contextmanager
import os
import unittest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.support.ui import WebDriverWait


class TestSubmitFlow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        chromedriver = os.getenv('CHROMEWEBDRIVER', 'tests/bin')
        chromedriver += '/chromedriver'

        chrome_options = Options()
        chrome_options.add_argument('--headless')

        cls.driver = webdriver.Chrome(chromedriver, options=chrome_options)

    @classmethod
    def tearDownClass(cls):
        cls.driver.close()
        cls.driver.quit()

    @contextmanager
    def wait_for_new_page(self):
        old_html_tag = self.driver.find_element_by_xpath('/html')
        yield
        WebDriverWait(self.driver, 5).until(staleness_of(old_html_tag))

    def test_submit(self):
        self.driver.get('http://localhost:8000')
        self.driver.find_element_by_link_text('Add Document').click()

        # Make a file on disk to submit
        with open('./a.txt', 'w') as fd:
            fd.write('some text')

        doc_path = os.path.abspath('./a.txt')

        self.driver.find_element_by_id('file').send_keys(doc_path)
        self.driver.find_element_by_id('doc_title').send_keys('APPROVE TITLE')
        self.driver.find_element_by_id('doc_description').send_keys(
            'APPROVE DESCRIPTION'
        )
        self.driver.find_element_by_id('source_org').send_keys('APPROVE ORG')

        self.driver.find_element_by_id('submit').click()

        self.assertIn('Document submitted for review', self.driver.page_source)

        # Make another submission to test deleting
        self.driver.find_element_by_link_text('Add Document').click()

        self.driver.find_element_by_id('file').send_keys(doc_path)
        self.driver.find_element_by_id('doc_title').send_keys('DELETE TITLE')
        self.driver.find_element_by_id('doc_description').send_keys(
            'DELETE DESCRIPTION'
        )
        self.driver.find_element_by_id('source_org').send_keys('DELETE ORG')

        self.driver.find_element_by_id('submit').click()

        # Ensure docs aren't visible yet
        self.driver.find_element_by_link_text('See all documents').click()
        self.driver.find_element_by_id('query').send_keys('TITLE')
        self.driver.find_element_by_id('search').click()
        self.assertIn('0 of 0', self.driver.page_source)

        # Log in as admin to review submissions
        admin_password = os.getenv('ADMIN_PASSWORD', 'testpassword')
        self.driver.get(
            'http://admin:{}@localhost:8000/auth/'.format(admin_password)
        )

        # Ensure admin can view docs pending review
        self.driver.find_element_by_link_text('Review').click()

        with self.wait_for_new_page():
            self.driver.find_elements_by_xpath(
                '//button[@class="approve"]'
            )[0].click()

        self.assertIn('Approved', self.driver.page_source)

        self.driver.get('http://localhost:8000/review')

        with self.wait_for_new_page():
            self.driver.find_elements_by_xpath(
                '//button[@class="remove"]'
            )[0].click()

            alert = self.driver.switch_to.alert
            alert.accept()

        self.assertIn('Deleted', self.driver.page_source)

        # Log out to ensure we can view approved docs
        self.driver.find_element_by_link_text('Log Out').click()
        self.driver.find_element_by_link_text('Search').click()

        self.driver.find_element_by_id('query').send_keys('TITLE')
        self.driver.find_element_by_id('search').click()
        self.assertIn('1 of 1', self.driver.page_source)

        self.driver.find_element_by_link_text('APPROVE TITLE').click()

        clean_up_url = self.driver.current_url

        # Log in to finish cleaning up
        self.driver.get(
            'http://admin:{}@localhost:8000/auth/'.format(admin_password)
        )

        self.driver.get(clean_up_url)
        self.driver.find_element_by_id('delete').click()
        alert = self.driver.switch_to.alert
        alert.accept()

        self.driver.get('http://localhost:8000')
        self.driver.find_element_by_link_text('Log Out').click()


if __name__ == '__main__':
    import unittest
    unittest.main()
