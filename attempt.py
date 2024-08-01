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
exam_url = "http://127.0.0.1:5000/exam"

# Test user credentials
testuser_credentials = {"username": "testuser1", "password": "password1"}

# Mapping of question text to correct answers
correct_answers = {
    "What is the capital of France?": "Paris",
    "What is 2 + 2?": "4",
    "What is the color of the sky?": "Blue",
    "What is the boiling point of water?": "100°C",
    "What is the largest planet in our solar system?": "Jupiter"
}

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

def attempt_exam():
    driver.get(exam_url)
    
    try:
        # Wait until the exam page is loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )

        # Find all quiz questions
        questions = driver.find_elements(By.CLASS_NAME, "question")
        
        for question in questions:
            question_text = question.find_element(By.TAG_NAME, "p").text
            correct_answer = correct_answers.get(question_text)
            
            if correct_answer:
                # Find the correct option for this question
                options = question.find_elements(By.CLASS_NAME, "radio-label")
                for option in options:
                    if option.text == correct_answer:
                        option.find_element(By.TAG_NAME, "input").click()
                        break
        
        # Submit the exam
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()
        
        # Wait until the results page is loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='result']"))
        )

        # Get the results
        result = driver.find_element(By.XPATH, "//div[@id='result']")
        print(result.text)
    
    except Exception as e:
        print(f"Exception occurred: {e}")

# Log in as the test user
login_user(testuser_credentials["username"], testuser_credentials["password"])

# Attempt the exam
attempt_exam()

# Close the browser
driver.quit()
