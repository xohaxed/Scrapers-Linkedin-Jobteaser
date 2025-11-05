# Scrapers — LinkedIn & JobTeaser

Collect your job application history from LinkedIn and JobTeaser using Selenium and export the results to timestamped CSV files.

Both scripts open Microsoft Edge, guide you through login (with safe fallbacks for captcha/2FA), scroll to load your applications, scrape key fields, and save the results as `candidatures_<site>_YYYYMMDD_HHMMSS.csv` in the project folder.

> Note: The console output and some labels are in French because the target sites are often used in French. The README is in English for broader reach.

## Features

- Microsoft Edge (preinstalled on Windows) automation via Selenium
- Interactive login with manual fallback when a captcha or 2FA appears
- Robust selectors with alternatives and debug HTML dumps if nothing is found
- Clean CSV export with UTF-8 BOM for Excel compatibility
- Separate scrapers for LinkedIn and JobTeaser

## Project structure

```
jobteaser_scraper.py      # Scrape your JobTeaser applications
linkedin_scraper.py       # Scrape your LinkedIn applications
requirements.txt          # Python dependencies (Selenium, webdriver-manager)
```

## Prerequisites

- Windows with Microsoft Edge installed (the scripts are configured for Edge)
- Python 3.9+ (3.10/3.11 recommended)
- Edge WebDriver (msedgedriver.exe) matching your Edge version
  - Check your Edge version: navigate to `edge://settings/help`
  - Download WebDriver: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
  - Place `msedgedriver.exe` either:
    - in this project folder, or
    - anywhere on your `%PATH%`

The scripts will show a clear message if the driver is missing and suggest how to install it.

> webdriver-manager is listed in requirements but not used by default in the code. You can switch to it later if you prefer automatic driver management.

## Setup (Windows PowerShell)

```powershell
# From the project folder
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks script execution, you may need to run PowerShell as Administrator and relax the policy temporarily:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Usage

### LinkedIn

```powershell
python .\linkedin_scraper.py
```

- Enter your LinkedIn email and password when prompted.
- If a captcha or special check appears, complete it in the browser. The script allows a manual fallback and continues afterwards.
- On success, you’ll see a CSV like `candidatures_linkedin_20251105_153012.csv` in the folder.

### JobTeaser

```powershell
python .\jobteaser_scraper.py
```

- Enter your JobTeaser email and password when prompted.
- The script handles the cookie banner and navigates to “Mes candidatures / My applications”.
- On success, you’ll see a CSV like `candidatures_jobteaser_20251105_153112.csv` in the folder.

## Output format (CSV columns)

Both scrapers export the same columns:

- id
- titre (job title)
- entreprise (company)
- lieu (location)
- date_candidature (application date)
- statut (status — default "En attente")
- type_contrat (contract type when available)
- url (job posting URL)

## Troubleshooting

- Edge driver error at startup:
  - Ensure `msedgedriver.exe` matches your Edge version and is in the folder or on PATH. The scripts print a step-by-step fix if the driver isn’t found.
- Stuck on login / captcha / 2FA:
  - Complete it manually in the opened Edge window. The scripts include manual fallbacks (they’ll wait and continue).
- “Aucune candidature trouvée” (no applications found):
  - The script saves the page HTML to `linkedin_debug.html` or `jobteaser_debug.html`. Open that file to inspect the DOM and update selectors if the site layout changed.
- Selectors broke after a site update:
  - Update the CSS selectors in `extract_application_data(...)` and/or the list of alternative selectors (each script has them documented in the code).

## Adapting to a different browser

The code is set up for Microsoft Edge. If you prefer Chrome or Firefox:

- Replace `webdriver.EdgeOptions()` and `webdriver.Edge(...)` with the corresponding Chrome/Firefox variants.
- Install the matching driver (chromedriver/geckodriver) and ensure it’s on PATH.

## Legal and ethical notes

- Scrape only your own data and respect each site’s Terms of Service.
- Use reasonable scraping frequency. These scripts are interactive and human-paced by design.
- Don’t share your CSVs if they contain personal information.

## Contributing

Issues and pull requests are welcome. If you improve selectors or add headless/driver-manager support, feel free to open a PR.

## License

No explicit license provided yet. If you plan to open-source, consider adding an SPDX-approved license (e.g., MIT).
