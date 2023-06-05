from selenium.common import WebDriverException
from undetected_chromedriver import Chrome  # , ChromeOptions
from selenium.webdriver.common.by import By
from python_anticaptcha import AnticaptchaClient, ImageToTextTask
from PIL import Image
from io import BytesIO
import time
import logging
import Task
import utils


class ChromeManager(object):

    _driver: Chrome = None
    api_key = '40832b1a7b09276db69e2505369aa7b2'
    ac_client = AnticaptchaClient(api_key)

    def __init__(self):
        logging.basicConfig()
        logging.getLogger(__name__).setLevel(logging.DEBUG)
        try:
            # self._options = ChromeOptions()
            # self._options.add_argument('--load-extension=D:\\Mneniya.pro\\RA\\trunk\\packages\\RAProxyManagerChrome')
            # self._driver = Chrome(self._options)
            self._driver = Chrome()
            self._driver.maximize_window()
        except Exception as e:
            logging.error("Cannot create Chrome driver instance: ")
            logging.exception(e)

    def get_html_page_by_uri(self, uri: str):
        try:
            self._driver.get(uri)
        except Exception as e:
            logging.error("Cannot get Uri:" + uri + ": ")
            logging.exception(e)

            if e is WebDriverException:
                self.restart_driver()

    def get_html_page(self, task: Task):
        utils.sleep_with_random_timeout(1, 5)
        try:
            self._driver.get(task.Uri)
            task.Uri = self._driver.current_url
            task.Page_Source = self._driver.page_source

            # CAPTCHA checking
            # For check box
            if utils.check_str_to_match_re(task.Page_Source, task.check_box_xpath):
                self.submit_captcha_check_box(task)
            # For image
            if utils.check_str_to_match_re(task.Uri, task.captcha_check_url_pattern):
                try:

                    #  CAPTCHA service here
                    # ImageToText task for first supported only
                    captcha_task = ImageToTextTask(self.get_captcha_image(task))
                    job = self.ac_client.createTask(captcha_task)
                    job.join()

                    while not job.check_is_ready():
                        time.sleep(0.5)

                    answer = job.get_captcha_text()

                except Exception as e:
                    logging.error("Cannot sole CAPTCHA:")
                    logging.exception(e)
                    answer = "cannot recognize the text"

                self.submit_captcha(task, answer)

        except Exception as e:
            logging.error("Cannot get Uri for Task:" + str(task.ID) + " the URI is:" + str(task.Uri) + ": ")
            logging.exception(e)

            if e is WebDriverException:
                self.restart_driver()

    def submit_captcha(self, task: Task, answer: str):
        try:
            self._driver.find_element(By.XPATH, task.rep_xpath).send_keys(answer)
            self._driver.find_element(By.XPATH, task.submit_btn_xpath).submit()
            task.Uri = self._driver.current_url
            task.Page_Source = self._driver.page_source
        except Exception as e:
            logging.error("Cannot submit CAPTCHA for Task:" + str(task.ID) + " the URI is:" + str(task.Uri) + ": ")
            logging.exception(e)

            if e is WebDriverException:
                self.restart_driver()

    def submit_captcha_check_box(self, task: Task):
        try:
            self._driver.find_element(By.XPATH, task.check_box_xpath).click()
            task.Uri = self._driver.current_url
            task.Page_Source = self._driver.page_source
        except Exception as e:
            logging.error("Cannot submit CAPTCHA for Task:" + str(task.ID) + " the URI is:" + str(task.Uri) + ": ")
            logging.exception(e)

    def get_captcha_image(self, task: Task):
        try:
            # Find the element by XPath
            element = self._driver.find_element_by_xpath(task.captcha_img_xpath)

            # Get the element's location and size
            # location = element.location
            # size = element.size

            # Take a screenshot of the element
            screenshot = element.screenshot_as_png

            # Convert the screenshot to a bitmap image
            image = Image.open(BytesIO(screenshot))

            return image
        except Exception as e:
            logging.error("Cannot get CAPTCHA image with provided XPATH: ")
            logging.exception(e)

            if e is WebDriverException:
                self.restart_driver()

    def quit(self):
        try:
            self._driver.quit()
        except Exception as e:
            logging.error("Exception happened on Chrome quit: ")
            logging.exception(e)

    def restart_driver(self):
        try:
            if self._driver is not None:
                self._driver.quit()
        except Exception as e:
            logging.error("Cannot dispose driver to restart: ")
            logging.exception(e)

        try:
            # self._options = ChromeOptions()
            # self._options.add_argument('--load-extension=D:\\Mneniya.pro\\RA\\trunk\\packages\\RAProxyManagerChrome')
            # self._driver = Chrome(self._options)
            self._driver = Chrome()
            self._driver.maximize_window()

        except Exception as e:
            logging.error("Cannot create Chrome driver instance: ")
            logging.exception(e)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._driver.quit()
