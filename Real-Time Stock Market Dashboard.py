# stock_dashboard.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf
from datetime import datetime, timedelta
import requests

st.set_page_config(page_title="Real-Time Stock Dashboard", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stock-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📈 Real-Time Stock Market Dashboard</div>', unsafe_allow_html=True)

# Sidebar for stock selection
st.sidebar.title("Stock Selection")
stock_symbols = st.sidebar.text_input(
    "Enter stock symbols (comma-separated)", 
    "AAPL, GOOGL, MSFT, TSLA, AMZN"
).upper().split(',')

stock_symbols = [symbol.strip() for symbol in stock_symbols]

# Date range selection
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("Start Date", datetime.now() - timedelta(days=365))
with col2:
    end_date = st.date_input("End Date", datetime.now())

# Time period for data
period = st.sidebar.selectbox("Data Period", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y"])

def get_stock_data(symbol, period="1y"):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        
        # Get current info
        info = stock.info
        current_price = info.get('currentPrice', hist['Close'][-1] if len(hist) > 0 else 0)
        previous_close = info.get('previousClose', hist['Close'][-2] if len(hist) > 1 else current_price)
        
        change = current_price - previous_close
        change_percent = (change / previous_close) * 100
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'change': change,
            'change_percent': change_percent,
            'history': hist,
            'info': info
        }
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return None

# Main dashboard
if st.sidebar.button("Fetch Stock Data"):
    st.sidebar.info("Fetching latest stock data...")
    
    # Progress bar
    progress_bar = st.progress(0)
    
    # Stock cards
    cols = st.columns(len(stock_symbols))
    stock_data = {}
    
    for i, symbol in enumerate(stock_symbols):
        data = get_stock_data(symbol, period)
        if data:
            stock_data[symbol] = data
            
            with cols[i]:
                st.markdown(f"""
                <div class="stock-card">
                    <h3>{symbol}</h3>
                    <h2>${data['current_price']:.2f}</h2>
                    <p style="color: {'green' if data['change'] >= 0 else 'red'}">
                        {data['change']:+.2f} ({data['change_percent']:+.2f}%)
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        progress_bar.progress((i + 1) / len(stock_symbols))
    
    # Price charts
    if stock_data:
        st.subheader("Stock Price Trends")
        
        # Create interactive price chart
        fig = go.Figure()
        
        for symbol, data in stock_data.items():
            if not data['history'].empty:
                fig.add_trace(go.Scatter(
                    x=data['history'].index,
                    y=data['history']['Close'],
                    name=symbol,
                    mode='lines'
                ))
        
        fig.update_layout(
            title="Stock Price Comparison",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Volume chart
        st.subheader("Trading Volume")
        fig_volume = go.Figure()
        
        for symbol, data in stock_data.items():
            if not data['history'].empty:
                fig_volume.add_trace(go.Bar(
                    x=data['history'].index,
                    y=data['history']['Volume'],
                    name=symbol,
                    opacity=0.7
                ))
        
        fig_volume.update_layout(
            title="Trading Volume",
            xaxis_title="Date",
            yaxis_title="Volume",
            height=400,
            barmode='group'
        )
        
        st.plotly_chart(fig_volume, use_container_width=True)
        
        # Stock metrics table
        st.subheader("Stock Metrics")
        metrics_data = []
        
        for symbol, data in stock_data.items():
            info = data['info']
            metrics_data.append({
                'Symbol': symbol,
                'Current Price': f"${data['current_price']:.2f}",
                'Change': f"{data['change']:+.2f}",
                'Change %': f"{data['change_percent']:+.2f}%",
                'Market Cap': f"${info.get('marketCap', 'N/A'):,}" if info.get('marketCap') else 'N/A',
                'P/E Ratio': f"{info.get('trailingPE', 'N/A'):.2f}" if info.get('trailingPE') else 'N/A',
                '52 Week High': f"${info.get('fiftyTwoWeekHigh', 'N/A'):.2f}" if info.get('fiftyTwoWeekHigh') else 'N/A',
                '52 Week Low': f"${info.get('fiftyTwoWeekLow', 'N/A'):.2f}" if info.get('fiftyTwoWeekLow') else 'N/A'
            })
        
        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df, use_container_width=True)
        
        # Daily returns heatmap
        st.subheader("Daily Returns Correlation")
        returns_data = {}
        
        for symbol, data in stock_data.items():
            if not data['history'].empty:
                returns = data['history']['Close'].pct_change().dropna()
                returns_data[symbol] = returns
        
        if returns_data:
            returns_df = pd.DataFrame(returns_data)
            correlation_matrix = returns_df.corr()
            
            fig_corr = px.imshow(
                correlation_matrix,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="RdBu",
                title="Stock Returns Correlation Matrix"
            )
            st.plotly_chart(fig_corr, use_container_width=True)

else:
    st.info("👈 Enter stock symbols in the sidebar and click 'Fetch Stock Data' to begin!")

# Footer
st.markdown("---")
st.markdown("**Real-Time Stock Market Dashboard** | Data provided by Yahoo Finance")
