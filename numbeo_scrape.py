# -*- coding: utf-8 -*-

# libraries
import csv
import datetime
from bs4 import BeautifulSoup
import requests

#Text coding
CODING = 'utf-8'

#Messages
INIT_DOWNLOAD_LIST = 'Downloading url: '
FINISH_SCRAPING_PROJECT = 'Finish scraping project in: '
ERROR_EMPTY_HTML = 'Error empty html for '

#Files name
COUNTRIES_FILE = 'numbeo-countries.csv'
TOWNS_FILE = 'numbeo-towns.csv'

#Web address
BASE_URL = 'http://www.numbeo.com/cost-of-living/'
EXT_CURRENCY = '&displayCurrency='
EXT_CITY = '&city='

#Files column names
COL_NAMES = ["RE_Inexpensive_Meal", "RE_Meal_2Ppl", "RE_Combo_Meal", "RE_Domestic_Beer", "RE_Imported_Beer",
             "RE_Cappuccino", "RE_Coke/Pepsi", "RE_Water",
             "MK_Milk", "MK_White_Bread", "MK_Rice", "MK_Eggs", "MK_Cheese", "MK_Chicken_Breasts", "MK_Red_Meat",
             "MK_Apples", "MK_Banana", "MK_Oranges", "MK_Tomato", "MK_Potato", "MK_Onion", "MK_Lettuce",
             "MK_Water", "MK_Wine", "MK_Domestic_Beer", "MK_Imported_Beer", "MK_Cigarettes_Pack",
             "TR_Ticket", "TR_Monthly_Pass", "TR_Taxi_Start", "TR_Taxi_1km", "TR_Taxi_1h", "TR_Gasoline",
             "TR_VW_Golf", "TR_TY_Corolla",
             "UT_Basic_85m2", "UT_Prepaid_Mobile", "UT_Internet",
             "SL_Fitness_Club", "SL_Tennis", "SL_Cinema",
             "CH_Preschool", "CH_International_School",
             "CS_Jeans", "CS_Summer_Dress", "CS_Running_Shoes", "CS_Leather_Shoes",
             "RM_Apartment_1Centre", "RM_Apartment_1Outside", "RM_Apartment_3Centre", "RM_Apartment_3Outside",
             "BA_PriceM2_Centre", "BA_PriceM2_Outside",
             "SF_Average_Salary", "SF_Mortgage_%Yearly"]
COL_COUNTRY_NAME = ["Country_Name"]
COL_TOWN_NAME = ["Town_Name"]

class ScraperNumbeo():
        #Scraper class for numbeo.com

        def __init__ (self, main_url, download_cities = True, currency = 'USD'):
                self.main_url = main_url
                self.download_cities = download_cities
                self.currency = currency
                self.session = requests.Session()

        def scrape_site(self):
                init = datetime.datetime.now()
  
                html = self.download(self.main_url)

                if html == "":
                        print(ERROR_EMPTY_HTML + self.main_url)
                        return

                soup = BeautifulSoup(html.content, 'lxml')
                countriesweb = soup.find('table',{'class':'related_links'}).find_all('a')

                self.scrape_content(countriesweb)

                end = datetime.datetime.now()
                print FINISH_SCRAPING_PROJECT, end-init

        def scrape_content(self, countriesweb):
                countrieslist = []

                for country in countriesweb:
                        countries = []

                        countries.append(country['href'])
                        countries.append(country.text.encode(CODING))

                        countrieslist.append(countries)

                townslist = self.scrape_data(countrieslist,  COL_COUNTRY_NAME + COL_NAMES, COUNTRIES_FILE, self.download_cities)

                self.scrape_data(townslist, COL_COUNTRY_NAME + COL_TOWN_NAME + COL_NAMES, TOWNS_FILE)

        def scrape_data(self, urls, columns, filename, next_info = False):
                listrows = []
                townslist = []

                listrows.append(columns)

                for url in urls:
                        row = []

                        link_url = self.main_url + url[0] + EXT_CURRENCY + self.currency
                        html = self.download(link_url)

                        if html == "":
                                print(ERROR_EMPTY_HTML + link_url)
                                continue

                        soup = BeautifulSoup(html.content, "lxml")
                        trs = soup.find('table',{'class':'data_wide_table'}).find_all('tr')

                        #add in each row country name or, country and city name
                        for x in range(1, len(url)):
                                row.append(url[x])

                        for tr in trs:
                                td = tr.find_all('td')
                        
                                if(td != []):
                                        if(td[0].text.encode(CODING).count('%') > 0 and td[1].text.encode(CODING) != ' ?'):
                                                row.append(td[1].text.encode(CODING)[1:])
                                        else:
                                                end = td[1].text.encode(CODING).find('\xc2')
                                                row.append(td[1].text.encode(CODING)[1:end])
                                
                        listrows.append(row)

                        if next_info:
                                
                                townsdata = soup.find('select',{'id':'city'}).find_all('option')[1:]

                                for town in townsdata:
                                        towns = []

                                        address = url[0].replace("country_", "city_") + EXT_CITY + town.text.encode(CODING).replace(" ", "+")
                                        towns.append(address)
                                        towns.append(url[1])
                                        towns.append(town.text.encode(CODING))

                                        townslist.append(towns)                                

                self.writeCsvFile(filename, listrows)

                return townslist
        
        def download(self, url, num_retries=2):
                print INIT_DOWNLOAD_LIST, url
                html = ""
                try:
                        html = self.session.get(url)
                except:
                        if num_retries > 0:
                                num_retries -= 1
                                self.session = requests.Session()
                                self.download(url, num_retries-1)
                return html


        def writeCsvFile(self, filename, rows):
                
                csvoutput = csv.writer(open(filename, 'w'))
                csvoutput.writerows(rows)                                
                
if __name__ == '__main__':
        numbeo_scraper = ScraperNumbeo(BASE_URL)
        numbeo_scraper.scrape_site()
