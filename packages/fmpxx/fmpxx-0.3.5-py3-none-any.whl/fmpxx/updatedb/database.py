import sqlite3
from pathlib import Path
from typing import Optional

class FMPDatabase:
    """管理FMP数据的SQLite数据库"""
    
    def __init__(self, db_path: str = "fmp_data.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        
    def connect(self) -> sqlite3.Connection:
        """连接到数据库，如果不存在则创建"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        return self.conn
        
    def initialize(self) -> None:
        """初始化数据库表结构"""
        with self.connect() as conn:
            # 创建日线历史数据表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS historical_prices (
                    symbol TEXT NOT NULL,
                    date TEXT NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    PRIMARY KEY (symbol, date)
                )
            """)
            
            # 创建财务数据表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS financials (
                    symbol TEXT NOT NULL,
                    date TEXT NOT NULL,
                    revenue REAL,
                    net_income REAL,
                    total_assets REAL,
                    total_liabilities REAL,
                    operating_cash_flow REAL,
                    PRIMARY KEY (symbol, date)
                )
            """)
            
            # 创建财报电话会议表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS earnings_transcripts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date TEXT NOT NULL,
                    quarter INTEGER,
                    year INTEGER,
                    content TEXT,
                    UNIQUE(symbol, date)
                )
            """)
            
            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_symbol ON historical_prices(symbol)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_financials_symbol ON financials(symbol)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_transcripts_symbol ON earnings_transcripts(symbol)")
            
    def close(self) -> None:
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
            
    def __enter__(self):
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
