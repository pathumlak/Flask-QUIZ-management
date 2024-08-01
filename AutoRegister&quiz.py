from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set up the Selenium WebDriver (make sure ChromeDriver is installed)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# URLs of the Flask application
register_url = "http://127.0.0.1:5000/register"
login_url = "http://127.0.0.1:5000/login"
quiz_url = "http://127.0.0.1:5000/admin/quiz"

# List of users to register
users = [
    {"username": "testuser1", "password": "password1"},
    {"username": "testuser2", "password": "password2"},
    {"username": "testuser3", "password": "password3"},
]

# Admin credentials
admin_credentials = {"username": "Admin", "password": "1212"}

# List of quizzes to add
quizzes = [
    {"question": "What is the capital of France?", "options": ["Paris", "London", "Berlin", "Madrid"], "correct_answer": "Paris"},
    {"question": "What is 2 + 2?", "options": ["3", "4", "5", "6"], "correct_answer": "4"},
    {"question": "What is the color of the sky?", "options": ["Blue", "Green", "Red", "Yellow"], "correct_answer": "Blue"},
    {"question": "What is the boiling point of water?", "options": ["90°C", "95°C", "100°C", "105°C"], "correct_answer": "100°C"},
    {"question": "What is the largest planet in our solar system?", "options": ["Earth", "Mars", "Jupiter", "Saturn"], "correct_answer": "Jupiter"}
]

def register_user(user):
    driver.get(register_url)
    
    # Find the username and password fields and the submit button
    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")
    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    
    # Fill in the fields and submit the form
    username_field.send_keys(user["username"])
    password_field.send_keys(user["password"])
    submit_button.click()
    
    try:
        # Wait until the page is redirected to login or shows an error
        WebDriverWait(driver, 10).until(
            EC.url_contains("/login") or EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Username already exists!")
        )
    except Exception as e:
        print(f"Exception occurred: {e}")

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

def add_quiz(quiz):
    driver.get(quiz_url)
    
    # Find the quiz form fields and submit button
    question_field = driver.find_element(By.NAME, "question")
    option1_field = driver.find_element(By.NAME, "option1")
    option2_field = driver.find_element(By.NAME, "option2")
    option3_field = driver.find_element(By.NAME, "option3")
    option4_field = driver.find_element(By.NAME, "option4")
    correct_answer_field = driver.find_element(By.NAME, "correct_answer")
    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    
    # Fill in the fields and submit the form
    question_field.send_keys(quiz["question"])
    option1_field.send_keys(quiz["options"][0])
    option2_field.send_keys(quiz["options"][1])
    option3_field.send_keys(quiz["options"][2])
    option4_field.send_keys(quiz["options"][3])
    correct_answer_field.send_keys(quiz["correct_answer"])
    submit_button.click()
    
    try:
        # Wait until the page is redirected or shows a success message
        WebDriverWait(driver, 10).until(
            EC.url_contains("/admin/quiz") or EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Quiz added successfully!")
        )
    except Exception as e:
        print(f"Exception occurred: {e}")

# Run the registration process for each user
for user in users:
    register_user(user)
    # Wait for a few seconds before registering the next user
    time.sleep(2)

# Log in as the admin
login_user(admin_credentials["username"], admin_credentials["password"])

# Add quizzes
for quiz in quizzes:
    add_quiz(quiz)
    # Wait for a few seconds before adding the next quiz
    time.sleep(2)

# Close the browser
driver.quit()
