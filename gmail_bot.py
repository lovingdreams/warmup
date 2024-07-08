import argparse
import json
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def search_emails(query, driver):
    search_box = WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.NAME, "q")))
    search_box.clear()
    search_box.send_keys(query + Keys.RETURN)


# Function to click the first email
def click_first_email(driver):
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="main"] .zA.zE')))
        # Assuming '.zA.zE' are classes for emails in the list, specifically first unread or read in the list
        emails = driver.find_elements(By.CSS_SELECTOR, 'div[role="main"] .zA.zE')
        if emails:
            ActionChains(driver).move_to_element(emails[0]).click().perform()
            print("Opened the first email")
            return True
        else:
            print("No emails found in the search results.")
    except Exception as err:
        print("Failed to find the first email on the page: ", err)


def mark_as_important(driver):
    try:
        # List all elements that match and check their visibility
        elements = driver.find_elements(By.CSS_SELECTOR, 'div[aria-label="More email options"]')
        for idx, elem in enumerate(elements):
            if elem.is_displayed() and elem.size["height"] > 0 and elem.size["width"] > 0:
                print(f"Interactable Element found at index {idx}")
                elem.click()
                break
        else:
            print("No interactable elements were found.")

        print("Clicked on the 'More email options' button.")

        # Wait until the clickable element containing "Mark as important" is present
        important_marker = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Mark as important']")))
        important_marker.click()
        print("Marked as important")
    except Exception as err:
        print("Failed to click on the button: ", err)


# TODO: Send Analytics
def send_reply(reply_body, analytics_api, driver):
    try:
        # Locate the reply button and click it
        reply_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[aria-label="Reply"]')))
        reply_button.click()

        # Wait for the reply text area to become active and type a response
        reply_text_area = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Message Body"]')))
        reply_text_area.click()
        # reply_text_area.send_keys('Thank you for your email.')

        # Convert HTML to plain text
        soup = BeautifulSoup(reply_body, "html.parser")
        plain_text_content = soup.get_text()

        reply_text_area.send_keys(plain_text_content)

        # Locate the send button and click it
        # Wait for the obstructing element to disappear
        WebDriverWait(driver, 120).until(EC.invisibility_of_element_located((By.ID, "link_enable_notifications_hide")))

        # Click the Send button
        send_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//div[text()="Send"]')))
        send_button.click()
        print("reply sent")
        try:
            analytics_api += "&eventType=replied&warmup=true"
            reply_sent_api_response = requests.get(url=analytics_api)
            reply_sent_api_response = reply_sent_api_response.json()
            print("reply_sent_api_response --->", reply_sent_api_response)
        except Exception as err:
            print("reply_sent_api exception: ", err)
        time.sleep(5)
        driver.implicitly_wait(5)
    except Exception as err:
        print("Failed to send the reply: ", err)


def click_on_star(driver):
    try:
        star_to_click = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[role='checkbox'][aria-label='Not starred'][aria-checked='false']")))
        star_to_click.click()
        print("Starred the email")
    except Exception as err:
        print("Failed to star the email: ", err)


# TODO: Send Analytics
def perform_spam_action(from_email, reply_body, analytics_api, driver):
    try:
        # Wait for the "More" button to be clickable and click it
        more_button = WebDriverWait(driver, 120).until(EC.element_to_be_clickable((By.XPATH, '//span[text()="More"]')))
        more_button.click()

        # Wait for the "Spam" folder to be visible and clickable and click it
        spam_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "spam")]')))
        spam_button.click()
        print("Inside spam")

        time.sleep(5)
        driver.implicitly_wait(5)

        search_emails(f"in:spam {from_email}", driver)
        time.sleep(5)
        driver.implicitly_wait(5)

        if click_first_email(driver):
            time.sleep(5)
            driver.implicitly_wait(5)

            if reply_body:
                send_reply(reply_body, analytics_api, driver)
                time.sleep(5)
                driver.implicitly_wait(5)

                click_on_star(driver)
                time.sleep(5)
                driver.implicitly_wait(5)

            # Wait for the "Report not spam" button to be clickable and click it
            not_spam_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Report as not spam")]')))
            not_spam_button.click()
            time.sleep(5)
            driver.implicitly_wait(5)
            print("Spam action completed")
            try:
                analytics_api += "&eventType=savedFromSpam&warmup=true"
                spam_action_api_response = requests.get(url=analytics_api)
                spam_action_api_response = spam_action_api_response.json()
                print("spam_action_api_response --->", spam_action_api_response)
            except Exception as err:
                print("spam_action_api exception: ", err)
        else:
            print("Email not found in spam")
    except Exception as err:
        print("Spam action failed: ", err)


def logout(driver):
    try:
        # Wait until the avatar is clickable and then click it
        avatar = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "SignOutOptions")]')))
        avatar.click()
        print("Clicked on Avatar")

        time.sleep(15)
        driver.implicitly_wait(15)
        actions = ActionChains(driver)
        actions.send_keys(Keys.TAB * 4)
        actions.send_keys(Keys.ENTER)
        actions.perform()
        print("Logout success")
    except Exception as err:
        print("Failed to perform logout: "), err


def bot(email, password, from_mail, reply_body, message_id, analytics_url, driver):
    try:
        analytics_api = analytics_url + message_id
        # Login
        try:
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "identifierId"))).send_keys(email + Keys.ENTER)
            time.sleep(5)
            driver.implicitly_wait(5)
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, "Passwd"))).send_keys(password + Keys.ENTER)

            try:
                first_time_confirm_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "confirm")))
                first_time_confirm_button.click()
            except Exception as err:
                print("first_time_confirm_button exception:", err)

            try:
                close_button = driver.find_element(By.XPATH, '//span[@aria-label="Close"]')
                close_button.click()
            except Exception as err:
                print("first_time_confirm_button closing exception:", err)
        except Exception as err:
            print("Login failed:", err)
            driver.quit()

        # Ensure the inbox page is loaded
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, "q")))

        time.sleep(5)
        driver.implicitly_wait(5)

        # Searching in Inbox
        search_emails(f"from:{from_mail}", driver)

        time.sleep(5)
        driver.implicitly_wait(5)

        # Opening first email
        if click_first_email(driver):
            time.sleep(5)
            driver.implicitly_wait(5)

            mark_as_important(driver)
            time.sleep(5)
            driver.implicitly_wait(5)

            if reply_body:
                send_reply(reply_body, analytics_api, driver)
                time.sleep(5)
                driver.implicitly_wait(5)

                click_on_star(driver)
                time.sleep(5)
                driver.implicitly_wait(5)
        else:
            # Perform spam action
            perform_spam_action(from_mail, reply_body, analytics_api, driver)
            time.sleep(5)
            driver.implicitly_wait(5)

        print("Bot action completed:")
        logout(driver)
        time.sleep(5)
        driver.implicitly_wait(5)
        try:
            analytics_api += "&warmup=true"
            warm_up_api_response = requests.get(url=analytics_api)
            warm_up_api_response = warm_up_api_response.json()
            print("warm_up_api_response --->", warm_up_api_response)
        except Exception as err:
            print("warm_up_api exception: ", err)
    except Exception as err:
        print("Bot exception:", err)
        driver.quit()


def main():
    # Initialize the parser
    parser = argparse.ArgumentParser(description="A script to demonstrate command-line arguments")

    # Add a single argument for JSON data
    parser.add_argument("--data", type=str, help="JSON data", required=True)

    # Parse the arguments
    args = parser.parse_args()

    # Parse the JSON data
    data = json.loads(args.data)

    # options = webdriver.ChromeOptions()
    # options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_experimental_option("useAutomationExtension", False)
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 2})  # 1: allow, 2: block

    # CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"
    # service = ChromeService(executable_path=CHROMEDRIVER_PATH)
    # driver = webdriver.Chrome(service=service, options=options)

    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("useAutomationExtension", True)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = webdriver.Chrome(options=options)
    driver.get("https://mail.google.com/")
    time.sleep(5)
    driver.implicitly_wait(5)

    driver.maximize_window()
    time.sleep(5)
    driver.implicitly_wait(5)

    # bot("saic64711@gmail.com", "9949127878", "astridsmi230@gmail.com", "Hey hey", driver)
    bot(data["email"], data["password"], data["emailData"]["sender"], data["replyContent"], data["emailData"]["messageId"], data["analytics_url"], driver)
    print("Closing the browser")
    driver.quit()


if __name__ == "__main__":
    main()