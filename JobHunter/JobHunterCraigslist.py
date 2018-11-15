# This script pulls from a job website and stores positions into a database. If there is a new posting it notifies the user.
# CNA 330
# Zachary Rubin, zrubin@rtc.edu
import mysql.connector
import sys
import json
import requests
import os
import time

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
		Craig_ID TEXT UNIQUE); ''')
    return

# Query the database.
# You should not need to edit anything in this function
def query_sql(cursor, query):
    cursor.execute(query)
    return cursor

# Add a new job
def add_new_job(cursor, jobdetails):
    query = """INSERT IGNORE INTO Jobs (PostDate, Title, Location, Description, Company, Apply_info, Craig_ID) VALUES (
	"''' + jobdetails['created_at'] + '''",
	"''' + jobdetails['title'] + '''",
	"''' + jobdetails['location'] + '''",
	"''' + jobdetails['description'] + '''",
	"''' + jobdetails['company'] + '''",
	"''' + jobdetails['how_to_apply'] + '''",
	"''' + jobdetails['id'] + '''")"""
    return query_sql(cursor, query)

# Check if new job
def check_if_job_exists(cursor, jobdetails):
    query = """SELECT EXISTS(SELECT * FROM Jobs WHERE jobdetails['id'])"""
    return query_sql(cursor, query)

# Delete given job
def delete_job(cursor, jobdetails):
    query = """DELETE FROM Jobs WHERE Craig_ID=jobdetails['id']"""
    return query_sql(cursor, query)

# Grab new jobs from a website
def fetch_new_jobs(cursor, arg_dict, url):
    r = requests.get(url) #Get page
    soup = BeautifulSoup(r.text, 'html.parser')
    job_links = soup.find_all('li', class_='result-row') #Find all job listings
	for job in job_links: #Get single job
		jobdetails['id'] = job['data-pid']
		jobdetails['title'] = job.p.a.string #Get title of job
		jobdetails['created_at'] = job.time['datetime'] #Get date posted of job
		
		job_location = job.p.a.next_sibling.next_sibling.find('span', class_='result-hood') #Get location of job
		try:
			jobdetails['location'] = job_location.replace('(', '').replace(')', '') #Clean output
		except:
			jobdetails['location'] = "No location given"
		
		joburl = job.a['href'] #Get url for job
		jobdetails['how_to_apply'] = joburl
		
		jobr = requests.get(joburl) #Delve into each job link and get compensation and description
		jobsoup = BeautifulSoup(jobr.text, 'html.parser')
		jobdetails['salary'] = jobsoup.find('p', class_='attrgroup').span.text #Get compensation
		
		jobdesc = jobsoup.find('section', id='postingbody') #Get description of job and clean output
		jobdetails['description'] = jobdesc.text.replace('\n', ' ').replace('\t', ' ')[30:] #[30:] cleans the first 30 characters referencing a QR code
		
	return jobdetails
	
# Load a text-based configuration file
def load_config_file(filename):
    argument_dictionary = []
    # Code from https://github.com/RTCedu/CNA336/blob/master/Spring2018/FileIO.py
    rel_path = os.path.abspath(os.path.dirname(__file__))
    file = 0
    file_contents = 0
    try:
        file = open(filename, "r")
        #file_contents = file.read()
    except FileNotFoundError:
        print("File not found, it will be created.")
        file = open(filename, "w")
        file.write("")
        file.close()
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
    from bs4 import BeautifulSoup

    url = "https://seattle.craigslist.org/search/jjj"
    jobdetails = fetch_new_jobs(cursor, arg_dict, url)
	add_new_job(cursor, jobdetails)
    ## Add in your code here to check if the job already exists in the DB

    ## Add in your code here to notify the user of a new posting

    ## EXTRA CREDIT: Add your code to delete old entries

# Setup portion of the program. Take arguments and set up the script
# You should not need to edit anything here.
def main():
    # Connect to SQL and get cursor
    conn = connect_to_sql()
    cursor = conn.cursor()
    create_tables(cursor, "table")
    # Load text file and store arguments into dictionary
    arg_dict = load_config_file(sys.argv[1])
    while(1):
        jobhunt(cursor, arg_dict)
        conn.commit()
        time.sleep(3600) # Sleep for 1h


if __name__ == '__main__':
    main()
