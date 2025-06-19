import os
import time
import pandas as pd
import random #<-- IMPORTED for polite pause
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# --- Configuration ---
queries_path = 'query.csv'
queries = []

# --- Load Search Queries ---
if os.path.exists(queries_path):
    try:
        df = pd.read_csv(queries_path)
        if 'Query' in df.columns:
            queries = df['Query'].dropna().tolist() # Added .dropna() to remove empty rows
            print(f"Loaded {len(queries)} queries from {queries_path}.")
        else:
            print(f"Error: 'Query' column not found in {queries_path}.")
    except Exception as e:
        print(f"Error loading queries from {queries_path}: {e}")

# --- Proceed only if queries were loaded ---
if not queries:
    print("No queries to process. Exiting.")
    exit()

# --- Setup WebDriver ---
service = Service(executable_path='msedgedriver.exe')
driver = webdriver.Edge(service=service)
driver.maximize_window()

# --- This list will store all our results ---
scraped_data = []
first_run = True # Helper to only check for cookie banner on the first run

# --- Start Scraping Loop ---
for query in queries:
    print(f"\n--- Starting search for: {query} ---")
    query_url = quote(query)
    url = f"https://www.google.com/search?q={query_url}&tbm=isch"

    print(f"Navigating to: {url}")
    driver.get(url)

    # --- Handle Cookie Consent Banner (only on the first navigation) ---
    if first_run:
        consent_button_xpaths = [
            "//button[.//div[text()='Accept all']]",
            "//button[.//div[text()='Reject all']]",
            "//div[text()='I agree']"
        ]
        try:
            print("Checking for cookie consent banner...")
            for xpath in consent_button_xpaths:
                try:
                    consent_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                    print(f"Found and clicked consent button.")
                    consent_button.click()
                    time.sleep(2)
                    break
                except TimeoutException:
                    continue
            first_run = False # Don't check again
        except Exception as e:
            print(f"Could not click consent button, continuing anyway. Error: {e}")
            first_run = False # Don't check again

    # --- Scroll to Load More Images ---
    print("Scrolling to load more images...")
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    # --- Find and Process Image Elements ---
    try:
        print("Waiting for image elements to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'img.YQ4gaf'))
        )
        img_elements = driver.find_elements(By.CSS_SELECTOR, 'img.YQ4gaf')
        print(f"Found {len(img_elements)} image elements for '{query}'.")

        # --- Loop through images and save their URLs ---
        url_count = 0
        for img in img_elements:
            if url_count > 15:  # Limit to 15 URLs per query
                print("Reached the limit of 15 URLs for this query. Stopping further processing.")
                break
            try:
                img_url = img.get_attribute("src")
                if img_url and img_url.startswith('http'):
                    scraped_data.append({'Query': query, 'Image URL': img_url})
                    url_count += 1
            except Exception as e:
                print(f"Could not process an image. Error: {e}")
                continue
        print(f"Added {url_count} valid image URLs for this query.")

    except TimeoutException:
        print("Timeout: No image elements were found for this query.")
    except Exception as e:
        print(f"An error occurred while finding image elements: {str(e)}")

    # --- Polite pause between queries ---
    pause_duration = random.uniform(4, 8)
    print(f"Pausing for {pause_duration:.2f} seconds before next query...")
    time.sleep(pause_duration)


# --- Cleanup AFTER the Loop ---
print("\n--- All queries processed. Closing browser. ---")
driver.quit()

# --- Save Reults to CSV ---
if scraped_data:
    print("Saving all collected data to a single CSV file...")
    df_results = pd.DataFrame(scraped_data)
    current_directory = os.getcwd()
    # Use a generic filename for the consolidated results
    csv_filename = 'query_results.csv'
    csv_path = os.path.join(current_directory, csv_filename)
    df_results.to_csv(csv_path, index=False)
    print(f"Success! All data saved to: {csv_path}")
else:
    print("No image URLs were found across all queries.")