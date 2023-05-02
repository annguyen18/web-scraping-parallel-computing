import csv
import multiprocessing
import time
import requests
from bs4 import BeautifulSoup

url = "https://itviec.com/viec-lam-it/java/ha-noi?job_selected=senior-fullstack-developer-java-javascript-typescript" \
      "-axlehire-1717&locale=vi&page={}&source=search_job "
headers = ({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58',
            'Accept-Language': 'en-US, en;q=0.5'})
# get the webpage
webpage = requests.get(url.format('1'))
# parse the webpage
soup = BeautifulSoup(webpage.content, "html.parser")

# Job Title | Job Location | Company's Name | Link

# find the number of pages by getting the text of the li next to the last li
pagination_ul = soup.find('ul', {'class': 'pagination'})
last_li = pagination_ul.find_all('li')[-1]
previous_li = last_li.find_previous_sibling('li')
# num_of_pages = int(previous_li.text)
# num_of_pages = 1

with open("jobs_details.csv", 'w', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter='\t')
    writer.writerow(['Job Title', 'Job Location', 'Company Name', 'Job Description'])


def scrape_page(page):
    print(f"Scraping page {page}...")
    # number of jobs per page
    num_of_jobs = 0

    # get the webpage of each job
    job_webpage = requests.get(url.format(str(page)))
    job_soup = BeautifulSoup(job_webpage.content, "html.parser")
    job_titles = job_soup.find_all('h3', {'class': 'title job-details-link-wrapper'})

    with open('jobs_details_parallel.csv', 'a', encoding='utf-8') as file:
        csv_writer = csv.writer(file, delimiter='\t')
        for t in job_titles:
            num_of_jobs += 1
            job_title = t.a.text.strip()
            # print("Job link: " + str(t.a.get('href')))

            # get the specific page of each job
            link_to_job = "https://itviec.com" + t.a.get('href')
            job_page = requests.get(link_to_job)
            job_soup = BeautifulSoup(job_page.content, "html.parser")
            divs = job_soup.find_all('div', {'class': 'svg-icon'})
            company_name = job_soup.find('h3',
                                         {'class': 'employer-long-overview__name hidden-xs d-none d-sm-block'}).a.text
            for div in divs:
                use = div.find('use')
                if use and use['xlink:href'] == '#location_icon':
                    # get job's location
                    location = div.div.span.text
                    csv_writer.writerow([job_title, location, company_name, link_to_job])
    return num_of_jobs

if __name__ == '__main__':
    num_of_pages = int(previous_li.text)
    pool = multiprocessing.Pool(processes=num_of_pages)
    start = time.time()
    results = []
    for page_number in range(1, num_of_pages + 1):
        result = pool.apply_async(scrape_page, args=(page_number,))
        results.append(result)

    num_of_jobs = 0
    for result in results:
        num_of_jobs += result.get()

    pool.close()
    pool.join()
    end = time.time()

    print(f"{num_of_jobs} jobs scraped in {end - start} seconds")