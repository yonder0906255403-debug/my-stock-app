import streamlit as st
import yfinance as yf
import feedparser
import urllib.parse

# 網頁標題與小圖示設定
st.set_page_config(page_title="股票新聞整合器", page_icon="📈", layout="centered")
st.title("📈 股票近期新聞智慧整合器")
st.write("手動輸入股票代號，一鍵抓取並整合最新市場新聞。")

# 讓使用者輸入代號的文字方塊
ticker_input = st.text_input("請輸入股票代號（美股如 AAPL，台股請加 .TW 如 2317.TW）", "2317.TW")

if st.button("開始整合新聞"):
    ticker = ticker_input.strip().upper()
    
    with st.spinner('正在搜尋最新新聞，請稍候...'):
        try:
            # 1. 依然使用 yfinance 抓取即時股價與公司名稱
            stock = yf.Ticker(ticker)
            info = stock.info
            company_name = info.get('longName', '未知公司')
            current_price = info.get('currentPrice', info.get('regularMarketPrice', '無資料'))
            currency = info.get('currency', 'USD')
            
            st.success(f"✅ 成功連結：{company_name} ({ticker})")
            if current_price != '無資料':
                st.metric(label="目前股價", value=f"{current_price} {currency}")
            
            st.markdown("---")
            st.subheader("📰 近期相關新聞 (Google 新聞即時整合)")
            
            # 2. 改用 Google News RSS 抓取繁體中文新聞
            # 我們用公司名稱去搜尋 Google 新聞，準確度最高
            search_keyword = company_name if company_name != '未知公司' else ticker
            encoded_keyword = urllib.parse.quote(search_keyword)
            
            # 建立 Google News 搜尋網址 (設定地區為台灣 hl=zh-TW, gl=TW)
            rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
            
            # 解析新聞
            feed = feedparser.parse(rss_url)
            news_entries = feed.entries[:10]  # 只取前 10 條最新新聞
            
            if not news_entries:
                st.warning("⚠️ 該股票近期沒有找到相關新聞。")
            else:
                for entry in news_entries:
                    raw_title = entry.get('title', '無標題')
                    link = entry.get('link', '#')
                    pub_date = entry.get('published', '時間未知')
                    
                    # Google 新聞標題格式通常是：「新聞標題 - 媒體名稱」
                    # 我們手動把它切開，讓畫面更漂亮
                    if " - " in raw_title:
                        title, publisher = raw_title.rsplit(" - ", 1)
                    else:
                        title, publisher = raw_title, "財經媒體"
                    
                    # 簡化時間顯示
                    if pub_date != '時間未知':
                        date_str = pub_date[:16] # 擷取日期與時間段
                    else:
                        date_str = "未知"
                    
                    # 呈現漂亮的摺疊選單
                    with st.expander(f"【{publisher}】 {title}"):
                        st.write(f"**新聞標題：** {title}")
                        st.write(f"**發布來源：** {publisher}")
                        st.write(f"**發布時間：** {date_str}")
                        st.markdown(f"[🔗 點此閱讀新聞原文網頁]({link})")
                        
        except Exception as e:
            st.error(f"❌ 擷取資料失敗！錯誤原因: {e}")