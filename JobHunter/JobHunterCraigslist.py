# This script pulls from a job website and stores positions into a database. If there is a new posting it notifies the user.
# CNA 330
# Zachary Rubin, zrubin@rtc.edu
import mysql.connector
import sys
import requests
import os
import time
from bs4 import BeautifulSoup

# Connect to database
# You should not need to edit anything in this function
def connect_to_sql():
    conn = mysql.connector.connect(user='root', password='',
                                  host='127.0.0.1',
                                  database='cna330')
    return conn

# Create the table structure
def create_tables(cursor, table):
    ## Add your code here. Starter code below
    cursor.execute('''CREATE TABLE IF NOT EXISTS Jobs (
        ID int NOT NULL PRIMARY KEY AUTO_INCREMENT, 
        PostDate TEXT, 
        Title TEXT, 
        Location TEXT, 
        Description TEXT, 
        Company TEXT, 
        Apply_info TEXT, 
        Salary FLOAT, 
        RawMessage TEXT, 
        Craig_ID VARCHAR(12) UNIQUE); ''')
    return

# Add a new job
insert_stmt = (
    "INSERT IGNORE INTO Jobs (PostDate, Title, Location, Description, Apply_info, Craig_ID) "
    "VALUES (%(created_at)s, %(title)s, %(location)s, %(description)s, %(how_to_apply)s, %(id)s)"
)
# Check if new job
check_stmt = """SELECT EXISTS(SELECT * FROM Jobs WHERE %(id)s)"""
# Delete given job
delete_stmt = """DELETE FROM Jobs WHERE Craig_ID = %(id)s"""

# Grab new jobs from a website
def fetch_new_job(arg_dict, job, jobdetails):
    jobdetails['title'] = str(job.p.a.string) #Get title of job
    jobdetails['created_at'] = str(job.time['datetime']) #Get date posted of job
    
    #Get location of job
    try:
        job_location = job.p.a.next_sibling.next_sibling.find('span', class_='result-hood').text
        jobdetails['location'] = str(job_location.replace('(', '').replace(')', '')) #Clean output
    except:
        jobdetails['location'] = "No location given"
    
    joburl = job.a['href'] #Get url for job
    jobdetails['how_to_apply'] = str(joburl)
    
    #Delve into each job link and get compensation and description
    jobr = requests.get(joburl) 
    jobsoup = BeautifulSoup(jobr.text, 'html.parser')
    jobdetails['salary'] = str(jobsoup.find('p', class_='attrgroup').span.text) #Get compensation
    
    #Get description of job and clean output
    jobdesc = jobsoup.find('section', id='postingbody') 
    jobdetails['description'] = str(jobdesc.text.replace('\n', ' ').replace('\t', ' ')[30:]) #[30:] cleans the first 30 characters referencing a QR code
    
    return jobdetails
    
# Load a text-based configuration file
def load_config_file():
    argument_dictionary = []
    file = 0
    # Code from https://github.com/RTCedu/CNA336/blob/master/Spring2018/FileIO.py
    try:
        filename = sys.argv[1]
        file = open(filename, "r")
    except (FileNotFoundError, IndexError):
        print("File not found, it will be created.")
        filename = os.path.join(os.path.dirname(__file__), 'cntconfig.txt')
        file = open(filename, "w+")

    #Read each line of file and add it to a list
    for aline in file:
        aline = aline.strip()
        argument_dictionary.append(aline)

    file.close()
    return argument_dictionary

# Main area of the code.
def jobhunt(cursor, arg_dict):
    # Fetch jobs from website
    ## Add your code here to parse the job page

    url = "https://seattle.craigslist.org/search/jjj"
    r = requests.get(url) #Get page
    soup = BeautifulSoup(r.text, 'html.parser')
    job_links = soup.find_all('li', class_='result-row') #Find all job listings
    for job in job_links: #Get single job
        jobdetails = {}
        jobdetails['id'] = job['data-pid'] #Get ID of job
        if not cursor.execute(check_stmt, jobdetails): #Check if ID of job already exists in DB
            jobdetails = fetch_new_job(arg_dict, job, jobdetails)
            cursor.execute(insert_stmt, jobdetails)
            print("Job " + jobdetails['title'] + " added.")
            
    ## Add in your code here to check if the job already exists in the DB

    ## Add in your code here to notify the user of a new posting

    ## EXTRA CREDIT: Add your code to delete old entries

# Setup portion of the program. Take arguments and set up the script
# You should not need to edit anything here.
def main():
    # Connect to SQL and get cursor
    conn = connect_to_sql()
    cursor = conn.cursor(buffered=True)
    create_tables(cursor, "table")
    # Load text file and store arguments into dictionary
    arg_dict = load_config_file()
    while(1):
        jobhunt(cursor, arg_dict)
        conn.commit()
        time.sleep(3600) # Sleep for 1h


if __name__ == '__main__':
    main()
