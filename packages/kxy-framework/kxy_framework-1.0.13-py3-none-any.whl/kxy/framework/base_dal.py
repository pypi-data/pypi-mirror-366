# coding=UTF-8

import asyncio
from datetime import datetime
import json
from typing import Dict, List as TypeList,TypeVar, Generic, Union
from sqlalchemy.orm import declarative_base,load_only

from kxy.framework.base_config import BaseConfig
from kxy.framework.base_entity import BaseEntity
from kxy.framework.mapper import Mapper
from .context import user_id,user_info,tenant_id,dep_id
from .friendly_exception import FriendlyException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update,delete,insert, func,text

T = TypeVar("T", bound=declarative_base)

class BaseDal(Generic[T]):
    def __init__(self,modal:T,session:AsyncSession,**kwargs):
        self.session = session
        self.UserId = kwargs.get('UserId',user_id.get())
        '''操作用户Id'''
        self.UserName = kwargs.get('UserName',user_info.get().get('chineseName',''))
        self.AutoCommit=kwargs.get('AutoCommit',True)
        self.modal = modal
    # 添加一个方法来自动为查询添加额外过滤
    def _add_extend_filter(self, filters):
        """
        自动为查询条件添加租户过滤
        """
        filters_copy= list(filters)
        # 检查模型类是否有 tenant_field 属性（由 TenantData 注解添加）
        if hasattr(self.modal, 'tenant_field'):
            # 获取租户字段名称
            tenant_field_name = self.modal.tenant_field
            # 检查模型实例是否有对应的租户字段
            if hasattr(self.modal, tenant_field_name):
                # 获取租户字段值（这里假设从某个地方获取租户ID，例如从上下文或会话中）
                # 你可能需要根据实际情况调整 tenant_id 的获取方式
                tenant_ids = tenant_id.get()
                if tenant_ids:
                    # 构造租户过滤条件
                    tenant_filter = getattr(self.modal, tenant_field_name).in_(tenant_ids)
                    filters_copy.append(tenant_filter)
        if hasattr(self.modal, 'dep_field'):
            dep_field_name = self.modal.dep_field
            if hasattr(self.modal, tenant_field_name):
                dep_ids = dep_id.get()
                if dep_ids:
                    # 构造部门过滤条件
                    dep_filter = getattr(self.modal, dep_field_name).in_(dep_ids)
                    filters_copy.append(dep_filter)
        return filters_copy

    async def BeginTransaction(self):
        if not self.session.in_transaction():
            await self.session.begin()
        self.AutoCommit=False
    async def __aenter__(self):
        await self.BeginTransaction()
        return self
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.Rollback()
        else:
            await self.CommitTransaction()
    async def CommitTransaction(self):
        self.AutoCommit=True
        await self.session.commit()
    async def Rollback(self):
        self.AutoCommit=True
        await self.session.rollback()
    async def Commit(self):
        await self.session.commit()
    async def IfCommit(self):
        if self.AutoCommit:
            await self.session.commit()
        
    async def TryCommit(self, entity):
        try:
            self.session.add(entity)
            await self.IfCommit()
        except Exception as ex:
            await self.session.rollback()
            raise ex
    async def Insert(self, entity):
        entity.CreateUser = self.UserId
        entity.CreateDate = datetime.now()
        entity.LastModifiedUser = self.UserId
        entity.LastModifiedDate = datetime.now()
        self.AddLogger('新增',entity)
        await self.TryCommit(entity)
    async def BatchInsert(self, entities: TypeList[T]):
        """
        批量插入实体列表，提升插入效率

        Args:
            entities (TypeList[T]): 待插入的实体列表
        """
        for entity in entities:
            entity.CreateUser = self.UserId
            entity.CreateDate = datetime.now()
            entity.LastModifiedUser = self.UserId
            entity.LastModifiedDate = datetime.now()
            self.session.add(entity)
        try:
            self.AddLogger('批量新增',entities)
            await self.IfCommit()
        except Exception as ex:
            await self.session.rollback()
            raise FriendlyException(f"批量插入失败: {str(ex)}")
    async def Update(self, entity):
        entity.LastModifiedUser = self.UserId
        entity.LastModifiedDate = datetime.now()
        self.AddLogger('更新',entity)
        await self.TryCommit(entity)

    async def Delete(self, id):
        entity = await self.Get(id)
        entity.Status = 10
        entity.IsDelete = 1
        self.AddLogger('逻辑删除',f'删除id为{id}的数据')
        await self.Update(entity)
    async def DeleteBatch(self,ids,status=10):
        if len(ids):
            fil=[self.modal.Id.in_(ids)]
            self.AddLogger('批量逻辑删除',f'删除id为{ids}的数据')
            await self.UpdateFields(fil,{self.modal.Status: status})

    async def TrueDel(self, id):
        self.AddLogger('物理删除',f'删除id为{id}的数据')
        if self.AutoCommit:
            fil = [self.modal.Id == str(id)]
            fil = self._add_extend_filter(fil)
            await self.session.execute(delete(self.modal).where(*fil))
            await self.IfCommit()
        else:
            entity =await self.Get(id)
            if entity: await self.session.delete(entity)
    async def TrueDelWhere(self,fil:TypeList[object]):
        if self.AutoCommit:
            filters = self._add_extend_filter(fil)
            sql = delete(self.modal).where(*filters)
            self.AddLogger('物理删除',f'删除语句为{sql}')
            await self.session.execute(sql)
            await self.IfCommit()
        else:
            entitys =await self.QueryALL(fil)
            for entity in entitys:
                self.AddLogger('物理删除',f'删除id为{entity.Id}的数据')
                await self.session.delete(entity)
    async def TrueDelBatch(self,ids):
        if len(ids):
            self.AddLogger('物理批量删除',f'id为{ids}')
            if self.AutoCommit:
                fil = [self.modal.Id.in_(ids)]
                fil = self._add_extend_filter(fil)
                d = delete(self.modal).filter(*fil)
                r = await self.session.execute(d)
                await self.IfCommit()
            else:
                for id in ids:
                    entity = await self.Get(id)
                    if entity: await self.session.delete(entity)

    async def TrueDelNotCommit(self, id):
        entity = await self.Get(id)
        self.AddLogger('物理删除',f'删除id为{id}的数据')
        if entity: await self.session.delete(entity)
    async def paginate_query(self,filters, order_by, page_index, page_size)->tuple[TypeList[T],int]:
        # 计算总记录数
        total_count = await self.QueryCount(filters)
        # 分页查询
        items = await self.page_nocount_query(filters, order_by, page_index, page_size)
        return items, total_count
    async def page_nocount_query(self,filters, order_by, page_index, page_size)->TypeList[T]:
        fil = self._add_extend_filter(filters)
        query = select(self.modal).filter(*fil).order_by(order_by).offset((page_index - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        items = result.scalars().all()
        await self.IfCommit()
        return items
    async def paginate_fields_query(self,fields, filters, order_by, page_index, page_size)->tuple[TypeList[T],int]:
        # 计算总记录数
        total_count = await self.QueryCount(filters)
        # 分页查询
        items = await self.page_fields_nocount_query(fields, filters, order_by, page_index, page_size)
        return items, total_count
    async def page_fields_nocount_query(self,fields, filters, order_by, page_index, page_size)->TypeList[T]:
        fil = self._add_extend_filter(filters)
        sql = select(self.modal).filter(*fil)
        if fields:
            sql = sql.options(load_only(*fields))
        sql = sql.order_by(order_by).offset((page_index - 1) * page_size).limit(page_size)
        result = await self.session.execute(sql)
        items = result.scalars().all()
        await self.IfCommit()
        return items
    
    async def Get(self, id)->T:
        fil =[self.modal.Id == str(id)]
        fil = self._add_extend_filter(fil)
        result = await self.session.execute(select(self.modal).filter(*fil).limit(1))
        await self.IfCommit()
        return result.scalar()

    async def GetExist(self, id)->T:
        '''根据id获取数据'''
        exist =await self.Get(id)
        if exist is None:
            raise FriendlyException('不存在' + str(id))
        return exist
    async def GetExistByUser(self, id)->T:
        '''获取id和uid为当前用户数据'''
        exist = await self.session.execute(select(self.modal).filter(self.modal.Id == str(id),self.modal.UID == self.UserId).limit(1))
        result = exist.scalar()
        await self.IfCommit()
        if result is None:
            raise FriendlyException('不存在' + str(id))
        return result
    async def GetByUser(self):
        return await self.QueryFirst([self.modal.UID==self.UserId])
        
    async def UpdateFields(self,fil:TypeList[object],fields:Dict[str,object],refreshDefault=False):
        """更新部分字段

        Args:
            fil ([]): 查询条件
            fields (Dict[fieldname:value]): {"Status":1}
            refreshDefault (bool): 如果为True则自动更新LastModifiedUser，LastModifiedDate

        Raises:
            ex: _description_
        """
        try:
            if refreshDefault:
                fields['LastModifiedUser'] = self.UserId
                fields['LastModifiedDate'] = datetime.now()
            filters = self._add_extend_filter(fil)
            sql = update(self.modal).filter(*filters).values(**fields)
            self.AddLogger('更新',f'更新语句：{sql},值:{fields}')
            result = await self.session.execute(sql)
            await self.IfCommit()
            return result.rowcount
        except Exception as ex:
            await self.session.rollback()
            raise ex
    async def QueryWhere(self,fil:TypeList[object],fields:TypeList[object]=None,orderBy:Union[TypeList[object], object]=None)->TypeList[T]:
        filters = self._add_extend_filter(fil)
        sql = select(self.modal).filter(*filters)
        if fields:
            sql.options(load_only(*fields))
        if orderBy is not None:
            if not isinstance(orderBy, list):
                sql = sql.order_by(orderBy)
            else:
                sql = sql.order_by(*orderBy)
        result = await self.session.execute(sql)
        await self.IfCommit()
        return result.scalars().all()
    async def QueryOne(self,fil:TypeList[object],fields:TypeList[object]=None,orderBy:Union[TypeList[object], object]=None)->T:
        filters = self._add_extend_filter(fil)
        sql = select(self.modal).filter(*filters)
        if fields:
            sql.options(load_only(*fields))
        if orderBy is not None:
            if not isinstance(orderBy, list):
                sql = sql.order_by(orderBy)
            else:
                sql = sql.order_by(*orderBy)
        result = await self.session.execute(sql.limit(1))
        await self.IfCommit()
        return result.scalar()
    async def QueryCount(self,fil:TypeList[object])->int:
        filters = self._add_extend_filter(fil)
        sql = select(func.count()).select_from(self.modal).filter(*filters)
        result = await self.session.execute(sql)
        await self.IfCommit()
        return result.scalar()
    async def _addLoggerAsync(self,action,data:Union[TypeList[T],T]):
        try:
            syslogger = Mapper.getservice('BatchSysLogService')
            if not syslogger:
                raise FriendlyException('开启了业务日志，但是未注册服务BatchSysLogService')
            logData=''
            if isinstance(data,list):
                for item in data:
                    logData += json.dumps(item.to_basic_dict(), ensure_ascii=False)+','
            elif isinstance(data,BaseEntity):
                logData = json.dumps(data.to_basic_dict(), ensure_ascii=False)
            else:
                logData = data
            await syslogger.AddLogAsync(self.modal.__tablename__, action, logData)
        except Exception as ex:
            print(f'添加日志失败{ex}')
        
    def AddLogger(self, action, data:Union[TypeList[T],T,str]):
        if BaseConfig.BussinessLog:
            asyncio.create_task(self._addLoggerAsync(action,data))
    async def ExecSql(self,sql:str):
        '''执行自定义Sql'''
        result = await self.session.execute(text(sql))
        return result
