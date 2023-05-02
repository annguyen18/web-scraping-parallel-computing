import csv
import requests
from bs4 import BeautifulSoup
import time
# url = "https://api.nytimes.com/svc/books/v3/lists/2023-04-11/combined-print-and-e-book-fiction.json?api-key
# =fIqdlL4wAvNIopU2HuHTe2E29gA1CnAa"
url = "https://itviec.com/viec-lam-it/java/ha-noi?job_selected=senior-fullstack-developer-java-javascript-typescript" \
      "-axlehire-1717&locale=vi&page={}&source=search_job "
headers = ({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58',
           'Accept-Language': 'en-US, en;q=0.5'})

# start the time execution
start = time.time()

# get the webpage
webpage = requests.get(url.format('1'))
# parse the webpage
soup = BeautifulSoup(webpage.content, "html.parser")

# Job Title | Job Location | Company's Name | Link

# find the number of pages by getting the text of the li next to the last li
pagination_ul = soup.find('ul', {'class': 'pagination'})
last_li = pagination_ul.find_all('li')[-1]
previous_li = last_li.find_previous_sibling('li')
num_of_pages = int(previous_li.text)
# num_of_pages = 1
page = 1
num_of_jobs = 0
with open("jobs_details.csv", 'w', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter='\t')
    writer.writerow(['Job Title', 'Job Location', 'Company Name', 'Job Description'])
while page <= num_of_pages:
    webpage = requests.get(url.format(str(page)))
    soup = BeautifulSoup(webpage.content, "html.parser")
    job_titles = soup.find_all('h3', {'class': 'title job-details-link-wrapper'})

    with open('jobs_details_serial.csv', 'a', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        for t in job_titles:
            num_of_jobs += 1
            job_title = t.a.text.strip()
            # print("Job link: " + str(t.a.get('href')))

            # get the specific page of each job
            link_to_job = "https://itviec.com" + t.a.get('href')
            job_page = requests.get(link_to_job)
            soup = BeautifulSoup(job_page.content, "html.parser")
            divs = soup.find_all('div', {'class': 'svg-icon'})
            company_name = soup.find('h3', {'class': 'employer-long-overview__name hidden-xs d-none d-sm-block'}).a.text
            for div in divs:
                use = div.find('use')
                if use and use['xlink:href'] == '#location_icon':
                    # get job's location
                    location = div.div.span.text
                    writer.writerow([job_title, location, company_name, link_to_job])
    page += 1

# end the time execution
end = time.time()

print(f"{num_of_jobs} jobs scraped in {end - start} seconds")
