from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class FunctionalTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()  # Make sure `geckodriver` is installed and in PATH

    def tearDown(self):
        self.browser.quit()

    def test_homepage(self):
        self.browser.get(self.live_server_url)
        self.assertIn("Galaxy", self.browser.title)

    def test_create_galaxy_entry(self):
        # Assuming there's an input box for creating new galaxy entries
        inputbox = self.browser.find_element(By.ID, 'new_galaxy_name')
        inputbox.send_keys('New Galaxy')
        inputbox.send_keys(Keys.ENTER)
        # Verify the new galaxy appears on the page
        self.assertIn('New Galaxy', self.browser.page_source)
        # More steps would be needed if the page updates dynamically without reload
