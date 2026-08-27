# FX Transaction Cost Analysis (TCA) & Execution Quality Engine

An institutional-grade Transaction Cost Analysis (TCA) framework designed for Treasury and multi-asset execution desks. This application ingests high-frequency trade execution data, stores it securely in a relational database, and computes key execution performance metrics across liquidity providers.

![Main Dashboard KPIs](assets/main_kpi.png)

## Business Use Case

In fast-paced trading environments, treasury desks must constantly evaluate the quality of their execution to minimize slippage and manage counterparty risk. This automated engine replaces manual spreadsheet reconciliation by providing front-office operations with immediate, actionable intelligence. 

The engine specifically solves the following operational challenges:
*   **Implementation Shortfall Tracking:** Measures the exact cost of market impact and slippage in basis points (bps) against arrival price benchmarks.
*   **Liquidity Provider Benchmarking:** Evaluates counterparty fill efficiency, rejection rates, and execution latency to optimize future routing decisions.
*   **Automated Reporting:** Eliminates manual data mining by structuring raw trade logs into a queryable SQLite database linked to an interactive visualization layer.

## Key Features & Visualizations

The analytical dashboard, built with Streamlit and Plotly, allows users to filter execution data dynamically by currency pair and counterparty.



*   **Slippage Distribution:** A histogram mapping adverse price selection across different currency pairs, identifying outlier trades that require operational investigation.
*   **Fill Rate vs. Latency:** A multi-variable chart tracking the reliability of liquidity providers by comparing their successful execution rates against their average system latency.

![Counterparty Data Table](assets/data_table.png)

*   **Execution Quality Breakdown:** An automated data table calculating Volume-Weighted Average Price (VWAP) spreads, highlighting the most cost-effective counterparties for high-volume transactions.

## Tech Stack

*   **Data Engineering:** Python (Pandas, NumPy), SQLite, SQLAlchemy
*   **Analytics & Frontend:** Plotly, Streamlit
*   **Architecture:** Multi-threaded data ingestion, ACID-compliant local storage, responsive web framework.

## Data Methodology

Please note that the trade execution data utilized in this repository is entirely synthetic. To demonstrate the analytical capabilities of the TCA engine without exposing proprietary or licensed financial data, I engineered a Python script (`generate_data.py`) to simulate high-frequency institutional FX order flow. 

This simulation accurately models real-world execution variables, including adverse price selection, variable counterparty latency, and realistic fill/rejection ratios. The underlying SQL ingestion pipeline and analytical architecture are fully functional and can be instantly mapped to a live FIX protocol or REST API data feed for production use.

## 🚀 Quickstart & Testing Guide

### 1. Live Interactive Demo
To immediately evaluate the execution quality metrics, slippage calculations, and dashboard functionality without setting up a local environment, please access the live application here:
**[Launch FX TCA Engine Dashboard](https://fx-tca-engine-pe5cftybjhs6qre6rckxjz.streamlit.app/)**

### 2. Local Technical Review
If you wish to review the underlying Python data pipeline architecture and test the SQL ingestion engine locally, please follow these steps. 

**Step 1: Clone the repository**
`git clone https://github.com/YOUR_GITHUB_USERNAME/fx-tca-engine.git`
`cd fx-tca-engine`

**Step 2: Activate the environment and install dependencies**
`python3 -m venv venv`
`source venv/bin/activate`
`pip install -r requirements.txt`

**Step 3: Execute the automated data pipeline**
The following commands will generate 10,000 mock trade execution logs and populate the local SQLite schema to test the backend logic.
`python generate_data.py`
`python tca_engine.py`

**Step 4: Launch the analytics interface**
`streamlit run app.py`