# Moomoo Market Data & Options Research

A collection of Python experiments for collecting stock and options quotes through Moomoo OpenD, paired with MATLAB scripts for exploring intraday price behavior, technical indicators, and trading signals.

The repository contains a standalone quote monitor, earlier data collectors and option-selection prototypes, recorded market data from December 2024, and analysis notes. It is an experimental research workspace with individually configured scripts, rather than a packaged application.

## What it includes

- **Live quote monitoring:** poll an option's last price and best bid/ask at a configurable interval.
- **Market-data recording:** earlier scripts collect underlying and option quotes into CSV files, including scheduled, nominally one-second sampling.
- **Option selection:** explore nearest-expiry calls and puts selected by volume, premium, proximity to the underlying, delta, or ranked in-the-money strikes.
- **Indicator research:** compare moving averages, trailing median filters, RSI, Bollinger bands, crossover timing, and price-change statistics.
- **Trade simulations:** explore bid/ask-based entries and exits, parameter sweeps, and gain/loss thresholds in MATLAB.
- **Call/put analysis:** compare individual legs, combined premiums, intrinsic value, and illustrative exponential curves.

## Repository layout

```text
.
|-- New Test.py                 # Standalone live option quote monitor
|-- Old/                        # Earlier Python experiments and supporting code
|   |-- Option_Selector.py      # Six option-selection variants
|   |-- Second Tracking*.py     # Multi-symbol quote recording experiments
|   |-- Price per Second.py     # Paired call/put quote recording
|   |-- Intraday MA Tracking 2.py
|   |-- History Kline.py        # Historical candles and comparison plots
|   |-- Ticker.py               # Price history, averages, and signal state
|   |-- Moomoo Sample.py        # Moving-average trading sample
|   |-- Test Buy.py / Test Sell.py
|   `-- ...                    # Account, scheduling, CSV, and plotting tests
`-- Data Analysis/
    |-- Analysis_V3.m ... Analysis_V10.m
    |-- IWM_Analysis.m
    |-- QQQCP_Analysis.m
    |-- *.csv                  # Recorded quotes and derived data variants
    `-- Graphic Analysis.docx  # Charts and research notes
```

An additional chart notebook, `Graphic Anaylsis 2.docx`, is stored in `Old/`. Any `__pycache__/` files are generated Python bytecode, not source files.

## Run the quote monitor

### Requirements

- Python with the `moomoo` SDK and APScheduler's 3.x API.
- Moomoo OpenD running and logged in, with the required market-data access for the chosen instrument.
- Access to the OpenD host and port configured in the script; the supplied values are `127.0.0.1:11111`.

From the repository folder, create a virtual environment and install the monitor's dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install moomoo "APScheduler<4"
```

Edit the settings at the top of `New Test.py`:

| Setting | Purpose |
| --- | --- |
| `OPTION_CODE` | Moomoo instrument code to monitor; replace the supplied expired example with a valid contract. |
| `REFRESH_SEC` | Polling interval in seconds; initially `1`. |
| `HOST`, `PORT` | OpenD connection address. |

Then run:

```powershell
.\.venv\Scripts\python.exe "New Test.py"
```

The script subscribes to quote and order-book data, then prints a timestamp, instrument code, last price, bid, and ask. Press **Ctrl+C** to stop the scheduler and close the quote connection. This script prints to the terminal; it does not save CSV data or place orders.

If subscription fails, it reports the error and still attempts polling. Check the OpenD connection, contract code, and quote permissions. Failed requests can return `None`; an empty bid or ask book is not explicitly handled.

## Earlier Python experiments

Some earlier scripts also import `pandas`, `numpy`, and `matplotlib`:

```powershell
.\.venv\Scripts\python.exe -m pip install pandas numpy matplotlib
```

Review each script before running it. Symbols, dates, session windows, output names, and strategy parameters are embedded in the source. Dates are historical, and scheduling uses the computer's local time without explicit exchange-timezone conversion. CSV output generally uses the current working directory and append mode, so repeated runs may append data and duplicate headers.

`Second Tracking 3.py` selects nearest-expiry call/put contracts at the first, second, and fifth in-the-money strike positions for its configured underlyings, then records last/bid/ask quotes. Earlier versions use different selection logic. `Option_Selector.py` also runs example queries at module level, so importing it can connect to OpenD and execute those queries.

**Trading scripts require particular care:** `Old/Test Buy.py` and `Old/Test Sell.py` unlock trading and submit orders with `TrdEnv.REAL`. `Old/Second Tracking 2.py` includes a real-order helper, although its unlock-and-buy invocation is commented out. `Old/Moomoo Sample.py` defaults to simulation. Files named “Test” are standalone experiments, not an automated test suite.

Hardcoded trading passwords exist in the legacy source. Remove them before publishing, rotate any that are valid, and use private configuration or environment variables for future credentials. Removing a value from a file does not remove it from any existing Git history.

## MATLAB analysis

Set MATLAB's current folder to `Data Analysis`, then run the desired function. For example:

```matlab
cd('Data Analysis')
Analysis_V10
```

`Analysis_V10` reads the included `2024-12-26.csv` and plots IWM, option midprices, put premium above intrinsic value, and a combined call/put series alongside illustrative exponential curves.

| Files | Focus |
| --- | --- |
| `Analysis_V3.m`, `Analysis_V6.m` | Moving-average parameter sweeps and simulated earning-ratio surfaces. |
| `Analysis_V4.m` | Moving-average crossover-gap distributions. |
| `Analysis_V5.m` | Moving averages, Bollinger bands, and RSI. |
| `Analysis_V7.m`, `Analysis_V8.m` | Median filtering, modified averages, and experimental trade-simulation helpers. |
| `Analysis_V9.m` | First/second price differences, rolling statistics, and threshold crossings. |
| `Analysis_V10.m` | IWM call/put premiums and combined-price exploration. |
| `IWM_Analysis.m`, `QQQCP_Analysis.m` | Focused IWM and QQQ quote plots. |

File names, column references, and parameters are hardcoded. Match those references to the selected CSV before running an analysis. Some scripts use `movavg` and `ksdensity`, which require the relevant MATLAB toolboxes. Helper functions in a file are not necessarily called by that file's main function.

## Recorded data

The CSV collection contains December 2024 stock and option observations, including SPY, QQQ, IWM, and individual equities. Common layouts include:

- A `Time` column followed by `<symbol>Last`, `<symbol>Bid`, and `<symbol>Ask` triplets.
- Paired option columns such as `Last Price C`, `Bid C`, `Ask C`, `Last Price P`, `Bid P`, and `Ask P`.
- Moving-average/action logs and derived files with additional indicator columns.

Schemas and timestamp formats vary. Some `Copy` files omit time or underlying columns; some files are empty or partial. Inspect headers and timestamps before combining datasets. A one-second collection target does not guarantee evenly spaced observations, and sample-index windows should not automatically be treated as elapsed seconds.

## Project status and limitations

There is no dependency lockfile, automated test suite, central configuration, or unified command-line interface. The legacy code includes incomplete experiments and limited handling of missing data, failed requests, or empty option selections.

The simulations are exploratory calculations, not a validated execution or portfolio model. They do not comprehensively model commissions, slippage, liquidity, partial fills, contract multipliers, or capital requirements. Charts and simulated earning ratios do not establish live trading performance.

No license file is currently included. Review source attribution and market-data redistribution terms before distributing the code or datasets.
