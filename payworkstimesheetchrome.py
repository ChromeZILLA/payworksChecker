
import selenium.webdriver as webdriver
import requests
import time
import tkinter as tk
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from datetime import datetime
from tkinter import simpledialog 


# Function to save credentials to a JSON file
def save_credentials(company_number, username):
    data = {
        "CompanyNumber": company_number,
        "Username": username
    }
    with open("credentials.json", "w") as f:
        json.dump(data, f)

# Function to load saved credentials from a JSON file
def load_credentials():
    try:
        with open("credentials.json", "r") as f:
            data = json.load(f)
            return data["CompanyNumber"], data["Username"]
    except FileNotFoundError:
        return None, None

# get userame and password
class MultiInputDialog(tk.Toplevel):
    def __init__(self, parent, title, prompts):
        super().__init__(parent)
        self.title(title)
        self.prompts = prompts
        self.entries = []

        for i, (prompt, show_password) in enumerate(prompts):
            label = tk.Label(self, text=prompt)
            label.grid(row=i, column=0, padx=5, pady=5, sticky="e")
            entry = tk.Entry(self, show='*' if show_password else None)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            self.entries.append(entry)

        button_frame = tk.Frame(self)
        button_frame.grid(row=len(prompts), columnspan=2, padx=5, pady=5)
        ok_button = tk.Button(button_frame, text="OK", command=self.ok)
        ok_button.pack(side="left", padx=10)
        cancel_button = tk.Button(button_frame, text="Cancel", command=self.cancel)
        cancel_button.pack(side="right", padx=10)

        # Bind the <Return> event to the OK button
        self.bind("<Return>", lambda event: ok_button.invoke())

    def ok(self):
        self.values = [entry.get() for entry in self.entries]
        self.destroy()

    def cancel(self):
        self.values = None
        self.destroy()

def get_user_input(prompts, title):
    root = tk.Tk()
    root.withdraw()
    dialog = MultiInputDialog(root, title, prompts)
    root.wait_window(dialog)
    return dialog.values

# Define prompts for each input field
prompts = [
    ("Company Number:", False),
    ("Username:", False),
    ("Password:", True)  # Show asterisks for password
]

# Get user input using the custom dialog
user_inputs = get_user_input(prompts, "Payworks Checker")

# Ensure all inputs are provided
if user_inputs is None or any(input_field.strip() == "" for input_field in user_inputs):
    print("All fields are required. Exiting.")
    exit()

# Unpack the user inputs
CoNumber, UsernameInput, PasswordInput = user_inputs

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

# please wait (Taken out for now)
#tk.messagebox.showinfo("Payworks Checker", f"Loading please wait.")

# Input data into the fields
payrollnum.send_keys(CoNumber)
username.send_keys(UsernameInput)
password.send_keys(PasswordInput)

# Click the login button
driver.find_element(by="id", value="btnLogin").click()
time.sleep(1)

# goes to the next page ie: timesheet
nextpage = "https://payroll.payworks.ca/genericscreen.asp?sectionID=117&MainTitle=selfservice&SubTitle=timemanagement&SubPage=mytimesheet&MenuID=361"
page = requests.get(nextpage)
driver.get(nextpage)

# Wait for the page to load,Adjust as needed
time.sleep(1)

# Clicking pay period
driver.find_element(by="id", value="payPeriod").click()

# Wait for page to load, Adjust as needed
time.sleep(1)

# print the page title
print(driver.title)

# Wait for the timesheet entries to load, Adjust as needed
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

# Wait for the alert to appear, Adjust as needed
time.sleep(1)

# Display a popup for missed punches
tk.messagebox.showinfo("Payworks Checker", f"Looks like you may have missed "+ f"{len(diffs)} time stamps.")

# Wait time, the promt will close. Adjust as needed
time.sleep(2)

# Close the application
import sys
sys.exit()
