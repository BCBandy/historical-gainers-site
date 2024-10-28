from sqlalchemy import create_engine, Column, Integer, Float, Date, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, column_property, declarative_base
import json

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

def top_gainers():
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
    ).order_by(Daily.date.desc()).limit(100).all()

    # Convert data to JSON format for the front end
    data = [{"Date": stock.date, "symbol": stock.symbol, "percent_gain": stock.percent_gain} for stock in gainers]
    with open("static\\top_gainers.json", "w") as f:
        json.dump(data, f, indent=4)

if __name__ == '__main__':
    top_gainers()
