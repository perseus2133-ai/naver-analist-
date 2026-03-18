import streamlit as st
import pandas as pd

# ----------------------------------------------------
# 1. Page Configuration & Custom Styling
# ----------------------------------------------------
st.set_page_config(
    page_title="Stock Discovery Matrix",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 크롤러 import를 try/except로 감싸서 import 실패 시에도 앱이 뜨도록
try:
    from crawler import get_recent_reports
    CRAWLER_OK = True
except Exception as e:
    CRAWLER_OK = False
    CRAWLER_ERROR = str(e)

def inject_custom_css():
    st.markdown("""
        <style>
        /* Global Background & Typography */
        .stApp {
            background-color: #0f172a !important;
        }

        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
        [data-testid="stToolbar"], section[data-testid="stSidebar"],
        .main, .main .block-container, .stMainBlockContainer {
            font-family: 'Inter', 'Noto Sans KR', sans-serif;
            background-color: #0f172a !important;
            color: #f8fafc !important;
        }

        /* Streamlit 기본 요소 텍스트 색상 강제 적용 */
        .stApp label, .stApp .stMarkdown, .stApp .stMarkdown p,
        .stApp span, .stApp h1, .stApp h2, .stApp h3,
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] span {
            color: #f8fafc !important;
        }

        /* select_slider 라벨 */
        .stSlider label, .stSelectSlider label {
            color: #f8fafc !important;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* 3D Title Styling */
        .main-title {
            text-align: center;
            font-size: 3.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #38bdf8, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
            animation: fadeIn 1s ease-in-out;
        }

        .sub-title {
            text-align: center;
            font-size: 1.2rem;
            color: #94a3b8 !important;
            margin-bottom: 3rem;
        }

        /* 3D Glassmorphism Cards */
        .stock-card {
            background: rgba(30, 41, 59, 0.7);
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
            background: linear-gradient(135deg, #6366f1, #a855f7) !important;
            color: white !important;
            border: none !important;
            padding: 0.5rem 2rem;
            border-radius: 12px !important;
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
# 2. Main Logic & Layout
# ----------------------------------------------------
def main():
    inject_custom_css()

    # Header
    st.markdown('<div class="main-title">Stock Discovery Matrix</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">네이버 증권 리서치 기반 실적 호조 기업 강력 추천 (3D View)</div>', unsafe_allow_html=True)

    # 크롤러 로드 실패 시 에러 표시
    if not CRAWLER_OK:
        st.error(f"크롤러 모듈 로드 실패: {CRAWLER_ERROR}")
        return

    # Controls
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_days = st.select_slider(
            "분석 기간 선택",
            options=[3, 5, 10],
            value=5,
            format_func=lambda x: f"최근 {x}일"
        )
        search_btn = st.button("강력 종목 발굴하기 (Search)")

    st.markdown("<br><br>", unsafe_allow_html=True)

    if search_btn:
        with st.spinner("네이버 증권 리서치를 탐색 중입니다..."):
            try:
                reports_data = get_recent_reports(days=search_days)
            except Exception as e:
                st.error(f"크롤링 중 오류 발생: {e}")
                return

        if not reports_data:
            st.warning(f"최근 {search_days}일 동안 등록된 종목 리포트가 없습니다.")
            return

        st.success(f"추천 종목 Top {min(20, len(reports_data))} 발굴 완료!")

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
                        <span class="mention-tag">언급빈도: {item['mentions']}회</span>
                        <span class="mention-tag">총점: {item['total_score']}점</span>
                        <span class="mention-tag">증권사: {', '.join(unique_brokers[:3])}</span>
                    </div>
                </div>
            </div>
            """

            col_a, col_b = st.columns([1.5, 1])
            # YFinance Technical Data
            yf_data = item.get('yfinance', {})
            yf_status = yf_data.get('status', '데이터 없음')
            yf_target = yf_data.get('target', 'N/A')
            yf_pe = yf_data.get('pe', 'N/A')
            yf_rec = yf_data.get('recommendation', 'N/A')

            tech_html = f"""
            <div style="background:rgba(255,255,255,0.05); padding:15px; border-radius:10px; margin-bottom:15px;">
                <h4 style="margin-top:0; color:#38bdf8;">딥 다이브 분석 (심화)</h4>
                <p style="margin:5px 0; font-size:0.95rem;"><b>차트 배열(추세):</b> {yf_status}</p>
                <p style="margin:5px 0; font-size:0.95rem;"><b>목표주가 추정치:</b> {yf_target}</p>
                <p style="margin:5px 0; font-size:0.95rem;"><b>PER (Trailing):</b> {yf_pe}</p>
                <p style="margin:5px 0; font-size:0.95rem;"><b>투자의견(글로벌):</b> {yf_rec}</p>
            </div>
            """

            with col_a:
                st.markdown(html_card, unsafe_allow_html=True)
                st.markdown(tech_html, unsafe_allow_html=True)
                st.markdown("**애널리스트 리포트 원문 (클릭 시 이동):**")
                st.markdown(reports_html, unsafe_allow_html=True)
                st.markdown(f'<br><a href="{naver_finance_url}" target="_blank" class="naver-link">네이버 증권 바로가기</a>', unsafe_allow_html=True)

            with col_b:
                st.markdown(f"""
                <div style="padding-top: 20px;">
                    <img src="{chart_url}" class="chart-img">
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.05); margin: 30px 0;'>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
