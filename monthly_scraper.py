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

        records[year] = dict()

        data = entry.find('ul').find_all('li', recursive = False)

        monthly_data = data[1].find('ul', recursive = False).find_all('li', class_ = 'submenu', recursive = False)

        for months in monthly_data:
            month = months.find('strong', recursive = False).text
            records[year][month] = dict()

            tiles = months.find('ul').find_all('li', class_ = 'submenu', recursive = False)

            for tile in tiles:

                tilename = tile.find('strong', recursive = False).text

                records[year][month][tilename] = dict()

                download_links = tile.find_all('li')

                for link in download_links:

                    try:
                        name = link.find('a').text
                        d_link = link.find('a')['href']
                        records[year][month][tilename][name] = d_link
                    except:
                        pass
 

def download_files(years):

    global records

    for year in years:

        if year in records:

            print(f'\nDownloading files for the year {year}')
            print('------------------------------------------')

            yearwise_path = os.path.join(os.getcwd(), year)

            if not os.path.exists(yearwise_path):
                os.mkdir(yearwise_path)

            for month in records[year]:

                print(f'\nDownloading files for the month {month} of {year}')
                print('--------------------------------------------')

                monthwise_path = os.path.join(yearwise_path, month)

                if not os.path.exists(monthwise_path):
                    os.mkdir(monthwise_path)

                for tilename in records[year][month]:
                    tilewise_path = os.path.join(monthwise_path, tilename)

                    if not os.path.exists(tilewise_path):
                        os.mkdir(tilewise_path)

                    for name in records[year][month][tilename]:

                        filename = name + '.tgz'
                        
                        file_path = os.path.join(tilewise_path, filename)

                        print(f'\nSearching "{file_path}" in the current directory -> ', end = '')
                        time.sleep(1)

                        download_site_response = requests.get(records[year][month][tilename][name], stream = True)
                        download_site_response.raise_for_status()

                        total_length = int(download_site_response.headers.get('content-length'))

                        # print(f'total length: -> {total_length}')

                        try :

                            if not os.path.exists(file_path):

                                print("NOT FOUND\n")
                                time.sleep(1)

                                print(f'\nDownloading "{file_path}"...\n')

                                with open(file_path, 'wb') as file:
                                    
                                    for chunk in progress.bar(download_site_response.iter_content(chunk_size=100000), expected_size=(total_length/100000) + 1):
                                        if chunk:
                                            file.write(chunk)
                                            file.flush()

                                print(f'\n"{file_path}" DOWNLOAD STATUS: OK!!')

                            else: 

                                file_size = os.stat(f'{file_path}')[6]

                                if file_size != total_length:

                                    print('INCOMPLETE/CURRUPTED FILE!')

                                    print(f'\n"Re-downloding {file_path}"...\n')

                                    with open(file_path, 'wb') as file:
                                        
                                        for chunk in progress.bar(download_site_response.iter_content(chunk_size=100000), expected_size=(total_length/100000) + 1):
                                            if chunk:
                                                file.write(chunk)
                                                file.flush()

                                else:

                                    print('FOUND\n')
                                    time.sleep(1)

                        except:

                            print(f'\nSome ERROR occurred while downloading "{file_path}"')

        else:
            print(f'\n{year} is an invalid year')


def main():

    collect_download_links()

    while True:

        print('\nMain Menu')
        print('Press 1: Download')
        print('Press 0: Quit')

        choice = int(input('Enter your choice: '))

        if choice == 0:
            break

        elif choice == 1:
            years = input('\nEnter the year(s)[Separate by comma in case of multiple years]: ')
            years = years.split(',')

            for i in range(len(years)):
                years[i] = years[i].strip()

            download_files(years)

        else:
            print('\nWrong Input!!Enter again!!')

main()

