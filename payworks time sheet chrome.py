from selenium import webdriver
import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time 
from selenium.webdriver.support import expected_conditions as EC
import tkinter as tk
from tkinter import simpledialog

#get userame and password
ROOT = tk.Tk()

ROOT.withdraw()
# the input dialog
UsernameInput = simpledialog.askstring(title="Test",
                                  prompt="Username:")
PasswordInput = simpledialog.askstring(title="Test",
                                  prompt="Password:")

# the url for the page request
url = "https://payroll.payworks.ca/Scheduling/Employee/TimesheetSummary.aspx" 
page = requests.get(url)

# Initialize WebDriver (replace Chrome with FireFox or FireFox with Chrome)
options = Options()
options.add_argument('--headless=new')
driver = webdriver.Chrome(options)

# Open the URL
driver.get(url)

# Find elements by ID
payrollnum = driver.find_element(by="id", value="PayRollNum")
username = driver.find_element(by="id", value="UserName")
password = driver.find_element(by="id", value="Password")

# Input data into the fields
payrollnum.send_keys("E91180")
username.send_keys(UsernameInput)
password.send_keys(PasswordInput)

# Click the login button
driver.find_element(by="id", value="btnLogin").click()
time.sleep(1)
soup = BeautifulSoup(page.content, 'html.parser')

# goes to the next page ie. timesheet
nextpage = "https://payroll.payworks.ca/genericscreen.asp?sectionID=117&MainTitle=selfservice&SubTitle=timemanagement&SubPage=mytimesheet&MenuID=361"
page = requests.get(nextpage)
driver.get(nextpage)

# Wait for the page to load
time.sleep(1)

# Clicking pay period
driver.find_element(by="id", value="payPeriod").click()

# Wait for page to load
time.sleep(1)

# parse the HTML content using BeautifulSoup
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

# print the page title
print(driver.title)

# Wait for the timesheet entries to load
time.sleep(1)

# Find all the start and end times
start_times = driver.find_elements(By.NAME, "TimesheetEntryStartTime")
end_times = driver.find_elements(By.NAME, "TimesheetEntryEndTime")

# Compare the start and end times to see if they are less than 1 hour apart
diffs = []
for start, end in zip(start_times, end_times):
    start_time = datetime.strptime(start.text.strip(), '%I:%M %p')
    end_time = datetime.strptime(end.text.strip(), '%I:%M %p')
    diff = end_time - start_time
    if diff.total_seconds() < 3600:
        diffs.append((start.text, end.text))

# Print the number of times the difference was less than 1 hour
print(f"Looks like you may have missed {len(diffs)} time stamps.")
print(diffs)

# Wait for the alert to appear
time.sleep(1)  # Adjust as needed

#popup for missed punches
tk.messagebox.showinfo("Brooks Payworks Checker", f"Looks like you may have missed "+ f"{len(diffs)} time stamps.")
time.sleep(10)
exit()
