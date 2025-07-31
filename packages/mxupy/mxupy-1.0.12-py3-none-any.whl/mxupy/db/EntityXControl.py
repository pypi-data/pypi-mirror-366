import traceback
import mxupy as mu
from peewee import *
from fastapi import Request
from playhouse.shortcuts import model_to_dict
from mxupy import IM, to_int, get_attr

class EntityXControl:
    """ 实体控制器，包含对表的增删改查等功能
    """
    
    def __init__(self):
        """
            实体类、库、表名、数据库执行器、主键名
        """
        
        _meta = self.Meta.model_class._meta
        
        self.model_class = self.Meta.model_class
        
        self.db = _meta.database
        self.table_name = _meta.table_name
        self.model_name = _meta.name
        
        self.key_name = self.get_primary_key_name(self.model_class)
        self.fields = _meta.fields
        self.table_fields = self.get_table_fields(_meta.fields)
        
        self.dbe = mu.DBExecuter(self.db)
    
    @classmethod
    def exists_inst(cls):
        """ 单例模式，通过此函数返回对象的实例

        Returns:
            mu.EntityXControl: 控制器实例
        """
        return hasattr(cls, '_inst')
    
    @classmethod
    def inst(cls):

        """ 单例模式，通过此函数返回对象的实例

        Returns:
            mu.EntityXControl: 控制器实例
        """
        if not hasattr(cls, '_inst'):
            cls._inst = cls()
            
        return cls._inst
    
    def get_table_fields(self, fields):
        """ 获取表字段，比如外键字段user，得到之后为为表中的字段userId

        Returns:
            dict: 字典 {'字段名':'字段类型'}
        """
        tfs = {}
        
        for fn, ft in fields.items():
            if isinstance(ft, ForeignKeyField):
                tfs[ft.column_name] = IntegerField
            else:
                tfs[fn] = ft
    
        return tfs
    
    def get_field_by_name(self, field_name):
        """ 根据字段名获取字段信息

        Args:
            field_name (str): 字段名

        Raises:
            AttributeError: 选中的某个字段不在当前实体中
        
        Returns:
            field: 字段信息
        """
        field = getattr(self.model_class, field_name, None)
        if field is None:
            raise AttributeError(f"字段 '{field_name}' 不在模型 '{self.model_name}' 中")
        return field
    
    def clone(self, model, contains_key=False, contains_foreign_key=False):
        """ 克隆

        Args:
            model (Entity): 实体
            contains_key (bool): 包含主键否
            contains_foreign_key (bool): 包含外键否

        Returns:
            Entity: 克隆后的实体
        """
        fs = self.fields if contains_foreign_key else self.table_fields
        
        m = self.model_class()
        for f in fs:
            if not contains_key and self.key_name == f:
                continue
            setattr(m, f, get_attr(model, f))
        return m
    
    def obj_to_model(self, model):
        """ 将对象转 Model

        Returns:
            Model: Model 实例
        """
        if (isinstance(model, Model)):
            return model
        
        if (isinstance(model, dict)):
            return model
        
        m = self.model_class()
        for attr in dir(model):
            # 私有属性不需要
            if attr.startswith('__'):
                continue
            
            value = getattr(model, attr)
            if hasattr(m, attr):
                setattr(m, attr, value)
                
        return m
    
    def to_where_sql(self, where):
        """ 得到条件，并打印表达式 和 sql

        Args:
            where (list[dict] | dict): 条件集或单个条件
        Returns:
            str: 表达式 和 sql
        """
        ch = mu.ConditionHandler(self.model_class)
        exp, sql = ch.to_sql(where)
        return exp, sql

    def run2(self, operation):
        """ 执行数据库操作，分为3步：
            1、开始一个事务
            2、执行数据库操作
            3、提交事务

        Args:
            operation (func): 操作

        Returns:
            im: 执行结果
        """
        im = IM()
        try:
            # 开始一个事务、执行数据库操作、提交事务
            self.db.begin()
            im = operation()
            self.db.commit()
            
        except IntegrityError as e:
            im.code = 500
            im.success = False
            im.msg = f"dbBigOAINET IntegrityError: {e}"
            im.type = 'IntegrityError'
            print(im.msg)
            traceback.print_exc()
            self.db.rollback()
            
        except DatabaseError as e:
            im.code = 500
            im.success = False
            im.msg = f"dbBigOAINET DatabaseError: {e}"
            im.type = 'DatabaseError'
            print(im.msg)
            traceback.print_exc()
            self.db.rollback()
            
        except OperationalError as e:
            im.code = 500
            im.success = False
            im.msg = f"dbBigOAINET OperationalError: {e}"
            im.type = 'OperationalError'
            print(im.msg)
            traceback.print_exc()
            self.db.rollback()
            
        except DoesNotExist as e:
            im.code = 500
            im.success = False
            im.msg = f"dbBigOAINET DoesNotExist: {e}"
            im.type = 'DoesNotExist'
            print(im.msg)
            traceback.print_exc()
            self.db.rollback()
            
        except Exception as e:
            im.code = 500
            im.success = False
            im.msg = f"dbBigOAINET An unexpected error occurred: {e}"
            im.type = 'Exception'
            print(im.msg)
            traceback.print_exc()
            self.db.rollback()

        return im
    
    def run(self, operation):
        """执行数据库操作，自动适配不同数据库的事务处理
        
        Args:
            operation (func): 需要执行的操作函数
            
        Returns:
            IM: 执行结果对象
        """
        im = IM()  # 假设 IM 是你的结果类
        
        # 检查是否已经在事务中
        if self.db.in_transaction():
            if isinstance(self.db, SqliteDatabase):
                # SQLite 下直接执行操作(不嵌套事务)
                im = operation()
                return im
            else:
                # MySQL 下可以安全嵌套
                with self.db.atomic():
                    im = operation()
                return im
        
        try:
            # 开始事务
            if isinstance(self.db, SqliteDatabase):
                # SQLite 使用更安全的上下文管理器
                with self.db.atomic():
                    im = operation()
            else:
                # MySQL 使用标准事务
                self.db.begin()
                im = operation()
                self.db.commit()
                
        except Exception as e:
            # 回滚事务
            if not isinstance(self.db, SqliteDatabase):
                # SQLite 的上下文管理器会自动处理回滚
                self.db.rollback()
            # 记录错误或重新抛出
            # raise
            # 或者 return 一个错误状态的 IM 对象
            return im.set_error(str(e))
        
        return im
    def get_primary_key_name(self, model_class):
        """ 
            返回给定模型类的主键字段名称。
        Args:
            model_class (class): 继承自 peewee.Model 的类。

        Returns:
            str: 主键字段的名称
        """
        # 获取模型类的元数据
        meta = model_class._meta
        # 检查主键字段
        primary_key_field = meta.primary_key
        # 返回主键字段的名称
        return primary_key_field.name
       
       
        
    def build_select(self, select):
        """ 选中哪些字段

        Args:
            select (list[str]|str): 选中的字段集

        Raises:
            AttributeError: 选中的某个字段不在当前实体中

        Returns:
            list[field]: 字段属性集
        """
        fields = []
        
        if not select:
            return fields
        #     return list(self.fields.values())
        
        if not isinstance(select, list):
            select = [select]
        
        # 保证主键有值
        if not self.key_name in select:
            select.append(self.key_name)
            
        for f in select:
            fields.append(self.get_field_by_name(f))
            
        return fields
        
    def build_where(self, where):
        """ 构建条件表达式，用于过滤查询结果。
            如果有多个条件，最终会通过'与'或者'或'计算合并成一个表达式

        Args:
            where (list[dict]|dict): 包含查询条件的字典集

        Returns:
            expression: 条件表达式
        """
        ch = mu.ConditionHandler(self.model_class)
        cs = ch.prepare_condition(where)
        c = ch.handle_condition(cs)
        
        return c.expr

    def build_orderby(self, order_by):
        """ 构建排序表达式，用于对查询结果进行排序

        Args:
            order_by (list[dict]|dict): 包含排序的字典集

        Raises:
            AttributeError: 当前实体不包含此字段

        Returns:
            orderbys: 排序集
        """
        
        if not isinstance(order_by, list):
            order_by = [order_by]
        
        os = []
        for ob in order_by:
            if isinstance(ob, object):
                ob = mu.obj_to_dict(ob)
            for key, value in ob.items():
                field = self.get_field_by_name(key)
                os.append(getattr(field, value)())

        return os

    def build_groupby(self, group_by):
        """ 构建分组表达式，用于对查询结果进行分组

        Args:
            group_by (list[str]|str): 包含分组的字典集

        Raises:
            AttributeError: 当前实体不包含此字段

        Returns:
            groupbys: 分组集
        """
        
        if not isinstance(group_by, list):
            group_by = [group_by]
        
        gs = []
        for gb in group_by:
            gs.append(self.get_field_by_name(gb))

        return gs

    def build_having(self, having):
        """ 构建筛选表达式，用于对查询结果进行筛选

        Args:
            having (list[str]|str): 包含筛选的字典集

        Raises:
            AttributeError: 当前实体不包含此字段

        Returns:
            havings: 分组集
        """
        having1 = []
        for key, value in having.items():
            field = self.get_field_by_name(key)
            having1.append(field == value)
        return having1

    def build_query(self, select=None, where=None, order_by=None, group_by=None, having=None, limit=10, offset=None):
        """ 

        Args:
            select (list[str]): 选中的字段集
            where (list[dict]|dict): 查询条件字典集
            order_by (list[dict]|dict, optional): 查询排序字典集
            group_by (list[str]|str, optional): 查询分组集
            having (list[dict]|dict, optional): 查询筛选字典集
            limit (int, optional): 每页多少条
            offset (int, optional): 从第几条开始
            
        Returns:
            ModelSelect: _description_
        """
        select1 = self.build_select(select)
        query = self.model_class.select(*select1)
        query.builds = {}
        query.builds['select'] = select1

        if where:
            expr = self.build_where(where)
            query.builds['where'] = expr
            query = query.where(expr)

        if order_by:
            order_by1 = self.build_orderby(order_by)
            query.builds['order_by'] = order_by1
            query = query.order_by(*order_by1)

        if group_by:
            group_by1 = self.build_groupby(group_by)
            query.builds['group_by'] = group_by1
            query = query.group_by(*group_by1)

        if having:
            expr = self.build_where(having)
            query.builds['having'] = expr
            query = query.having(expr)
            
            # having1 = self.build_having(having)
            # query.builds['having'] = having1
            # query = query.having(*having1)

        if limit:
            query = query.limit(limit)
            query.builds['limit'] = limit

        if offset:
            query = query.offset(offset)
            query.builds['offset'] = offset

        return query
    
    def handle_extra_attrs(self, extra_attrs):
        """ 处理扩展属性
            普通的扩展属性由用户传递，外键字段由系统自动处理

        Args:
            extra_attrs (list[str]|str): to_dict 时，处理扩展字段

        Raises:
            AttributeError: 当前实体不包含此字段

        Returns:
            havings: 分组集
        """
        # 处理 extra_attrs
        extra_attrs = extra_attrs if extra_attrs else []
        extra_attrs2 = extra_attrs.split(',') if isinstance(extra_attrs, str) else extra_attrs
        
        # to_dict 时，处理外键字段
        for field_name in self.fields:
            field = self.fields[field_name]
            if isinstance(field, ForeignKeyField):
                if field.column_name and field.column_name not in extra_attrs2:
                    extra_attrs2.append(field.column_name)
                
        return extra_attrs2
    
    def exists(self, where):
        """
            检查是否存在满足条件的记录。
        Args:
            where (list[dict]|dict): 包含查询条件的字典集
            
        Returns:
            im:  如果存在至少一条记录，则返回 True，否则返回 False。
        """
        im = IM()
        query = self.model_class.select()
        if where:
            expr = self.build_where(where)
            query = query.where(expr)

        result = query.exists()
        im.data = result
        
        if not result:
            im.msg = '[' + self.model_name + ']不存在。'
        
        return im

    def exists_by_id(self, id):
        """ 按主键id检索是否存在

        Args:
            id (int): 主键id

        Returns:
            im[bool]: 存在否
        """
        im = self.exists(where={self.key_name: id})
        return im
    
    def get_count(self, where):
        """ 获取满足条件的记录数量。

        Args:
            where (list[dict]|dict): 包含查询条件的字典集
            
        Returns:
            im:  返回符合条件的数量
        """
        im = IM()
            
        query = self.model_class.select()
        if where:
            expr = self.build_where(where)
            query = query.where(expr)

        result = query.count()
        im.data = result

        return im
    
    def get_one(self, select=None, where=None, order_by=None, group_by=None, having=None, offset=None, 
                to_dict=False, recurse=False, backrefs=False, extra_attrs=None, max_depth=1):
        """ 获取单条记录

        Args:
            select (list[str]): 选中的字段集
            where (list[dict]|dict): 查询条件字典集
            order_by (list[dict]|dict, optional): 查询排序字典集
            group_by (list[str]|str, optional): 查询分组集
            having (list[dict]|dict, optional): 查询筛选字典集
            offset (int, optional): 从第几条开始
            to_dict (bool, optional): 是否将查询结果转为字典
            recurse (bool, optional): 是否递归地处理外键字段
            backrefs (bool, optional):是否递归地处理反向引用的字段
            extra_attrs (list[str]|str, optional):扩展项集，获取扩展属性
            max_depth (int, optional):是否递归的最大层级
            
        Returns:
            im: 单条记录
        """
        im = IM()
        
        query = self.build_query(select, where, order_by, group_by, having, 1, offset)

        res = query.first()
        if res is None:
            im.msg = '[' + self.model_name + ']不存在。'
            im.data = None
            return im

        if to_dict:
            
            extra_attrs2 = self.handle_extra_attrs(extra_attrs)
            
            if select:
                im.data = model_to_dict(
                    res, recurse=recurse, backrefs=backrefs, max_depth=max_depth, extra_attrs=extra_attrs2, only=query.builds['select'])
            else:
                im.data = model_to_dict(
                    res, recurse=recurse, backrefs=backrefs, max_depth=max_depth, extra_attrs=extra_attrs2)
        else:
            im.data = res

        return im

    def get_one_by_id(self, id, select=None, to_dict=False, recurse=False, backrefs=False, extra_attrs=None,  max_depth=1):
        """ 按主键id获取一条记录

        Args:
            id (int): 主键id
            select (list[str]): 选中的字段集
            to_dict (bool, optional): 是否将查询结果转为字典
            recurse (bool, optional): 是否递归地处理外键字段
            backrefs (bool, optional):是否递归地处理反向引用的字段
            extra_attrs (list[str]|str, optional):扩展项集，获取扩展属性
            max_depth (int, optional):是否递归的最大层级

        Returns:
            im: 单条记录
        """
        im = self.get_one(select=select, where={self.key_name: id}, 

                    to_dict=to_dict, recurse=recurse, backrefs=backrefs, extra_attrs=extra_attrs, max_depth=max_depth)
        return im

    def get_list(self, select=None, where=None, order_by=None, group_by=None, having=None, limit=None, offset=None, 
                 to_dict=False, recurse=False, backrefs=False, extra_attrs=None, max_depth=1):
        """ 获取记录集

        Args:
            select (list[str]): 选中的字段集
            where (list[dict]|dict): 查询条件字典集
            order_by (list[dict]|dict, optional): 查询排序字典集
            group_by (list[str]|str, optional): 查询分组集
            having (list[dict]|dict, optional): 查询筛选字典集
            limit (int, optional): 每页多少条
            offset (int, optional): 从第几条开始
            to_dict (bool, optional): 是否将查询结果转为字典
            recurse (bool, optional): 是否递归地处理外键字段
            backrefs (bool, optional):是否递归地处理反向引用的字段
            extra_attrs (list[str]|str, optional):扩展项集，获取扩展属性
            max_depth (int, optional):是否递归的最大层级
            
        Returns:
            im: 记录集
        """
        im = IM()
                    
        query = self.build_query(select, where, order_by, group_by, having, limit, offset)

        if to_dict:
            # 处理 extra_attrs
            extra_attrs2 = self.handle_extra_attrs(extra_attrs)
            
            if select:
                im.data = [model_to_dict(d, recurse=recurse, backrefs=backrefs, extra_attrs=extra_attrs2, 
                                max_depth=max_depth, only=query.builds['select']) for d in query]
            else:
                im.data = [model_to_dict(d, recurse=recurse, backrefs=backrefs, extra_attrs=extra_attrs2, 
                                max_depth=max_depth) for d in query]
        else:
            im.data = list(query)

        return im



    def add_or_update(self, model, fields=None, to_dict=False):
        """ 添加或删除一条记录
            当主键id有值并大于0，执行添加操作，否则执行修改操作

        Args:
            model (model|dict|obj): 模型
            fields (list[str], optional): 修改哪些字段
            to_dict (bool, optional): 转为字典否
            
        Returns:
            im: 单条记录
        """
        im = IM()
        
        # 将 model 转 dict
        model = self.obj_to_model(model)
        im = self.dbe.to_dict(model)
        if im.error:
            return im
        model2 = im.data
        
        # 执行添加或修改
        id = to_int(get_attr(model2, self.key_name, -1), -1)
        im = self.add(model2, False, to_dict) if id < 0 else self.update_by_id(id, model2, fields, to_dict)
        if im.error:
            return im
        
        return im

    def add(self, model, keep_id=False, to_dict=False):
        """ 添加一条记录

        Args:
            model (model|dict): 模型
            keep_id (bool, optional): 是否保留主键id，一般导入数据的时候会需要强制保留
            to_dict (bool, optional): 转为字典否

        Returns:
            im: 单条记录
        """
        
        # 将 model 转 dict
        model2 = self.obj_to_model(model)
        im = self.dbe.to_dict(model2)
        if im.error:
            return im
        model3 = im.data
        
        # 处理id
        id = to_int(get_attr(model3, self.key_name, -1), -1)
        if self.key_name in model3 and (not keep_id or id < 0):
            del model3[self.key_name]
        
        try:
            # 执行添加
            data = self.model_class.create(**model3)
        except Exception as e:
            traceback.print_exc()
            self.db.rollback()
            msg = f"dbbigOAINET UnexpectedError: {e}"
            print(msg)
            return IM(False, msg, None, 500, 'UnexpectedError')
        
        return IM(True, f"添加{self.model_name}成功！", model_to_dict(data, False) if to_dict else data)
    
    def update(self, where, model, fields=None, to_dict=False):
        """ 按条件更新多条记录

        Args:
            where (list[dict]|dict): 包含查询条件的字典集
            model (model|dict): 模型
            fields (list[str]|str): 字段集
            
        Raises:
            AttributeError: 当前实体不包含此字段
            
        Returns:
            im: 多条记录
        """
        im = IM()
        
        # 记录存在否
        im = self.exists(where)
        if not im.data:
            return im.set_error(f'{self.model_name}不存在符合条件的记录！')
        
        # model 转 dict
        model = self.obj_to_model(model)
        im = self.dbe.to_dict(model)
        if im.error:
            return im
        model2 = im.data

        # 处理字段
        if fields:
            model3 = {}
            fields2 = fields if isinstance(fields, list) else [fields]
            for f in fields2:
                model3[self.get_field_by_name(f)] = model2.get(f)
            model2 = model3

        # 执行修改
        cnt = self.model_class.update(model2).where(self.build_where(where)).execute()
        return IM(True, f"更新{self.model_name}成功！", model_to_dict(cnt, False) if to_dict else cnt)

    def update_by_id(self, id, model, fields=None, to_dict=False):
        """
            按 id 更新一条记录
        Args:
            id (int): 主键id
            model (model|dict): 新值
            fields (list[str]): 字段集
            to_dict: 结果转为字典
            
        Returns:
            im:  一条记录
        """
        return self.update({self.key_name: id}, model, fields, to_dict)

    def delete(self, where, recursive=True):
        """
            检查是否存在满足条件的记录。
        Args:
            where (list[dict]|dict): 包含查询条件的字典集
            recursive (bool): 是否同时删除被引用项
            
        Returns:
            im:  结果
        """
        im = IM()

        query = self.model_class.select()
        expr = self.build_where(where)
        data = query.where(expr).first()
        if data is None:
            im.success = False
            im.msg = f'{self.model_name}不存在符合条件的记录！'
            return im

        try:
            # 执行删除，当recursive为true的时候，会同时删除被引用项，此时有可能会报错
            # 比如删除权限时，此数据对应的权限分类下还有数据，此时就会报错
            data.delete_instance(recursive=recursive)
        except IntegrityError as e:
            traceback.print_exc()
            self.db.rollback()
            msg = f"dbbigOAINET IntegrityError: {e}"
            print(msg)
            return IM(False, msg, None, 500, 'IntegrityError')
        except InterfaceError as e:
            traceback.print_exc()
            self.db.rollback()
            msg = f"dbbigOAINET InterfaceError: {e}"
            print(msg)
            return IM(False, msg, None, 500, 'InterfaceError')
        except Exception as e:
            traceback.print_exc()
            self.db.rollback()
            msg = f"dbbigOAINET UnexpectedError: {e}"
            print(msg)
            return IM(False, msg, None, 500, 'UnexpectedError')
                    
        im.msg = f"删除{self.model_name}成功！"

        return im

    def delete_by_id(self, id, recursive=True):
        """
            按 id 删除记录
        Args:
            id (int): 主键id
            recursive (bool): 是否同时删除被引用项
            
        Returns:
            im:  结果
        """
        return self.delete({self.key_name: id}, recursive)
    
    
    
    def create_table(self, safe=True):
        """
            创建表
        Args:
            safe (bool): 
                当 safe 参数设置为 True 时，如果要创建的表已经存在于数据库中，Peewee 不会抛出错误，而是会忽略创建表的操作，
                继续执行后续代码。这可以避免因重复创建表而引发的错误，使得代码更加健壮。
                当 safe 参数设置为 False 时，如果尝试创建的表已经存在于数据库中，
                Peewee 会抛出相应的数据库错误（例如在 MySQL 中会抛出 OperationalError），因为数据库系统不允许重复创建同名的表。
            
        Returns:
            im:  结果
        """
        try:
            self.db.create_tables([self.model_class], safe=safe)
        except Exception as e:
            traceback.print_exc()
            self.db.rollback()
            msg = f"dbbigOAINET UnexpectedError: {e}"
            print(msg)
            return IM(False, msg, None, 500, 'UnexpectedError')
        
        return IM(True, f"创建{self.table_name}成功！")
    
    def drop_table(self, safe=True):
        """
            移除表
        Args:
            safe (bool): 
                当 safe 参数设置为 True 时，如果要删除的表在数据库中并不存在，Peewee 不会抛出错误，而是会忽略删除表的操作，继续执行后续代码。
                这样可以避免因尝试删除不存在的表而引发错误，增强代码的健壮性。
                当 safe 参数设置为 False 时，如果尝试删除的表在数据库中不存在，Peewee 会抛出相应的数据库错误。
                不同数据库系统抛出的错误类型可能有所不同，例如在 MySQL 中会抛出 OperationalError。
        Returns:
            im:  结果
        """
        
        try:
            self.model_class.drop_table(safe=safe)
        except Exception as e:
            traceback.print_exc()
            self.db.rollback()
            msg = f"dbbigOAINET UnexpectedError: {e}"
            print(msg)
            return IM(False, msg, None, 500, 'UnexpectedError')
        
        return IM(True, f"移除{self.table_name}成功！")
    
    def truncate_table(self):
        """
            清空数据，主键重新开始自增长
        Returns:
            im:  结果
        """
        try:
            # 删除表中所有数据
            self.model_class.delete().execute()
            # 重置自增主键
            self.db.execute_sql(f'ALTER TABLE `{self.table_name}` AUTO_INCREMENT = 1;')
        except Exception as e:
            traceback.print_exc()
            self.db.rollback()
            msg = f"dbbigOAINET UnexpectedError: {e}"
            print(msg)
            return IM(False, msg, None, 500, 'UnexpectedError')
        
        return IM(True, f"清除{self.table_name}数据成功！")
    
    
