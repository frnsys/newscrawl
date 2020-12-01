# newscrawl

1. Finds articles matching queries on MediaCloud
2. Downloads the complete articles
3. Extracts sentences matching specified keywords and named entities

# Setup

Install requirements: `pip install -r requirements.txt`

Create `config.py` with the following contents:

```python
import datetime

MEDIACLOUD_API_KEY = '<your mediacloud api key>'

# Search config
START_DATE = datetime.date(2020, 3, 1)
END_DATE = datetime.date.today()
QUERIES = [
    # "United States - State & Local" collection
    # https://sources.mediacloud.org/#/collections/38379429
    '(moratorium OR suspen*) AND ("covid-19" OR covid19 OR coronavirus) AND tags_id_media:38379429'
]

# Keywords to match sentences on
KEYWORDS = ['moratorium', 'suspension', 'suspend']
```

See <https://mediacloud.org/support/query-guide> for how to construct queries.

# Usage

```
python main.py
```

To generate a CSV from the data, run `python gencsv.py`.

# References

- <https://mediacloud.org/support/query-guide>
- <https://github.com/berkmancenter/mediacloud/blob/master/doc/api_2_0_spec/api_2_0_spec.md>
