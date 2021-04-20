"""
List of the major crypto synthetic rates from FTX
"""
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz

min_annual_rate = 20 # Minimum annual rate targeted
futuresapi = requests.get('https://ftx.com/api/futures')
data = json.loads(futuresapi.text)
df = pd.json_normalize(data["result"])
df = df.drop(columns=['enabled','postOnly','priceIncrement','sizeIncrement',
                      'change1h','change24h','changeBod','volume',
                      'volumeUsd24h','moveStart','positionLimitWeight','bid',
                      'ask','underlyingDescription','imfFactor','lowerBound',
                      'upperBound','type','expired','marginPrice','last',
                      'group','expiryDescription','description','underlying'])

df = df[df.perpetual != True]
df['today'] = datetime.now(tz=pytz.UTC)
df['days'] = (pd.to_datetime(df['expiry']) - df['today']).dt.days

df = df.drop(columns=['expiry','perpetual','today'])

df['index'] = pd.to_numeric(df['index'])
df['mark'] = pd.to_numeric(df['mark'])
df['dir_rate'] = round(((df['mark'] / df['index']) - 1) * 100,2)
df['annual_rate'] = round((df['dir_rate'] / df['days']) *365, 2)
df = df[df['annual_rate'] > min_annual_rate]
df.sort_values(by='annual_rate', ascending=False)