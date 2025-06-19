# Google Image URL Scraper

## Description
This Python script allows you to loop through a list of search queries to obtain image URLs for each search. Once URLs are acquired, they're saved alongside the search term in a ***query_results.csv*** file. This file can then be accessed via the provided ***image_reviewer.html*** file to review all image URLs obtained.

**Purpose:** The primary goal of this project is to quickly gather image URLs from a large list of terms for use in a local database. Intended output is one link per query item.

## Usage

Clone this repository to your local machine:
```bash
git clone https://github.com/BgWv3/Google-Image-Scraper.git
```
Navigate to the project folder:
``` bash
cd Google-Image-Scraper
```
Install the required Python packages:
``` bash
pip install -r requirements.txt
```
Add a `query.csv` file to the root directory. Use the `sample_query.csv` file for reference.

Run the script:
``` python
python image_scraper.py
```

### Results
Images matching the query will be stored in a new CSV file along side the searched query.

**Output File:** *query_results.csv* in the project's root directory

## Using the Image Reviewer Webpage

1. Open the *image_reviewer.html* file in your browser or run it on a local server.
2. Load in the *query_results.csv* file.
3. Scroll through the list of images gathered and make a selection for the ones you would like to keep. (Selections will highlight and can be altered)
4. Once all selections have been made, scroll back to the top and export the selections.

### Results
A *query_reviewed.csv* file will be downloaded consisting of a consolidated list of query items and URLs. One entry for each item reflecting the selected image during review.

**Output File:** *query_reviewed.csv* in your downloads directory

---
```
Dependencies:
- Python 3.x
- Selenium
- Microsoft WebDriver (Ensure it's compatible with your Edge browser version by using the Microsoft website [here](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/?form=MA13LH))```
