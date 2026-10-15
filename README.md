# Supermart Grocery Sales Dashboard

An interactive data analytics dashboard built with **Python, Pandas, Streamlit and Plotly**, using the supplied Supermart Grocery Sales retail analytics dataset.

## Features

- KPI cards for total sales, total profit, unique orders, average sales per order and profit margin
- Monthly sales and profit trends
- Category and sub-category sales/profit analysis
- High-sales category/sub-category combinations with profit context
- Discount vs. profit scatter plot and profit by discount band
- State-wise sales and profit
- City-level sales, profit, order count and profit margin
- Filters for date range, category, region and state
- Filtered data table and CSV export

## Dataset

The supplied CSV is stored at:

`data/Supermart Grocery Sales - Retail Analytics Dataset.csv`

The source dataset has 9,994 rows and 11 columns. The original project requirements are included in `Sapphire IQ Supermart Grocery Sales Dashboard.pdf`.

## Run locally

Python 3.10 or newer is recommended.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit, typically `http://localhost:8501`.

If `python` is not recognized, install Python from https://www.python.org/downloads/ and enable **Add Python to PATH**, then reopen PowerShell.

## Upload to GitHub

1. Create a repository, e.g. `supermart-grocery-sales-dashboard`.
2. Upload `app.py`, `README.md`, `requirements.txt`, `.gitignore`, the PDF and the `data` folder.
3. Commit the changes.
4. Keep the CSV in the `data` folder with its exact filename.

## Deploy online (optional)

Push the project to GitHub, then connect the repository through Streamlit Community Cloud. Set the main file path to `app.py` and deploy.

## Metric definitions

- Total Sales: sum of `Sales` within the selected filters.
- Total Profit: sum of `Profit` within the selected filters.
- Unique Orders: count of distinct `Order ID`.
- Average Sales / Order: total sales divided by distinct orders.
- Profit Margin: total profit divided by total sales, multiplied by 100.

Discount-profit charts show observed associations in this dataset; they do not prove that discounts caused a profit change.

## Project structure

```text
supermart-grocery-sales-dashboard/
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
├── Sapphire IQ Supermart Grocery Sales Dashboard.pdf
└── data/
    └── Supermart Grocery Sales - Retail Analytics Dataset.csv
```

## Disclaimer

Educational portfolio project using the user-provided dataset. It is not affiliated with a grocery retailer.
