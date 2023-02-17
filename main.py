import datetime
from enum import Enum
from pathlib import Path

import pandas as pd
from pykrx import stock

OUTPUT_PATH = Path("/Users/mindongsung/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian Vault/51 주식/51.12 상한가 천만주 정리")

class Market(Enum):
    KOSPI = 'KOSPI'
    KOSDAQ = 'KOSDAQ'    

def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

def get_today(format: str = "%Y%m%d"):
    return datetime.datetime.strftime(datetime.datetime.now(), format)

def get_10B(market: Market, today: str)->pd.DataFrame:
    df = stock.get_market_ohlcv(today, market = market.value)
    result = df.loc[df['거래량'] > 10_000_000].sort_values(by='거래량', ascending=False)
    result['종목명'] = [stock.get_market_ticker_name(t) for t in result.index]
    return result

def get_upper_limit(market: Market, today: str)->pd.DataFrame:
    result = stock.get_market_ohlcv(today, market = market.value).query("등락률 > 29").sort_values('등락률', ascending=False)
    result['종목명'] = [stock.get_market_ticker_name(t) for t in result.index]
    return result

def create_document():
    results = create_tag_document()
    results += create_upper_limit_document()
    results += create_10B_document()
    return results

def create_tag_document():
    return """---
tags: [주식, 상한가, 천만주]
---\n"""

def create_upper_limit_document():
    result = f"# [[{get_today(format = '%Y-%m-%d')}]] 상한가\n"
    df = pd.concat([get_upper_limit(Market.KOSPI, get_today(format = "%Y%m%d")), get_upper_limit(Market.KOSDAQ, get_today(format = "%Y%m%d"))]).sort_values('등락률', ascending=False)
    result += dataframe_to_markdown(df)
    return result

def create_10B_document():
    result = f"# [[{get_today(format = '%Y-%m-%d')}]] 천만주\n"
    df = pd.concat([get_10B(Market.KOSPI, get_today(format = "%Y%m%d")), get_10B(Market.KOSDAQ, get_today(format = "%Y%m%d"))]).sort_values('거래량', ascending=False)
    result += dataframe_to_markdown(df)
    return result

def dataframe_to_markdown(df: pd.DataFrame):
    return "".join(
        f"## [[{row['종목명']}]] (등락률 = {round(row['등락률'], 2)}, 거래량 = {human_format(row['거래량'])})\n\n"
        for _, row in df.iterrows()
    )    
def save_document(document, output_file_path):
    assert not output_file_path.exists()
    with open(OUTPUT_PATH / f"{get_today(format = '%Y-%m-%d')} 상한가 천만주.md", "w") as f:
        f.write(document)
    
def main():
    output_file_path = OUTPUT_PATH / f"{get_today(format = '%Y-%m-%d')} 상한가 천만주.md"
    if not output_file_path.exists():
        document = create_document()
        save_document(document, output_file_path)
    
if __name__ == '__main__':
    main()
