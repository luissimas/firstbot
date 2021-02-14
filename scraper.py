from selenium import webdriver
import re

class Result:
    def __init__(self, url, title, content):
        self.url = url
        self.title = title
        self.content = content


def scrapePage(query):
    # Setting up driver
    options = webdriver.ChromeOptions()
    options.binary_location = "/usr/bin/chromium"
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    driver.get('https://pt.wikipedia.org/wiki/Wikipédia:Página_principal')


    searchBox = driver.find_element_by_xpath('/html/body/div[5]/div[1]/div[2]/div/form/div/input[1]')
    searchBox.send_keys(query)

    searchButton = driver.find_element_by_xpath('/html/body/div[5]/div[1]/div[2]/div/form/div/input[4]')
    searchButton.click()

    resultUrl = driver.current_url
    resultTitle = driver.find_element_by_xpath('/html/body/div[3]/h1').text
    resultContent = re.sub(r'\[.*?\]', "", str(driver.find_element_by_xpath('/html/body/div[3]/div[3]/div[5]/div[1]/p[1]').text))

    driver.close()

    return Result(resultUrl, resultTitle, resultContent)
