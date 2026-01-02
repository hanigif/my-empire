import asyncio
from flask import Flask, render_template
import plotly.graph_objs as go
import yfinance as yf
import pandas as pd
import os

app = Flask(__name__)

def get_live_data():
    # قائمة الشركات الكبرى التي طلبها المدير
    tickers = ['NVDA', 'AAPL', 'MSFT', 'GOOGL', 'TSLA']
    data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        # جلب السعر الحالي
        price = stock.history(period='1d')['Close'].iloc[-1]
        data.append({'Company': ticker, 'Price': round(price, 2)})
    return pd.DataFrame(data)

@app.route('/')
def index():
    try:
        df = get_live_data()
        # إنشاء الرسم البياني التفاعلي
        fig = go.Figure(data=[go.Bar(
            x=df['Company'], 
            y=df['Price'], 
            marker_color='gold',
            text=df['Price'],
            textposition='auto'
        )])
        
        fig.update_layout(
            title='الأسعار الحية لأعمدة الإمبراطورية (USD)',
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white")
        )
        
        chart_html = fig.to_html(full_html=False)
        return render_template('index.html', chart=chart_html)
    except Exception as e:
        return f"جاري تحديث البيانات من البورصة... (خطأ: {e})"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
