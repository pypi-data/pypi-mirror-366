import os
import mariadb
import sys
from sqlalchemy import create_engine
from dotenv import load_dotenv


### LOAD ENV
load_dotenv()


engine = None

def get_pd_remote():
    global engine
    try:
        # Use environment variables or defaults
        DB_HOST = os.environ.get("DB_HOST", "localhost")
        DB_PORT = int(os.environ.get("DB_PORT", 3307))
        DB_USER = os.environ.get("DB_USER", "root")
        DB_PASSWORD = os.environ.get("DB_PASSWORD", "root")
        DB_NAME = os.environ.get("DB_NAME", "dtuser_DASH")

        if engine is None:
            engine = create_engine(
                f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
                pool_size=100,
                max_overflow=0,
                pool_timeout=120,
            )
            return engine
        else:
            return engine

    except Exception as e:
        print(f"❌ Error connecting to DB Platform: {e}")
        return None
