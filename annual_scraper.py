from bs4 import BeautifulSoup
import requests
import pprint
import os
import time
from clint.textui import progress

site_data = 'https://eogdata.mines.edu/pages/download_dnb_composites_iframe.html'
records = dict()


def collect_download_links():

    global records

    with open('download.html') as html_file:
        soup = BeautifulSoup(html_file, 'lxml')

    entries = soup.select('ul.treeview > li')

    for entry in entries:

        year = entry.find('strong').text

        annual_data = entry.find('ul').find_all('li', recursive = False)[0]

        annual_links = annual_data.find('ul').find_all('li', recursive = False)

        if annual_links != []:
            records[year] = dict()
            
            for link in annual_links:
                name = link.find('a').text
                d_link = link.find('a')['href']

                records[year][name] = d_link
 

def download_files(years):

    global records
    print(years)
    print(records)

    for year in years:

        if year in records:

            print(f'\nDownloading files for the year {year}')
            print('------------------------------------------')
            
            yearwise_path = os.path.join(os.getcwd(), year)

            if not os.path.exists(yearwise_path):
                os.mkdir(yearwise_path)

            for name in records[year]:

                file_name = name + '.tgz'
                file_path = os.path.join(yearwise_path, file_name)

                print(f'\nSearching "{file_path}" in the current directory -> ', end = '')
                time.sleep(1)

                try :

                    if not os.path.exists(file_path):

                        print("NOT FOUND\n")
                        time.sleep(1)

                        print(f'Downloading "{file_path}"...')

                        download_site_response = requests.get(records[year][name], stream = True)
                        download_site_response.raise_for_status()

                        with open(file_path, 'wb') as file:
                            total_length = int(download_site_response.headers.get('content-length'))
                            
                            for chunk in progress.bar(download_site_response.iter_content(chunk_size=100000), expected_size=(total_length/100000) + 1):
                                if chunk:
                                    file.write(chunk)
                                    file.flush()

                        print(f'\n"{file_path}" DOWNLOAD STATUS: OK!!')

                    else:

                        print('FOUND\n')
                        time.sleep(1)

                except:

                    print(f'\nSome ERROR occurred while downloading "{file_path}"')

        else:
            print(f'\nProduct is not ready for {year}')
            print('------------------------------------------')


def main():

    # check_site_data_updates()
    collect_download_links()

    while True:

        print('\nMain Menu')
        print('Press 1: Download')
        print('Press 0: Quit')

        choice = int(input('Enter your choice: '))

        if choice == 0:
            break

        elif choice == 1:
            years = input('Enter the year(s)[Separate by comma in case of multiple years]: ')
            years = years.split(',')

            for i in range(len(years)):
                years[i] = years[i].strip()

            download_files(years)

main()

