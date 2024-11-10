from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc://@DESKTOP-BKHK1H3/Stonks?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes&autocommit=true"
db = SQLAlchemy(app)

class Daily(db.Model):
    __tablename__ = 'daily'
    symbol = db.Column(db.String(8), primary_key=True)
    open = db.Column(db.Float)
    high = db.Column(db.Float)
    low = db.Column(db.Float)
    close = db.Column(db.Float)
    volume = db.Column(db.Integer)
    date = db.Column(db.String(10), primary_key=True)

    @hybrid_property
    def percent_gain(self):
        return ((self.high - self.open) / self.open) * 100 if self.open else None

@app.route('/api/top-gainers')
def top_gainers():
    # Query the top 10 gainers (customize this as needed)
    gainers = Daily.query.filter(
        Daily.percent_gain > 20,
        Daily.volume > 20*1000000,
        Daily.open > 0,
        (Daily.high+Daily.low)/2 * Daily.volume > 5*1000000
        ).order_by(Daily.date.desc()).limit(100).all()
    # Convert data to JSON format for the front end
    data = [{"Date": stock.date, "symbol": stock.symbol, "percent_gain": stock.percent_gain} for stock in gainers]
    
    return jsonify(data)



@app.route('/')
def index():
    '''
    http://127.0.0.1:5000/
    '''
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
