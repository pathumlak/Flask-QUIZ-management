from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set up the Selenium WebDriver (make sure ChromeDriver is installed)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# URLs of the Flask application
login_url = "http://127.0.0.1:5000/login"
manage_students_url = "http://127.0.0.1:5000/admin/manage_students"

# Admin credentials
admin_credentials = {"username": "Admin", "password": "1212"}

def login_user(username, password):
    driver.get(login_url)
    
    # Find the username and password fields and the submit button
    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")
    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    
    # Fill in the fields and submit the form
    username_field.send_keys(username)
    password_field.send_keys(password)
    submit_button.click()
    
    try:
        # Wait until the page is redirected to dashboard or shows an error
        WebDriverWait(driver, 10).until(
            EC.url_contains("/dashboard") or EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Invalid username or password!")
        )
    except Exception as e:
        print(f"Exception occurred: {e}")

def grant_all_users_access():
    driver.get(manage_students_url)
    
    try:
        # Wait until the manage students page is loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Grant All Students Access')]"))
        )

        # Click the grant all access button
        grant_all_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Grant All Students Access')]")
        grant_all_button.click()
        
        # Wait for a success message or redirection
        WebDriverWait(driver, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Access granted to all users") or EC.url_contains("/admin/manage_students")
        )
    
    except Exception as e:
        print(f"Exception occurred: {e}")

# Log in as the admin
login_user(admin_credentials["username"], admin_credentials["password"])

# Grant all users access
grant_all_users_access()

# Close the browser
driver.quit()
