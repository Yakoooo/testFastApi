from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 创建引擎和会话
engine = create_engine(
    settings.database_url,
     echo=True
)

sessionLocal = sessionmaker(
    bind=engine
)
