import sqlite3
import os
from typing import List, Optional
from datetime import datetime

# Path to the SQLite database inside the package
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'earnings.db')

def get_connection():
    """Returns a connection to the earnings database."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError("Database not found. Ensure 'earnings.db' exists in the 'data' folder.")
    return sqlite3.connect(DB_PATH)

def get_earnings(ticker: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[str]:
    """
    Retrieves the earnings dates for a given stock ticker.

    Args:
        ticker (str): Stock ticker (e.g., "AAPL", "MSFT").
        start_date (str, optional): Filter results starting from this date ("YYYY-MM-DD").
        end_date (str, optional): Filter results ending at this date ("YYYY-MM-DD").

    Returns:
        List[str]: A list of earnings dates in "YYYY-MM-DD" format.
    """
    if not ticker or not isinstance(ticker, str):
        raise ValueError("Ticker must be a non-empty string.")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT Earnings_Date FROM earnings WHERE Ticker = ?"
        params = [ticker.upper()]

        if start_date:
            query += " AND Earnings_Date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND Earnings_Date <= ?"
            params.append(end_date)

        query += " ORDER BY Earnings_Date DESC"
        cursor.execute(query, tuple(params))

        results = cursor.fetchall()
        return [row[0] for row in results]

    except sqlite3.Error as e:
        raise RuntimeError(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def list_all_tickers() -> List[str]:
    """
    Returns a sorted list of all tickers available in the database.

    Returns:
        List[str]: A list of unique ticker symbols.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT Ticker FROM earnings ORDER BY Ticker ASC")
        results = cursor.fetchall()
        return [row[0] for row in results]

    except sqlite3.Error as e:
        raise RuntimeError(f"Database error: {e}")
    finally:
        if conn:
            conn.close()
