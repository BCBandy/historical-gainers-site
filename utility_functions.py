from sqlalchemy import create_engine, Column, Integer, Float, Date, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, column_property, declarative_base
import json
import pyodbc
import pandas as pd

Base = declarative_base()

DATABASE_URI = f"mssql+pyodbc://@DESKTOP-BKHK1H3/Stonks?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes&autocommit=true"
# Set up the database engine and session
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

class Daily(Base):
    __tablename__ = 'daily'
    symbol = Column(String(8), primary_key=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    date = Column(String(10), primary_key=True)
    percent_gain = column_property(((high - open) / open) * 100)

def top_gainers_sqlalchemy():
    # Query the top 10 gainers (customize this as needed)
    gainers = session.query(
        Daily.date,
        Daily.symbol,
        Daily.volume,
        Daily.percent_gain  # Calculated percent_gain
    ).filter(
        Daily.percent_gain > 20,  
        Daily.volume > 20 * 1000000,
        Daily.open > 0,
        (Daily.high + Daily.low) / 2 * Daily.volume > 5 * 1000000
    ).order_by(Daily.date.desc()).limit(500).all()

    # Convert data to JSON format for the front end
    data = [{"Date": stock.date, "symbol": stock.symbol, "percent_gain": stock.percent_gain} for stock in gainers]
    with open("static\\top_gainers.json", "w") as f:
        json.dump(data, f, indent=4)

def get_connection():
        cnxn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};"
                        "Server=DESKTOP-BKHK1H3;"
                        "Database=Stonks;"
                        "Trusted_Connection=yes;")
        return cnxn

def get_results_df(sql, values=None):
        cnxn = get_connection()
        if values is not None:
            data = pd.read_sql(sql, params=values,con=cnxn) 
        else:
             data = pd.read_sql(sql,con=cnxn) 
        return data

def update_top_gainers():
    sql = '''
-- get historical from daily through march then use scanner data
SELECT daily.symbol as symbol
	, daily.[date] as [Date]
	, round((daily.[high] - daily2.[close])/daily2.[close]*100, 2) as percent_gain
	, daily.volume/1000000 as Volume
	--, daily.[open] as [Open]
	, daily.[high] as [High]
	--, daily.[low] as [Low]
	--, daily.[close] as [Close]
FROM dbo.daily_temp AS daily
join dbo.daily_temp as daily2
	on daily2.symbol = daily.symbol
	and daily2.symbol_count = daily.symbol_count-1
WHERE  daily.[open] > 0 
	--and daily.volume > 20*1000000
	and daily.[high] >= .50													-- open price
	and ((daily.[high] + daily.[low]) / 2) * daily.volume >= 20 *1000000	-- dollar volume
	and (daily.[high] - daily2.[close])/daily2.[close] >= .4				-- pct gain to hod from open
	and daily.date < '2025-03-01'

union

select symbol
	, date
	, pctChange
	, volume/1000000
	, price as high

from ServiceGainers
where date >= '2025-03-01'
and price >= .5
and price * volume > 20 * 1000000
and pctChange >= 40
order by 2 desc, 3 desc
'''
    results_df = get_results_df(sql)
    results_json = results_df.to_json(orient="records", lines=False)
    results_json_clean = json.loads(results_json)
    with open("static\\top_gainers.json", "w") as f:
        json.dump(results_json_clean, f, indent=4)
    with open("docs\\static\\top_gainers.json", "w") as f:
        json.dump(results_json_clean, f, indent=4)

if __name__ == '__main__':
    # needed for daily gainers udpate, should be moved to another file and update the task scheduler/bat
    update_top_gainers()
