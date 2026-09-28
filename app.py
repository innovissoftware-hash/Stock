import streamlit as st
import plotly.graph_objects as go
from analysis_engine import analyze

st.set_page_config(page_title="Stock Technical Agent", layout="wide")
st.title("📈 Stock Technical Analysis Agent")
st.caption("50/100/200 DMA + daily, weekly and monthly technical structure")

ticker = st.text_input("Enter stock ticker", value="RELIANCE.NS", help="For NSE use symbols such as RELIANCE.NS, TCS.NS, INFY.NS")
period = st.selectbox("History", ["2y", "5y", "10y"], index=1)

if st.button("Analyze", type="primary"):
    try:
        r = analyze(ticker)
        st.session_state["result"] = r
    except Exception as e:
        st.error(str(e))

if "result" in st.session_state:
    r = st.session_state["result"]
    d = r["data"]

    st.subheader(f"{r['ticker']} — Technical Report")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Price", f"₹{r['price']:,.2f}")
    c2.metric("50 DMA", f"₹{r['dma'][50]:,.2f}")
    c3.metric("100 DMA", f"₹{r['dma'][100]:,.2f}")
    c4.metric("200 DMA", f"₹{r['dma'][200]:,.2f}")

    st.info(f"Technical bias: **{r['bias']}** | DMA alignment: **{r['alignment']}** | Signal score: **{r['score']}/7**")

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=d.index, open=d["Open"], high=d["High"], low=d["Low"], close=d["Close"], name="Price"
    ))
    for n in (50,100,200):
        fig.add_trace(go.Scatter(x=d.index, y=d[f"SMA{n}"], mode="lines", name=f"{n} DMA"))
    fig.update_layout(height=650, xaxis_rangeslider_visible=False, title=f"{r['ticker']} — Price + 50/100/200 DMA")
    st.plotly_chart(fig, use_container_width=True)

    left,right = st.columns(2)
    with left:
        st.subheader("Weekly")
        st.write(f"Trend: **{r['weekly']['trend']}**")
        st.write(f"Candle: **{r['weekly']['pattern']}**")
    with right:
        st.subheader("Monthly")
        st.write(f"Trend: **{r['monthly']['trend']}**")
        st.write(f"Candle: **{r['monthly']['pattern']}**")

    st.subheader("Indicator snapshot")
    st.dataframe({
        "Metric": ["Price > 50 DMA","Price > 100 DMA","Price > 200 DMA","RSI(14)","MACD","MACD Signal","Volume / 20D Avg"],
        "Value": [
            r["above_dma"][50], r["above_dma"][100], r["above_dma"][200],
            round(r["rsi"],2), round(r["macd"],4), round(r["macd_signal"],4),
            round(r["volume_ratio"],2) if r["volume_ratio"] else None
        ]
    }, hide_index=True)

    st.caption(f"Data timestamp: {r['as_of']}. Technical indicators are calculated from historical market data.")
