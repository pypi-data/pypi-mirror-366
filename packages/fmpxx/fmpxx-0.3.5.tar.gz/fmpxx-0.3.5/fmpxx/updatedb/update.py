import sys
from pathlib import Path
from typing import List, Dict
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from fmpxx.updatedb.database import FMPDatabase
from fmpxx.quote import Quote

def update_historical_prices(api_key: str, symbol: str, db_path: str = "fmp_data.db", period: int = 1) -> int:
    """
    更新指定股票的日线历史数据
    
    Args:
        api_key (str): FMP API密钥
        symbol (str): 股票代码
        db_path (str): 数据库路径，默认为"fmp_data.db"
        period (int): 获取的年数，默认为1年
        
    Returns:
        int: 更新的记录数
    """
    quote = Quote(api_key)
    df = quote.get_his_daily(symbol, period)
    print(df)
    if df.empty:
        return 0
        
    db = FMPDatabase(db_path)
    updated_count = 0
    
    with db as db:
        # 添加symbol列
        df['symbol'] = symbol
        # 将DataFrame直接写入数据库
        df.to_sql(
            'historical_prices',
            db.conn,
            if_exists='append',
            index=False,
            method='multi'
        )
        updated_count = len(df)
        db.conn.commit()
        
    return updated_count
    
def update_all_prices(api_key: str, symbols: List[str], db_path: str = "fmp_data.db", period: int = 1) -> Dict[str, int]:
    """
    批量更新多个股票的日线历史数据
    
    Args:
        api_key (str): FMP API密钥
        symbols (List[str]): 股票代码列表
        db_path (str): 数据库路径，默认为"fmp_data.db"
        period (int): 获取的年数，默认为1年
        
    Returns:
        Dict[str, int]: 每个股票更新的记录数
    """
    results = {}
    for symbol in symbols:
        count = update_historical_prices(api_key, symbol, db_path, period)
        results[symbol] = count
    return results


if __name__ == "__main__":
    update_historical_prices('aapl',1)
