import pandas as pd
from google.cloud import bigquery
from pathlib import Path
from datetime import datetime, timedelta
import hashlib

def fetch_with_cache(query: str) -> pd.DataFrame:
    """
    Fetch data from BigQuery with caching.
    
    Args:
        query (str): The SQL query to execute.
        
    Returns:
        pd.DataFrame: The result of the query as a DataFrame.
    """
    client = bigquery.Client('analytics-only')
    
    # Compute a simple hash of the query to use as a cache key.
    cache_key = hashlib.md5(query.encode()).hexdigest()
    cache_path = Path(f'cache/{cache_key}.parquet')

    # Invalidate the cache after 1h.
    if not cache_is_valid(cache_path):
        df = client.query(query).result().to_dataframe(create_bqstorage_client=False)
        df.to_parquet(cache_path)
    
    return pd.read_parquet(cache_path)

def cache_is_valid(cache_path: Path) -> bool:
    """
    Check if the cache file is valid (exists and not older than 1 hour).
    
    Args:
        cache_path (Path): The path to the cache file.
        
    Returns:
        bool: True if the cache is valid, False otherwise.
    """
    # If the cache file does not exist, it is not valid.
    if not cache_path.exists():
        return False
    
    # If the cache file is older than 1 hour, it is not valid.
    if datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime) > timedelta(hours=1):
        return False

    return True

# You can test this file by running it.
if __name__ == "__main__":
    sql_query = """
    SELECT 'Hello, world!' AS message
    """
    df = fetch_with_cache(sql_query)
    print(df.head(10))