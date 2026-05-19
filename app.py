import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(page_title="Institutional Stock Terminal", page_icon="⚡", layout="wide")

st.title("⚡ Elite Institutional Stock Analytics Terminal")
st.markdown("---")

# 2. Sidebar Controls
st.sidebar.header("🕹️ Terminal Controls")
ticker_symbol = st.sidebar.text_input("Enter Stock Ticker:", "AAPL").upper()
time_period = st.sidebar.selectbox("Select Time Horizon:", ("1mo", "6mo", "1y", "max"))

# 3. Data Fetching Engine
try:
    stock = yf.Ticker(ticker_symbol)
    df = stock.history(period=time_period)
    info = stock.info
    
    if not df.empty:
        company_name = info.get('longName', ticker_symbol)
        st.subheader(f"📊 {company_name} ({ticker_symbol}) Advanced Analysis")
        
        # --- NEW EXPERT EXTENSION: TECHNICAL INDICATORS DATA PROCESSING ---
        # Calculate 20-day Simple Moving Average (SMA)
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        
        # Calculate Relative Strength Index (RSI)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-10)  # avoid division by zero
        df['RSI'] = 100 - (100 / (1 + rs))
        # -----------------------------------------------------------------

        # 4. KPI Metrics Row
        latest_close = df['Close'].iloc[-1]
        previous_close = df['Close'].iloc[-2] if len(df) > 1 else latest_close
        price_delta = latest_close - previous_close
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current Price", f"${latest_close:.2f}", f"{price_delta:.2f}")
        with col2:
            st.metric("Period High", f"${df['High'].max():.2f}")
        with col3:
            st.metric("Period Low", f"${df['Low'].min():.2f}")
        with col4:
            st.metric("RSI (14d Momentum)", f"{df['RSI'].iloc[-1]:.1f}" if not pd.isna(df['RSI'].iloc[-1]) else "N/A")
            
        st.markdown("---")
        
        # 5. Advanced Candlestick Chart + Moving Average Overlay
        st.write("### 📈 Interactive Price Feed & Trend Tracking")
        
        fig = go.Figure()
        
        # Add core Candlestick Data
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Market Price'
        ))
        
        # Overlay the 20-day Moving Average Line
        fig.add_trace(go.Scatter(
            x=df.index, y=df['SMA_20'], mode='lines', name='20-Day Trend Line (SMA)', line=dict(color='#ff9900', width=1.5)
        ))
        
        fig.update_layout(
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            height=500,
            margin=dict(l=20, r=20, t=10, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # 6. --- NEW EXPERT EXTENSION: DATA EXPORT HUB ---
        st.write("### 📂 Corporate Data & Export Hub")
        
        # Clean up data frame for corporate export preview
        export_df = df.copy().sort_index(ascending=False)
        
        # Create an automated CSV download trigger
        csv_data = export_df.to_csv().encode('utf-8')
        
        col_btn, _ = st.columns([2, 8])
        with col_btn:
            st.download_button(
                label="📥 Export Report to CSV / Excel",
                data=csv_data,
                file_name=f"{ticker_symbol}_financial_report.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        st.dataframe(export_df, use_container_width=True)
            
    else:
        st.error(f"⚠️ No data found for ticker symbol: '{ticker_symbol}'.")
except Exception as e:
    st.error(f"❌ Connection Error: {e}")