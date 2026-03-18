import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import re
import time

def get_recent_reports(days=3):
    """
    네이버 증권 리서치 페이지에서 최근 'days' 일간의 리포트를 크롤링합니다.
    """
    base_url = "https://finance.naver.com/research/company_list.naver"

    # 목표 날짜를 계산 (형식: YY.MM.DD)
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%y.%m.%d')

    page = 1
    reports = []

    # 최대 50페이지까지만 탐색 (무한루프 방지)
    while page <= 50:
        url = f"{base_url}?&page={page}"
        try:
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            res.raise_for_status()
        except requests.RequestException as e:
            print(f"[경고] 페이지 {page} 요청 실패: {e}")
            break
        soup = BeautifulSoup(res.text, 'html.parser')

        table = soup.find('table', class_='type_1')
        if not table:
            break

        rows = table.find_all('tr')
        valid_page = False

        for row in rows:
            tds = row.find_all('td')
            if len(tds) < 6:
                continue

            stock_name_td = tds[0]
            title_td = tds[1]
            broker_td = tds[2]
            date_td = tds[4]

            date_str = date_td.text.strip()

            # 날짜 형식 검증 (YY.MM.DD)
            if not re.match(r'\d{2}\.\d{2}\.\d{2}', date_str):
                continue

            # 기준일자보다 오래된 리포트면 중단
            if date_str < cutoff_date:
                return process_reports(reports)

            stock_a = stock_name_td.find('a')
            if not stock_a:
                continue

            stock_name = stock_a.text.strip()
            # 버그 수정: .naver와 .nhn 모두 대응 (code= 파라미터만 추출)
            stock_code_match = re.search(r'code=(\d+)', stock_a.get('href', ''))
            stock_code = stock_code_match.group(1) if stock_code_match else ""

            if not stock_code:
                continue

            title_a = title_td.find('a')
            title = title_a.text.strip() if title_a else title_td.text.strip()
            title = re.sub(r'[\r\n\t]+', ' ', title).strip() # 줄바꿈 제거

            # 버그 수정: 절대경로/상대경로 모두 올바르게 처리
            if title_a and title_a.get('href'):
                href = title_a['href']
                if href.startswith('http'):
                    link = href
                elif href.startswith('/'):
                    link = "https://finance.naver.com" + href
                else:
                    link = "https://finance.naver.com/research/" + href
            else:
                link = ""

            broker = broker_td.text.strip()

            reports.append({
                'date': date_str,
                'stock_name': stock_name,
                'stock_code': stock_code,
                'title': title,
                'broker': broker,
                'link': link
            })
            valid_page = True

        if not valid_page:
            break

        page += 1
        time.sleep(0.3)  # 요청 간 딜레이 (차단 방지)

    return process_reports(reports)

def process_reports(reports):
    """
    수집된 리포트들을 분석하여 점수를 매기고, 종목별로 그룹화하여 랭킹을 산출합니다.
    """
    if not reports:
        return []

    df = pd.DataFrame(reports)

    # 긍정적인 평가 키워드
    positive_keywords = [
        '실적', '호조', '상향', 'buy', '매수', '성장', '흑자',
        '기대', '강세', '목표가', '돌파', '개선', '확대', '최대', '컨센서스', '추천'
    ]

    def calculate_score(title):
        score = 1 # 기본 언급 점수
        title_lower = title.lower()
        for kw in positive_keywords:
            if kw in title_lower:
                score += 1
        return score

    df['score'] = df['title'].apply(calculate_score)
    df['is_positive'] = df['score'] > 1

    df['report_data'] = df.apply(lambda row: {'title': row['title'], 'broker': row['broker'], 'link': row['link']}, axis=1)

    # 종목별 그룹화
    grouped = df.groupby(['stock_code', 'stock_name']).agg(
        mentions=('stock_code', 'count'),
        total_score=('score', 'sum'),
        reports=('report_data', lambda x: list(x))
    ).reset_index()

    # 정렬: 1. 총합 점수 높은순, 2. 언급 빈도 높은순
    grouped = grouped.sort_values(by=['total_score', 'mentions'], ascending=[False, False])

    # 상위 20개만 추출하여 yfinance로 차트/단기 추세 데이터 보강
    top_20 = grouped.head(20).to_dict('records')

    import yfinance as yf
    for item in top_20:
        code = item['stock_code']
        # KOSPI(.KS) 또는 KOSDAQ(.KQ) 시도
        y_data = {'status': "추세 데이터 없음", 'pe': "N/A", 'target': "N/A", 'recommendation': "N/A"}
        for suffix in ['.KS', '.KQ']:
            ticker = f"{code}{suffix}"
            try:
                stock_yf = yf.Ticker(ticker)
                # 버그 수정: 6mo -> 1y (MA120 계산에 충분한 데이터 확보)
                hist = stock_yf.history(period="1y")
                if not hist.empty and len(hist) >= 20:
                    # 이동평균선 계산
                    hist['MA20'] = hist['Close'].rolling(window=20).mean()
                    hist['MA60'] = hist['Close'].rolling(window=60).mean()
                    hist['MA120'] = hist['Close'].rolling(window=120).mean()

                    last_close = hist['Close'].iloc[-1]
                    ma20 = hist['MA20'].iloc[-1]
                    ma60 = hist['MA60'].iloc[-1]
                    ma120 = hist['MA120'].iloc[-1]

                    status = "혼조세 (추세 전환 또는 횡보)"
                    if pd.notna(ma120):
                        if last_close > ma20 > ma60 > ma120:
                            status = "📈 완벽한 정배열 (강한 상승 추세)"
                        elif last_close < ma20 < ma60 < ma120:
                            status = "📉 완벽한 역배열 (강한 하락 추세)"
                        elif last_close > ma20 and last_close > ma60:
                            status = "↗️ 단기 상승 추세 (MA20/60 상회)"
                        elif last_close < ma20 and last_close < ma60:
                            status = "↘️ 단기 하락 추세 (MA20/60 하회)"
                    elif pd.notna(ma60):
                        # MA120 데이터 없을 때 MA60으로 판단
                        if last_close > ma20 > ma60:
                            status = "↗️ 단기 상승 추세 (MA20/60 상회)"
                        elif last_close < ma20 < ma60:
                            status = "↘️ 단기 하락 추세 (MA20/60 하회)"
                    y_data['status'] = status

                    # 밸류에이션 및 컨센서스 (수집 가능시)
                    info = stock_yf.info
                    pe = info.get('trailingPE', info.get('forwardPE', 'N/A'))
                    # 버그 수정: pe가 None일 수 있음
                    if pe is not None and pe != 'N/A':
                        y_data['pe'] = round(pe, 2)
                    y_data['target'] = info.get('targetMeanPrice', 'N/A')
                    rec = info.get('recommendationKey', 'N/A')
                    # 버그 수정: recommendationKey가 None일 수 있음
                    if rec and isinstance(rec, str):
                        y_data['recommendation'] = rec.replace('_', ' ').title()
                    else:
                        y_data['recommendation'] = 'N/A'
                    break # 성공 시 루프 종료
            except Exception:
                continue
        item['yfinance'] = y_data

    return top_20

if __name__ == "__main__":
    # Test crawler
    data = get_recent_reports(3)
    for idx, item in enumerate(data[:3]):
        print(f"{idx+1}. {item['stock_name']} (점수: {item['total_score']}, 언급: {item['mentions']})")
