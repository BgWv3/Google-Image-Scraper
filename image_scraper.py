import os
import time
import json
import pandas as pd
import random
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from rich.progress import Progress, TimeElapsedColumn, TimeRemainingColumn, BarColumn, TextColumn
from rich.console import Console

# --- Configuration ---
queries_path = 'query.csv'
progress_path = 'progress.json'
result_path = 'query_results.csv'
queries = []
console = Console()

# --- Load Queries ---
if os.path.exists(queries_path):
    try:
        df = pd.read_csv(queries_path)
        if 'Query' in df.columns:
            queries = df['Query'].dropna().tolist()
            console.print(f"[green]Loaded {len(queries)} queries from {queries_path}.[/green]")
        else:
            console.print(f"[red]Error: 'Query' column not found in {queries_path}.[/red]")
            exit()
    except Exception as e:
        console.print(f"[red]Error loading queries: {e}[/red]")
        exit()
else:
    console.print(f"[red]{queries_path} not found.[/red]")
    exit()

# --- Resume Progress ---
completed = set()
if os.path.exists(progress_path):
    with open(progress_path, 'r') as f:
        completed = set(json.load(f))

# --- Setup WebDriver ---
service = Service(executable_path='msedgedriver.exe')
driver = webdriver.Edge(service=service)
driver.maximize_window()

# --- Timer ---
start_time = time.time()
first_run = True

# --- Progress Bar ---
with Progress(
    TextColumn("[bold blue]{task.description}"),
    BarColumn(),
    "[progress.percentage]{task.percentage:>3.1f}%",
    TimeElapsedColumn(),
    TimeRemainingColumn(),
    console=console
) as progress:
    task = progress.add_task("Scraping", total=len(queries))

    for query in queries:
        if query in completed:
            progress.advance(task)
            continue

        console.print(f"\n[cyan]--- Starting search for:[/cyan] {query}")
        query_url = quote(query)
        url = f"https://www.google.com/search?q={query_url}&tbm=isch"
        driver.get(url)

        # --- Accept Cookies Once ---
        if first_run:
            consent_button_xpaths = [
                "//button[.//div[text()='Accept all']]",
                "//button[.//div[text()='Reject all']]",
                "//div[text()='I agree']"
            ]
            for xpath in consent_button_xpaths:
                try:
                    consent_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )
                    consent_button.click()
                    time.sleep(2)
                    break
                except TimeoutException:
                    continue
            first_run = False

        # --- Scroll to Load More Images ---
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        query_data = []

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'img.YQ4gaf'))
            )
            img_elements = driver.find_elements(By.CSS_SELECTOR, 'img.YQ4gaf')

            url_count = 0
            for img in img_elements:
                if url_count > 29:
                    break
                try:
                    img_url = img.get_attribute("src")
                    if img_url and img_url.startswith('http'):
                        query_data.append({'Query': query, 'Image URL': img_url})
                        url_count += 1
                except Exception:
                    continue
            console.print(f"[green]Added {url_count} image URLs for: {query}[/green]")

        except TimeoutException:
            console.print(f"[yellow]Timeout: No images found for {query}[/yellow]")

        # --- Append to CSV Immediately ---
        if query_data:
            df_query = pd.DataFrame(query_data)
            header_needed = not os.path.exists(result_path)
            df_query.to_csv(result_path, mode='a', header=header_needed, index=False)

        # --- Polite Pause ---
        pause_duration = random.uniform(4, 8)
        time.sleep(pause_duration)

        # --- Update Progress ---
        completed.add(query)
        with open(progress_path, 'w') as f:
            json.dump(list(completed), f)
        progress.advance(task)

# --- Close Browser ---
driver.quit()

elapsed = time.time() - start_time
console.print(f"\n[bold blue]Total Elapsed Time: {elapsed:.2f} seconds[/bold blue]")
console.print(f"[bold green]Results saved to {result_path}[/bold green]")
