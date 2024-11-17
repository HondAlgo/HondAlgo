import streamlit as st
import pandas as pd
import yfinance as yf
import time


# ================== FUNCTIONS ==================

def fetch_stock_data(symbol, period="1y"):
    """Fetch historical daily data for a stock symbol."""
    try:
        return yf.download(symbol, period=period, interval="1d")
    except Exception as e:
        return None


def calculate_indicators(df, ema_fast, ema_mid, ema_slow, wr_length):
    """Calculate EMAs, Williams %R, Relative Volume, and Buy Signal."""
    # Ensure the DataFrame has valid data
    if df is None or df.empty or 'Close' not in df.columns:
        raise ValueError("DataFrame is empty or does not contain required columns.")

    # Calculate EMAs
    df['EMA_Fast'] = df['Close'].ewm(span=ema_fast, adjust=False).mean()
    df['EMA_Mid'] = df['Close'].ewm(span=ema_mid, adjust=False).mean()
    df['EMA_Slow'] = df['Close'].ewm(span=ema_slow, adjust=False).mean()

    # Calculate Williams %R
    high_roll = df['High'].rolling(window=wr_length)
    low_roll = df['Low'].rolling(window=wr_length)
    df['%R'] = (high_roll.max() - df['Close']) / (high_roll.max() - low_roll.min()) * -100

    # Volume-based calculations (only if Volume column exists)
    if 'Volume' in df.columns and not df['Volume'].isnull().all():
        df['Volume_SMA'] = df['Volume'].rolling(window=30).mean()
        df['Rel_Volume'] = df['Volume'] / df['Volume_SMA']
        df['Rel_Volume'] = df['Rel_Volume'].fillna(0)  # Fill NaN values with 0
    else:
        df['Rel_Volume'] = 0  # Default to 0 if Volume data is missing

    # Buy Signal Conditions
    df['EMA_Aligned'] = (df['EMA_Fast'] > df['EMA_Mid']) & (df['EMA_Mid'] > df['EMA_Slow'])
    df['WR_Cross'] = (df['%R'].shift(1) <= -80) & (df['%R'] > -80)
    df['Close_Above_EMA50'] = df['Close'] > df['EMA_Mid']
    
    # Final Buy Signal
    df['Buy_Signal'] = (
        df['EMA_Aligned'] & 
        df['WR_Cross'] & 
        df['Close_Above_EMA50'] & 
        (df['Rel_Volume'] > 1)  # Ensure relative volume is above average
    )
    
    return df


# ================== STREAMLIT UI ==================

st.markdown(
    """
    <div style="text-align: center;">
        <h1>HondAlgo</h1>
        <p>Algorithm analyzes stock data and detects stocks with high bullish potential.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar for parameter inputs
st.sidebar.header("Set Parameters")
ema_fast = st.sidebar.number_input("Fast EMA Length", value=20, min_value=1)
ema_mid = st.sidebar.number_input("Mid EMA Length", value=50, min_value=1)
ema_slow = st.sidebar.number_input("Slow EMA Length", value=100, min_value=1)
wr_length = st.sidebar.number_input("Williams %R Length", value=14, min_value=1)

period = "1y"  # Fixed 1-year period for consistency

st.markdown(
    """
    <div style="text-align: center;">
        <h3>Stock Symbols</h3>
        <p>Enter stock symbols (comma-separated)</p>
    </div>
    """,
    unsafe_allow_html=True
)
symbols = st.text_area("", "AAPL, MSFT, TSLA")

# ================== ANALYSIS PROCESS ==================

if st.button("Analyze"):
    stock_symbols = [s.strip() for s in symbols.split(",") if s.strip()]
    
    if not stock_symbols:
        st.error("Please provide at least one stock symbol.")
    else:
        analyzing_placeholder = st.markdown(
            f"<div style='text-align: center; font-size: 18px;'>Analyzing {len(stock_symbols)} stocks 📈💹...</div>",
            unsafe_allow_html=True
        )

        qualifying_stocks = []
        error_stocks = []
        progress = st.progress(0)
        status_placeholder = st.empty()
        step = 100 / len(stock_symbols)
        stock_icons = ["📈", "📉", "💹", "📊", "💵"]

        for i, symbol in enumerate(stock_symbols):
            current_icon = stock_icons[i % len(stock_icons)]
            status_placeholder.markdown(
                f"<div style='text-align: center; font-size: 18px;'>Analyzing {i+1}/{len(stock_symbols)}: {symbol} {current_icon}</div>",
                unsafe_allow_html=True
            )
            progress.progress(int((i + 1) * step))
            
            try:
                df = fetch_stock_data(symbol, period=period)
                if df is None or df.empty:
                    raise ValueError(f"No data available for {symbol}.")
                
                df = calculate_indicators(df, ema_fast, ema_mid, ema_slow, wr_length)
                if df['Buy_Signal'].iloc[-1]:
                    qualifying_stocks.append(symbol)
            except Exception as e:
                error_stocks.append(symbol)
                st.warning(f"Error analyzing {symbol}: {str(e)}")

            time.sleep(0.5)
        
        status_placeholder.empty()
        analyzing_placeholder.empty()

        st.markdown(
            f"<div style='text-align: center; font-size: 18px; color: green;'>{len(stock_symbols)} stocks have been analyzed successfully ✅</div>",
            unsafe_allow_html=True
        )

        st.markdown("### Results")
        
        if qualifying_stocks:
            st.subheader("Qualified Stocks")
            df_qualifying = pd.DataFrame(qualifying_stocks, columns=["Stock"])
            df_qualifying.index += 1
            st.dataframe(df_qualifying)
        else:
            st.write("No qualified stocks found.")

        if error_stocks:
            st.subheader("Lost Stocks")
            df_errors = pd.DataFrame(error_stocks, columns=["Stock"])
            df_errors.index += 1
            st.dataframe(df_errors)
        else:
            st.write("No errors detected.")

        with pd.ExcelWriter("results.xlsx", engine="openpyxl") as writer:
            if qualifying_stocks:
                df_qualifying.to_excel(writer, index=False, sheet_name="Buy Signals")
            if error_stocks:
                pd.DataFrame(error_stocks, columns=["Lost Stocks"]).to_excel(writer, index=False, sheet_name="Errors")
            if not qualifying_stocks and not error_stocks:
                pd.DataFrame(["No available data"]).to_excel(writer, index=False, header=False, sheet_name="No Data")

        with open("results.xlsx", "rb") as file:
            st.download_button(
                label="Download Results as Xlsx",
                data=file,
                file_name="HondAlgo_Results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# ================== FOOTER ==================

st.markdown(
    """
    <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            padding: 10px 0;
            background-color: #333333;
            color: white;
            font-size: 14px;
        }
        .footer-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 20px;
        }
        .footer-center {
            flex: 1;
            text-align: center;
        }
        .footer-center a {
            color: white;
            text-decoration: none;
        }
        .footer-center a:hover {
            color: blue; /* Change text color to blue on hover */
            text-decoration: underline;
        }
    </style>
    <div class="footer">
        <div class="footer-content">
            <div class="footer-center">
                © 2024 HondAlgo. Designed by: 
                <a href="https://www.facebook.com/share/1YtvJ13iDG/" target="_blank">Mohaned Abdallah</a>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
