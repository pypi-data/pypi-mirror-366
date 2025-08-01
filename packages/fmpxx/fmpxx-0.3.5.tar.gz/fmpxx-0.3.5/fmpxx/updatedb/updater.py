from typing import List, Dict
from datetime import datetime
# from .database import FMPDatabase
from fmpxx.financials import Financials

def update_earnings_transcripts(api_key: str, symbol: str, db_path: str = "fmp_data.db", period: int = 3) -> int:
    """
    更新指定股票的财报电话会议记录
    
    Args:
        api_key (str): FMP API密钥
        symbol (str): 股票代码
        db_path (str): 数据库路径，默认为"fmp_data.db"
        period (int): 获取的年数，默认为3年
        
    Returns:
        int: 更新的记录数
    """
    financials = Financials(api_key)
    transcripts = financials.get_earnings_transcript(symbol, period)
    if not transcripts:
        return 0
        
    db = FMPDatabase(db_path)
    updated_count = 0
    
    with db as db:
        cursor = db.conn.cursor()
        
        for transcript in transcripts:
            try:
                # 解析日期
                date = datetime.strptime(transcript["date"], "%Y-%m-%d").strftime("%Y-%m-%d")
                quarter = transcript.get("quarter")
                year = transcript.get("year")
                content = transcript.get("content", "")
                
                cursor.execute("""
                    INSERT OR REPLACE INTO earnings_transcripts 
                    (symbol, date, quarter, year, content)
                    VALUES (?, ?, ?, ?, ?)
                """, (symbol, date, quarter, year, content))
                
                updated_count += 1
            except Exception as e:
                print(f"Failed to insert transcript for {symbol} on {transcript['date']}: {e}")
                
        db.conn.commit()
        
    return updated_count
    
def update_all_transcripts(api_key: str, symbols: List[str], db_path: str = "fmp_data.db", period: int = 3) -> Dict[str, int]:
    """
    批量更新多个股票的财报电话会议记录
    
    Args:
        api_key (str): FMP API密钥
        symbols (List[str]): 股票代码列表
        db_path (str): 数据库路径，默认为"fmp_data.db"
        period (int): 获取的年数，默认为3年
        
    Returns:
        Dict[str, int]: 每个股票更新的记录数
    """
    results = {}
    for symbol in symbols:
        count = update_earnings_transcripts(api_key, symbol, db_path, period)
        results[symbol] = count
    return results
