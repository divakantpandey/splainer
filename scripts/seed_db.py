import logging
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime
from datetime import datetime, timedelta

from spl_to_sql.config import SplToSqlConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_database():
    config = SplToSqlConfig.from_env()
    conn_str = config.database.connection_string.get_secret_value()
    
    if not conn_str:
        logger.error("DB_CONNECTION_STRING is not set in environment or infra/.env")
        return
        
    engine = create_engine(conn_str)
    metadata = MetaData()
    
    # 1. 'main' table (for: search index=main | stats count by host)
    Table(
        'main', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('_time', DateTime, default=datetime.utcnow),
        Column('host', String(64), nullable=False)
    )
    
    # 2. 'web' table (for: search index=web | stats avg(response_time) by endpoint)
    Table(
        'web', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('_time', DateTime, default=datetime.utcnow),
        Column('endpoint', String(255), nullable=False),
        Column('response_time', Float, nullable=False),
        Column('status', Integer, nullable=False)
    )
    
    # 3. 'app' table (for: search index=app source=api.log | transaction request_id ...)
    Table(
        'app', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('timestamp', DateTime, default=datetime.utcnow), # Common in LLM queries
        Column('source', String(255), nullable=False),
        Column('request_id', String(64), nullable=False),
        Column('message', String(255), nullable=True)
    )
    
    logger.info("Dropping existing tables (main, web, app)...")
    metadata.drop_all(engine)
    
    logger.info("Creating tables (main, web, app)...")
    metadata.create_all(engine)
    
    logger.info("Inserting dummy golden data...")
    now = datetime.utcnow()
    
    with engine.begin() as conn:
        # Seed 'main'
        conn.execute(metadata.tables['main'].insert(), [
            {"host": "server-01", "_time": now},
            {"host": "server-01", "_time": now},
            {"host": "server-02", "_time": now},
        ])
        
        # Seed 'web'
        conn.execute(metadata.tables['web'].insert(), [
            {"endpoint": "/api/v1/users", "response_time": 45.2, "status": 200, "_time": now},
            {"endpoint": "/api/v1/users", "response_time": 50.1, "status": 200, "_time": now},
            {"endpoint": "/api/v1/login", "response_time": 120.5, "status": 401, "_time": now},
        ])
        
        # Seed 'app' - creating a transaction that spans 10 seconds (duration > 5)
        # Transaction 1: > 5s
        conn.execute(metadata.tables['app'].insert(), [
            {"source": "api.log", "request_id": "REQ-1001", "message": "API_START", "timestamp": now - timedelta(seconds=20)},
            {"source": "api.log", "request_id": "REQ-1001", "message": "API_END", "timestamp": now - timedelta(seconds=10)},
        ])
        
        # Transaction 2: < 5s (Should be filtered out by where duration > 5)
        conn.execute(metadata.tables['app'].insert(), [
            {"source": "api.log", "request_id": "REQ-1002", "message": "API_START", "timestamp": now - timedelta(seconds=5)},
            {"source": "api.log", "request_id": "REQ-1002", "message": "API_END", "timestamp": now - timedelta(seconds=2)},
        ])
        
    logger.info("Database seeding complete!")

if __name__ == "__main__":
    seed_database()

