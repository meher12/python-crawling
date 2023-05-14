from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import csv
import re
from urllib.parse import urlencode
import pandas as pd


# Set up Selenium
chrome_options = Options()
#chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-application-cache')
chrome_options.add_argument('--disable-cache')
chrome_options.add_argument('--disable-plugins')
chrome_options.add_argument('--disable-local-storage')
chrome_options.add_argument('--disable-session-storage')
chrome_options.add_argument('--disable-web-db')
driver = webdriver.Chrome(options=chrome_options)
# https://www.pagesjaunes.fr/pagesblanches/recherche?ou=Allees%20Marechal%20de%20Lattre%20de%20Tassigny%2017000%20La%20Rochelle
# https://www.pagesjaunes.fr/pagesblanches/recherche?ou=Impasse%20de%20l%E2%80%99Amiral%20Duperre%2017000%20La%20Rochelle%27
# https://www.pagesjaunes.fr/pagesblanches/recherche?ou=Avenue%20Amsterdam%2017000%20La%20Rochelle

data = []

def more_pages_available(driver):
        try:
            next_button = driver.find_element(By.XPATH, "//span[text()='Suivant']")
            return True
        except NoSuchElementException:
            return False   
input_file = 'urls.csv'
# Loop over the rows in the CSV file and visit the URLs
with open(input_file, 'r') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        base_url = 'https://www.pagesjaunes.fr/pagesblanches/recherche?ou='+row['url']
        print(base_url)
        query_params = {'q': 'selenium', 'page': 1}

        while True:
                    # Construct the URL with the current page number
                    url = base_url + '?' + urlencode(query_params)
                    driver.get(url)
                    driver.implicitly_wait(10)
                    html = driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')
                    list_li = soup.find('ul', {'class': 'bi-list'})
                    if(soup.find('li', class_='bi bi-generic')):
                        rows = list_li.find_all('li')
                        for row in rows:
                            row_data = []
                         
                            #Name
                            cells2 = row.find_all('h3')
                            for cell in cells2:
                                cell_data2 = cell.text
                                row_data.append(cell_data2)

                            #Address
                            cells4 = row.find_all('a', class_='pj-lb pj-link')
                            for cell in cells4:
                                cell_data4 = cell.text.replace("Voir le plan", "")
                                zipcode_match = re.search(r'\b\d{5}\b', cell_data4)
                                if zipcode_match:
                                    zipcode = zipcode_match.group(0)
                                else:
                                    print("No zip code found.")
                                row_data.append({"address": cell_data4.strip(), "zip_code": zipcode})

                            #Tel
                            cells3 = row.find_all('div', class_='number-contact')
                            for cell in cells3:
                                cell_data3 = cell.text.replace("Opposé aux opérations de marketing", "")
                                row_data.append(cell_data3)
                            data.append(row_data)

                    
                    with open('listings.csv', 'w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        #writer.writerow(['Name', 'Telephone'])
                        writer.writerows(data)
                    
                    # Increment the page number and check if there are more pages
                    query_params['page'] += 1
                    if not more_pages_available(driver):
                        break
    # Close browser
    driver.quit()


# Data Cleaning of CSV file using Pandas
def strip(text):
    try:
        return text.strip()
    except AttributeError:
        return text


table = pd.read_table("listings.csv", sep=r',',
                      names=["Name", "FullAdresse",  "Telephone1", "Telephone2"],
                      converters = {'Name' : strip,
                                    'FullAdresse' : strip,
                                    'Telephone1' : strip,
                                    'Telephone2' : strip,
                                    
                                    })
df = pd.DataFrame(table)
df.to_csv('listings.csv',  sep=',', index=False, header=True)

