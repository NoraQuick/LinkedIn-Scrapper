#Import packages for web scrapping and logging
import logging
import random
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

print("Starting timer...")
start_time = time.time()

logging.basicConfig(filename="scraping.log", level=logging.INFO)

def LI_job_scrape(job_title: str, location: str, pages: int = None) -> list:
    #Find jobs based on their job title and location
    logging.info(f'Starting LinkedIn job scrape for "{job_title}" in "{location}"...')

    #Set the pages to scrape
    pages = pages or 1

    #Set up the Selenium we driver
    #driver = webdriver.Chrome("chromedriver.exe")
    driver = webdriver.Chrome()

    #Go to LinkedIn job search page with the given job title and location
    driver.get(f"https://linkedin.com/jobs/search/?keywords={job_title}&location={location}")

    #Scroll through the set number of pages
    for i in range(pages):
        logging.info(f"Scrolling to bottom of page {i+1}...")

        #Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located(By.XPATH, "/html/body/div[1]/div/main/section[2]/button"))
            #Click "show more"
            element.click()

        except Exception:
            logging.info("Show more button not found, retrying...")

        #Wait a random amount of time before scrolling to the next page
        time.sleep(random.choice(list(range(3, 7))))

    #Scrape the job posting
    jobs = []
    soup_parse = BeautifulSoup(driver.page_source, "html.parser")
    job_listings = soup_parse.find_all("div",
                                 class_="base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card",)
    
    try:
        #Get the info I want
        for job in job_listings:
            #Get the job title (should have already been specified)
            job_title = job.find("h3", class_="base-search-card__title").text.strip()

            #Get the company
            job_company = job.find("h4", class_="base-search-card__subtitle").text.strip()

            #Get the job location (should have already been specified)
            job_location = job.find("span", class_="job-search-card__location").text.strip()

            #Get the link
            job_link = job.find("a", class_="base-card__full-link")["href"]

            #Sleep again
            time.sleep(random.choice(list(range(5,11))))

            #Combine all the info together
            jobs.append({
                "title": job_title,
                "company": job_company,
                "location": job_location,
                "link": job_link,
            })

            logging.info(f'Scraped "{job_title}" at {job_company} in {job_location}...')

    except Exception as e:
        logging.error(f"An error occurred while scraping jobs: {str(e)}")

        #Return the existing list so we save some info found
        return jobs
    
    #Close the Seleium web driver
    driver.quit()

    #Return the completed (or non-completed) list of jobs found
    return jobs


def save_jobs_csv(data: dict) -> None:
    df = pd.DataFrame(data)

    #Save info to a csv
    df.to_csv("DataAnalyst_Boston.csv", index=False)


data = LI_job_scrape("Data Analyst", "Boston, Massachusetts", 5)
save_jobs_csv(data)


print("--- %s seconds ---" % (time.time() - start_time))
