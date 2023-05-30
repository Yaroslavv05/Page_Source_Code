import undetected_chromedriver
import time

try:
    driver = undetected_chromedriver.Chrome()
    driver.get('https://nowsecure.nl/')
    time.sleep(10)
    page_html = driver.page_source
    print(page_html)
except Exception as ex:
    print(ex)