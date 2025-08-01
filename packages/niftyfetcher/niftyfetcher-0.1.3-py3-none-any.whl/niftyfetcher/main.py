import typer
from datetime import datetime, timedelta
import pandas as pd
import requests
import json
import time


app = typer.Typer(help="📈 Fetch historical data for a given instrument between two dates.")


def validate_file_type(file_type: str) -> str:
    valid_types = {"csv", "xlsx", ".csv", ".xlsx"}
    if file_type.lower() not in valid_types:
        raise typer.BadParameter("file_type must be one of: csv, xlsx, .csv, .xlsx")
    return file_type.lower().lstrip(".")

@app.command()
def fetch_data(
    instrument_key: str = typer.Argument(..., help="Upstox instrument key for the stock"),
    unit: str = typer.Argument(..., help="Unit of the data to fetch. Can be 'minutes', 'hours', 'days', 'weeks', 'months'"),
    interval: int = typer.Argument(..., help="Interval of the data to fetch."),
    from_date: str = typer.Argument(..., help="Start date in YYYY-MM-DD format"),
    to_date: str = typer.Argument(..., help="End date in YYYY-MM-DD format"),
    file_type: str = typer.Argument(..., callback=validate_file_type, help="File type to save: csv or xlsx")
):
    """
    Fetch historical data between the specified date range.
    """
    # Use a list to collect DataFrames and avoid pandas concat warning
    dataframes_list = []
    
    # Parse the date strings, but keep the original string variables unchanged
    from_date_dt = datetime.strptime(from_date, "%Y-%m-%d")
    to_date_dt = datetime.strptime(to_date, "%Y-%m-%d")
    
    # Format dates as YYYY-MM-DD strings for API (these will be the same as input, but ensures correct format)
    from_date_str = from_date_dt.strftime("%Y-%m-%d") 
    to_date_str = to_date_dt.strftime("%Y-%m-%d")

    date_range = to_date_dt - from_date_dt

    typer.echo(f"📊 Fetching data for {instrument_key} from {from_date_str} to {to_date_str}")
    typer.echo(f"💾 File will be saved as a .{file_type} file")

    def fetch_and_append(start_dt, end_dt):
        start_str = start_dt.strftime("%Y-%m-%d")
        end_str = end_dt.strftime("%Y-%m-%d")
        try:
            url = f"https://api.upstox.com/v3/historical-candle/{instrument_key}/{unit}/{interval}/{end_str}/{start_str}"
            payload = {}
            headers = {
                'Accept': 'application/json'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code != 200:
                typer.echo(f"❌ API Error: HTTP {response.status_code}")
                typer.echo(f"Response: {response.text}")
                return None
        except Exception as e:
            typer.echo(f"❌ Error: {e}")
            return None

        try:
            response_data = json.loads(response.text)
            if response_data.get("status") == "error":
                typer.echo(f"❌ API Error: {response_data.get('errors', 'Unknown error')}")
                return None

            candles_data = response_data["data"]["candles"]
            try:
                df = pd.DataFrame(
                    [(c[0], c[1], c[2], c[3], c[4], c[5]) for c in candles_data],
                    columns=["timestamp", "open", "high", "low", "close", "volume"]
                )

            except:
                df = pd.DataFrame(
                    [(c[0], c[1], c[2], c[3], c[4], "NA") for c in candles_data],
                    columns=["timestamp", "open", "high", "low", "close", "volume"]
                )
            
            return df
            
        except KeyError as e:
            typer.echo(f"❌ Error parsing response data: {e}")
            typer.echo(f"Response: {response.text}")
            return None
        except Exception as e:
            typer.echo(f"❌ Error: {e}")
            return None

    if date_range.days > 2:
        # Fetch in 2-day intervals
        current_start = from_date_dt
        while current_start <= to_date_dt:
            current_end = min(current_start + timedelta(days=2), to_date_dt)
            df = fetch_and_append(current_start, current_end)
            time.sleep(1)
            if df is not None:
                dataframes_list.append(df)
            current_start = current_end + timedelta(days=1)
    else:
        # Fetch as is
        df = fetch_and_append(from_date_dt, to_date_dt)
        if df is not None:
            dataframes_list.append(df)

    # Combine all DataFrames at once to avoid pandas warning
    if dataframes_list:
        historical_data = pd.concat(dataframes_list, ignore_index=True)
    else:
        typer.echo("❌ No data retrieved")
        return

    # Clean filename by replacing problematic characters
    filename = f"{instrument_key}_{unit}_{interval}_{from_date_str}_{to_date_str}.{file_type}".replace("|", "_").replace(" ", "_")
    
    if file_type == "csv":
        historical_data.to_csv(filename, index=False)
    elif file_type == "xlsx":
        historical_data.to_excel(filename, index=False)
    else:
        typer.echo(f"❌ Error: Invalid file type: {file_type}")
        return
        
    typer.echo(f"✅ Data successfully saved to {filename}")
    typer.echo(f"📈 Fetched {len(historical_data)} records")



def main():
    app()

if __name__ == "__main__":
    main()
