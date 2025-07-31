import asyncio
import sys
import os

# 正确添加项目根路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
from kxy.framework.context import user_id, user_info, tenant_id, dep_id
from datetime import datetime

user_id.set('43')
tenant_id.set(['0'])
dep_id.set(['0'])
user_info.set({'chineseName':'张三'})

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from test.config import config

engine = create_async_engine(config.mysql_url, pool_size=5,pool_pre_ping=True,pool_recycle=1800, max_overflow=20,echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False,autoflush=False,autocommit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        
from test.test_table_dal import TestTableDal
from test.test_table import TestTable

async def test_table_add():
    async with AsyncSessionLocal() as session:
        dal = TestTableDal('43',session)
        for i in range(10,20):
            tab = TestTable()
            tab.UID=user_id.get()
            tab.UserName = f'张三{i}'
            tab.Sex =1
            tab.ExpiresTime =datetime.now()
            tab.IsDelete = 0
            tab.TenantId = i%3
            tab.DepId=i%3
            await dal.Insert(tab)
async def query():
    async with AsyncSessionLocal() as session:
        dal = TestTableDal(session)
        results,total = await dal.Search({},1,30)
        print(total,[res.DepId for res in results])

loop:asyncio.AbstractEventLoop = asyncio.new_event_loop()
loop.run_until_complete(query())