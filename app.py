import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from crawler import get_recent_reports

# ----------------------------------------------------
# 1. Page Configuration & Custom Styling
# ----------------------------------------------------
st.set_page_config(
    page_title="Stock Discovery Matrix", 
    page_icon="💎", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

def inject_custom_css():
    st.markdown("""
        <style>
        /* Global Background & Typography */
        html, body, [class*="css"] {
            font-family: 'Inter', 'Noto Sans KR', sans-serif;
            background-color: #0f172a; /* Slate 900 */
            color: #f8fafc; /* Slate 50 */
        }
        
        /* 3D Title Styling */
        .main-title {
            text-align: center;
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #38bdf8, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            text-shadow: 0px 4px 15px rgba(129, 140, 248, 0.4);
            animation: fadeIn 1s ease-in-out;
        }
        
        .sub-title {
            text-align: center;
            font-size: 1.2rem;
            color: #94a3b8;
            margin-bottom: 3rem;
        }
        
        /* 3D Glassmorphism Cards */
        .stock-card {
            background: rgba(30, 41, 59, 0.7); /* Slate 800 */
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5), 
                        inset 0 1px 0 rgba(255,255,255,0.1);
            position: relative;
            overflow: hidden;
        }
        
        .stock-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 40px -10px rgba(56, 189, 248, 0.2), 
                        0 0 20px rgba(129, 140, 248, 0.3);
            border: 1px solid rgba(129, 140, 248, 0.4);
        }
        
        /* Rank Badge */
        .rank-badge {
            position: absolute;
            top: -10px;
            left: -10px;
            background: linear-gradient(135deg, #f59e0b, #ef4444);
            color: white;
            padding: 10px 20px;
            border-radius: 0 0 16px 0;
            font-weight: bold;
            font-size: 1.2rem;
            box-shadow: 3px 3px 10px rgba(0,0,0,0.3);
        }
        
        /* Neon Links */
        .naver-link {
            display: inline-block;
            margin-top: 15px;
            padding: 10px 20px;
            background: linear-gradient(90deg, #10b981, #059669);
            color: white !important;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
            text-align: center;
        }
        
        .naver-link:hover {
            background: linear-gradient(90deg, #34d399, #10b981);
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6);
            transform: translateY(-2px);
        }
        
        /* Mention Tags */
        .mention-tag {
            display: inline-block;
            background: rgba(56, 189, 248, 0.2);
            color: #38bdf8;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            margin-right: 8px;
            margin-bottom: 8px;
            border: 1px solid rgba(56, 189, 248, 0.3);
        }
        
        /* Report Title List */
        .report-list {
            list-style: none;
            padding: 0;
            margin-top: 15px;
        }
        .report-list li {
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            font-size: 0.95rem;
            color: #cbd5e1;
        }
        .report-list li::before {
            content: "✨";
            margin-right: 8px;
            font-size: 0.8rem;
        }
        
        /* Image Chart Styling */
        .chart-img {
            width: 100%;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        /* Custom Button */
        div.stButton > button {
            background: linear-gradient(135deg, #6366f1, #a855f7);
            color: white;
            border: none;
            padding: 0.5rem 2rem;
            border-radius: 12px;
            font-weight: bold;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
            width: 100%;
        }
        
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(168, 85, 247, 0.6);
        }
        </style>
    """, unsafe_allow_html=True)

# ----------------------------------------------------
# 2. Helper Functions
# ----------------------------------------------------
def draw_candlestick(df, title=""):
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])
    fig.update_layout(
        title=title,
        template="plotly_dark",
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_rangeslider_visible=False
    )
    return fig

# ----------------------------------------------------
# 3. Main Logic & Layout
# ----------------------------------------------------
def main():
    inject_custom_css()
    
    # Header
    st.markdown('<div class="main-title">🚀 Stock Discovery Matrix</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">네이버 증권 리서치 기반 실적 호조 기업 강력 추천 (3D View)</div>', unsafe_allow_html=True)
    
    # Controls
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_days = st.select_slider(
            "분석 기간 선택",
            options=[3, 5, 10],
            value=5,
            format_func=lambda x: f"최근 {x}일"
        )
        search_btn = st.button("🔍 강력 종목 발굴하기 (Search)")
            
    st.markdown("<br><br>", unsafe_allow_html=True)

    if search_btn:
        st.session_state['search_clicked'] = True
        st.session_state['search_days'] = search_days
        
    if st.session_state.get('search_clicked', False):
        current_search_days = st.session_state.get('search_days', 5)
        
        # Use cache or just fetch (in real scenario, we should use cache for performance)
        with st.spinner("네이버 증권 리버스를 탐색 중입니다..."):
            reports_data = get_recent_reports(days=current_search_days)
            
        if not reports_data:
            st.warning(f"최근 {current_search_days}일 동안 등록된 종목 리포트가 없습니다.")
            return
            
        st.success(f"🔥 추천 종목 Top {min(20, len(reports_data))} 발굴 완료!")
        
        # DataFrame for Export
        export_list = []
        for rank, item in enumerate(reports_data[:20]):
            y_data = item.get('yfinance', {})
            export_list.append({
                '순위': rank + 1,
                '종목명': item['stock_name'],
                '종목코드': item['stock_code'],
                '언급빈도': item['mentions'],
                '총점': item['total_score'],
                '현재가': y_data.get('current_price', 'N/A'),
                '목표가': y_data.get('target', 'N/A'),
                '수익여력(%)': round(((y_data.get('target', 0) - y_data.get('current_price', 0)) / y_data.get('current_price', 1)) * 100, 1) if isinstance(y_data.get('target'), (int,float)) and isinstance(y_data.get('current_price'), (int,float)) and y_data.get('current_price') > 0 else 'N/A',
                '투자의견': y_data.get('recommendation', 'N/A'),
                '기술적추세': y_data.get('status', 'N/A')
            })
        export_df = pd.DataFrame(export_list)
        csv_data = export_df.to_csv(index=False).encode('utf-8-sig')
        
        col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
        with col_btn2:
            st.download_button(
                label="📥 종목 리스트 엑셀(CSV) 다운로드",
                data=csv_data,
                file_name="stock_recommendation_list.csv",
                mime="text/csv",
                use_container_width=True
            )
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Display Results
        for idx, item in enumerate(reports_data[:20]):
            rank = idx + 1
            code = item['stock_code']
            chart_url = f"https://ssl.pstatic.net/imgfinance/chart/item/area/day/{code}.png"
            naver_finance_url = f"https://finance.naver.com/item/main.naver?code={code}"
            
            # Calculate unique brokers
            unique_brokers = list(set([r['broker'] for r in item['reports']]))
            
            # Format report titles as clickable links
            reports_html = "<ul class='report-list'>" + "".join([
                f"<li><a href='{r['link']}' target='_blank' style='color:#cbd5e1; text-decoration:none; transition: color 0.3s;' onmouseover='this.style.color=\"#38bdf8\"' onmouseout='this.style.color=\"#cbd5e1\"'>[{r['broker']}] {r['title']}</a></li>" 
                for r in item['reports'][:4]
            ]) + "</ul>"
            
            # Card Layout
            html_card = f"""
            <div class="stock-card">
                <div class="rank-badge">#{rank}</div>
                <div style="padding-left: 10px;">
                    <h2 style="margin-bottom: 5px; color: #f8fafc;">{item['stock_name']} <span style="font-size: 1rem; color: #94a3b8;">({code})</span></h2>
                    <div>
                        <span class="mention-tag">🔥 언급빈도: {item['mentions']}회</span>
                        <span class="mention-tag">⭐ 총점: {item['total_score']}점</span>
                        <span class="mention-tag">🏢 증권사: {', '.join(unique_brokers[:3])}</span>
                    </div>
                </div>
            </div>
            """
            
            # Use Streamlit columns inside the container to mix HTML and Streamlit elements (like images/buttons if needed, but HTML is prettier)
            col_a, col_b = st.columns([1.5, 1])
            # YFinance Technical Data
            yf_data = item.get('yfinance', {})
            yf_status = yf_data.get('status', '데이터 없음')
            yf_target = yf_data.get('target', 'N/A')
            yf_pe = yf_data.get('pe', 'N/A')
            yf_rec = yf_data.get('recommendation', 'N/A')
            yf_curr = yf_data.get('current_price', 'N/A')
            
            with col_a:
                st.markdown(html_card, unsafe_allow_html=True)
                
                curr_price_str = f"{format(yf_curr, ',')}원" if isinstance(yf_curr, (int, float)) else "N/A"
                target_str = f"{format(yf_target, ',')}원" if isinstance(yf_target, (int, float)) else "N/A"
                
                delta_str = None
                if isinstance(yf_curr, (int, float)) and isinstance(yf_target, (int, float)) and yf_curr > 0:
                    delta_pct = ((yf_target - yf_curr) / yf_curr) * 100
                    delta_str = f"{delta_pct:+.1f}%"
                
                m1, m2 = st.columns(2)
                m1.metric("📌 현재가", curr_price_str)
                m2.metric("🎯 목표가 (평균)", target_str, delta=delta_str)
                
                tech_html = f"""
                <div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; margin-bottom:15px; margin-top:10px;">
                    <p style="margin:5px 0; font-size:0.95rem;"><b>차트 배열(추세):</b> {yf_status}</p>
                    <p style="margin:5px 0; font-size:0.95rem;"><b>PER (Trailing):</b> {yf_pe}</p>
                    <p style="margin:5px 0; font-size:0.95rem;"><b>투자의견(글로벌):</b> {yf_rec}</p>
                </div>
                """
                st.markdown(tech_html, unsafe_allow_html=True)
                
                st.markdown(f"**📈 애널리스트 리포트 원문 (클릭 시 이동):**", unsafe_allow_html=True)
                st.markdown(reports_html, unsafe_allow_html=True)
                st.markdown(f'<br><a href="{naver_finance_url}" target="_blank" class="naver-link">네이버 증권 바로가기 ➔</a>', unsafe_allow_html=True)
                
            with col_b:
                st.markdown("<div style='padding-top:20px;'></div>", unsafe_allow_html=True)
                
                hist_df = yf_data.get('hist')
                if hist_df is not None and not hist_df.empty:
                    # Daily (Last 120 trading days roughly 6 months)
                    day_df = hist_df.tail(120)
                    # Weekly
                    week_df = hist_df.resample('W').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'})
                    week_df = week_df.dropna()
                    # Monthly
                    month_df = hist_df.resample('ME').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'})
                    month_df = month_df.dropna()
                    
                    tab1, tab2, tab3 = st.tabs(["일봉 (Day)", "주봉 (Week)", "월봉 (Month)"])
                    with tab1:
                        st.plotly_chart(draw_candlestick(day_df, "일일 가격 추이"), use_container_width=True)
                    with tab2:
                        st.plotly_chart(draw_candlestick(week_df, "주간 가격 추이"), use_container_width=True)
                    with tab3:
                        st.plotly_chart(draw_candlestick(month_df, "월간 가격 추이"), use_container_width=True)
                else:
                    st.info("차트 데이터를 불러오지 못했습니다.")
            
            st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.05); margin: 30px 0;'>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
