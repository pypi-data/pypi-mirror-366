This is a simple helper intended to be used at Fivetran to cache queries to BigQuery. It's used as follows:

```python
from ftbqcache import fetch_with_cache

df = fetch_with_cache("select 1")
```

Queries are run in `analytics-only`. You need to have your own credentials, obviously. Results are cached for 1h as parquet files in `./cache`.