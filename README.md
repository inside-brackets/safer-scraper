# Safer Scraper

## Overview
This project is a web scraper built using **Selenium** to extract detailed information about trucks. The scraper focuses on gathering **callable leads**, ensuring that only leads meeting specific criteria are saved. This includes checking the carrier's operating status, geographical location, and other parameters.

## Features
- Scrapes detailed truck and carrier information.
- Filters and saves only **callable leads** based on pre-defined rules (e.g., operating status and state).
- Extracts relevant fields such as **MC number**, **company name**, **phone number**, **email**, and more.
- Saves results in a CSV format for further processing.

## Key Functionalities

### 1. Callable Lead Filtering
- **Operating Status**: Scrapes only leads that are "Authorized for Property".
- **State Filtering**: Ensures that the lead’s physical address matches a valid U.S. state from a predefined list.
- **Carrier Type**: Scrapes only leads where the carrier is of type **CARRIER**.

### 2. Data Extraction
- Extracts key fields such as:
  - **MC Number**
  - **Company Name**
  - **Phone Number**
  - **Physical Address**
  - **USDOT Number**
  - **Cargo Carried**
  - **Power Units**
  - **Email**

### 3. Data Transformation and Saving
- Transforms the extracted data into a structured format.
- Saves callable leads in a **CSV file** for later use.

## Installation

### Prerequisites
- Python 3.x
- Google Chrome (or another browser)
- Selenium WebDriver for your browser version
- Required Python packages (listed in `requirements.txt`)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/truck-scraper.git
   ```
2. Navigate to the project directory:
   ```bash
   cd truck-scraper
   ```
3. Install the required dependencies using `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

4. Download and set up the correct **WebDriver** for your browser (e.g., ChromeDriver).

## Usage

1. Update the **states_list** and **operation_class_check** variables if needed, to refine the filtering criteria.

2. Run the scraper:
   ```bash
   python scraper.py
   ```

3. The scraped data will be saved in the `./files/carriers.csv` file in CSV format.

### CSV Format
The saved CSV file will have the following columns:
- `mc_number`
- `company_name`
- `dba_name`
- `address`
- `phone_number`
- `usdot_number`
- `power_units`
- `email`
- `c_status`
- `cargo_carried`

## Code Snippet Example
```python
def save_entity(page, mc):
    is_callable, entity = check_callable(page)
    if entity == -1:
        return -1  # scraping error
    if is_callable:
        entity['mc_number'] = str(mc)
        with open(r'./files/carriers.csv', 'a', newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writerow(entity)
        return 0  # success
    else:
        return -2  # not callable
```
