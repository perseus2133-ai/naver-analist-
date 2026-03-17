# 🚀 Stock Discovery Matrix

네이버 증권 리서치 데이터를 바탕으로 최근 3일, 5일, 10일간 **가장 많이 언급되고 실적이 좋은 종목**을 발굴해 주는 3D UI 기반의 지능형 Streamlit 애플리케이션입니다.

## ✨ 주요 기능 (Key Features)

*   **웹 크롤러 내장**: 실시간으로 네이버 증권 종목분석 게시판의 데이터를 수집하여 긍정 키워드(실적 호조, 매수, 상향 등)가 포함된 리포트를 분석합니다.
*   **프리미엄 3D UI**: Glassmorphism(글래스모피즘) 카드와 CSS 애니메이션을 통해 입체적이고 화려한 사용자 경험을 제공합니다.
*   **딥 다이브 펀더멘털 분석**: `yfinance` 라이브러리를 연동하여, 크롤링된 추천 종목의 실시간 이동평균선(20/60/120일) 추세, PER(주가수익비율), 그리고 글로벌 투자 등급을 즉시 확인합니다.
*   **원클릭 리포트 원문 연결**: 카드에 나열된 요약 리포트 제목이나 '네이버 증권 바로가기' 버튼을 클릭하여 즉시 원문과 차트 정보를 자세히 볼 수 있습니다.

## 📦 설치 및 실행 방법 (How to Run)

1. **저장소 클론 및 폴더 이동**
   ```bash
   git clone <your-repo-url>
   cd stock-discovery-matrix
   ```

2. **필요 패키지 설치**
   앱 실행에 필요한 파이썬 라이브러리들을 설치합니다.
   ```bash
   pip install -r requirements.txt
   ```

3. **Streamlit 서버 실행**
   터미널에서 아래 명령어를 실행하면, 브라우저가 열리며 앱이 시작됩니다.
   ```bash
   streamlit run app.py
   ```

## 🛠️ 기술 스택 (Tech Stack)
*   **Python 3**
*   **Streamlit** (Frontend Web UI & Custom CSS)
*   **BeautifulSoup4 & Requests** (Web Crawling)
*   **Pandas** (Data Transformation)
*   **yfinance** (Live Stock Technical Analysis)
