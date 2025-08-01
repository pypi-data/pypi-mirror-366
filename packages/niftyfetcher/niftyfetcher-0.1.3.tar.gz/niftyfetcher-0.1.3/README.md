# 📈 NiftyFetcher

A powerful CLI tool to fetch historical OHLC (Open, High, Low, Close) data for stocks using the Upstox API.

## 🚀 Features

- Fetch historical stock data with customizable time intervals
- Support for multiple time units (minute, hour, day, week, month)
- Export data to CSV or Excel formats
- Automatic handling of large date ranges with intelligent chunking
- Clean, user-friendly command-line interface
- Error handling with detailed feedback

## 📦 Installation

Install from PyPI:

```bash
pip install niftyfetcher
```

Or install from source:

```bash
git clone https://github.com/yash2002vardhan/niftyfetcher.git
cd niftyfetcher
pip install -e .
```

## 🛠️ Usage

### Basic Syntax

```bash
niftyfetcher INSTRUMENT_KEY UNIT INTERVAL FROM_DATE TO_DATE FILE_TYPE
```

### Arguments

| Argument | Description | Example Values |
|----------|-------------|----------------|
| `INSTRUMENT_KEY` | Upstox instrument key for the stock | `NSE_EQ\|INE002A01018` |
| `UNIT` | Time unit for data | `minutes`, `hours`, `days`, `weeks`, `months` |
| `INTERVAL` | Interval within the unit | `1`, `5`, `15`, `30` |
| `FROM_DATE` | Start date (YYYY-MM-DD) | `2024-01-01` |
| `TO_DATE` | End date (YYYY-MM-DD) | `2024-01-31` |
| `FILE_TYPE` | Output format | `csv` or `xlsx` |

### 📋 Examples

**Fetch daily data for Nifty 50:**
```bash
niftyfetcher "NSE_INDEX|Nifty 50" days 1 2024-01-01 2024-01-31 csv
```

**Fetch 5-minute interval data:**
```bash
niftyfetcher "NSE_EQ|INE002A01018" minutes 5 2024-01-15 2024-01-16 xlsx
```

**Fetch weekly data for a year:**
```bash
niftyfetcher "NSE_EQ|INE002A01018" weeks 1 2023-01-01 2023-12-31 csv
```

### 📊 Output

The tool generates files with the following naming convention:
```
{instrument_key}_{unit}_{interval}_{from_date}_{to_date}.{file_type}
```

Output contains columns:
- `timestamp` - Date/time of the data point
- `open` - Opening price
- `high` - Highest price
- `low` - Lowest price
- `close` - Closing price

## 🔧 Getting Help

```bash
niftyfetcher --help
```

## 📝 Requirements

- Python 3.8+
- Internet connection for API access

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes. Always verify data accuracy for trading decisions. The authors are not responsible for any financial losses.

## 🐛 Issues

If you encounter any issues, please report them on [GitHub Issues](https://github.com/yash2002vardhan/niftyfetcher/issues).

## ⚠️ Note on Rate Limits

Please be mindful of the rate limits imposed by the Upstox API to avoid errors or temporary bans. While this tool includes basic safeguards (such as delays between requests), it is ultimately your responsibility to ensure you do not exceed Upstox's allowed request limits. The authors are not liable for any issues arising from rate limit violations.
