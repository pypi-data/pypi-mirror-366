import mxupy as mu
from functools import reduce

class ConditionOperator:
    """ 数据库操作符字典类
    """
    # 共计 16 类操作符
    equal = '='
    not_equal = '!='
    not_equal_alias = '<>'
    
    less = '<'
    less_equal = '<='
    greater = '>'
    greater_equal = '>='
    
    contains = 'contains'
    not_contains = 'not_contains'
    startswith = 'startswith'
    not_startswith = 'not_startswith'
    endswith = 'endswith'
    not_endswith = 'not_endswith'
    
    in_ = 'in'
    not_in = 'not_in'
    is_null = 'is_null'
    is_not_null = 'is_not_null'
    
    @staticmethod
    def fix_not_equal(operator):
        """ 将操作符从别名修正为正名，将 <> 替换成 !=

        Args:
            operator (str): 操作符
        """
        if not operator:
            return operator
        return operator.replace(ConditionOperator.not_equal_alias, ConditionOperator.not_equal)

class Condition:
    """ 数据库条件
    """
    def __init__(self, model_class, expr, field_name='', operator='=', value=None, type='and', left=0, right=0):
        """ 条件

        Args:
            model_class (Expression): peewee model 类，需要通过它来得到 sql 进行打印
            expr (Expression): peewee 条件表达式
            field_name (str): 字段名
            operator (str): 操作符
            value (any): 值
            type (str): 类型 and 或 or
            left (int): 左边括号数
            right (int): 右边括号数
        """
        
        self.model_class = model_class
        self.expr = expr
        
        self.field_name = field_name
        self.operator = operator
        self.value = value
        
        self.type = type
        self.left = left
        self.right = right

    def __str__(self):
        """ 转成字符串

        Returns:
            str: 条件信息
        """
        sql = f"{ 'SQL：' + str(self.model_class.select().where(self.expr).sql()) }"
        return sql

class ConditionHandler:
    """ 条件处理器
    """
    def __init__(self, model_class):
        """ 条件处理器

        Args:
            model_class (Model): 模型类，条件可据此生成 peewee 条件表达式
        """
        self.model_class = model_class
    
    def remove_excess_bracket(self, left, right):
        """ 中和掉左右多余的括号，
        一个条件要么只有左括号、要么只有右括号，不可能同时拥有左右括号

        Args:
            left (int): 左括号数量
            right (int): 右括号数量

        Returns:
            int: 中和掉括号后的左右括号数
        """
        if left >= right:
            left -= right
            right = 0
        else:
            right -= left
            left = 0
        
        return left, right
    
    def get_operation(self, mixed_values):
        """ 根据混合值得到操作符

        Args:
            mixed_values (str): 混合了操作符、左右括号、连接符
                
        Returns:
            str: 操作符
        """
        
        co = ConditionOperator
        
        # 条件中不传操作符，则认为操作是“=”
        if not mixed_values:
            return co.equal
        
        # 注意顺序不能乱，比如字符串包含 >=, 那么一定包含 >, 
        # 所以 greater_equal 在 greater 前面, 其他条件同理
        ops = [
            co.not_equal,
            co.less_equal,
            co.less,
            co.greater_equal,
            co.greater,
            
            co.not_contains,
            co.contains,
            co.not_startswith,
            co.startswith,
            co.not_endswith,
            co.endswith,
            
            co.is_not_null,
            co.is_null,
            co.not_in,
            co.in_,
        ]
        mvs = co.fix_not_equal(mixed_values.lower())
        for op in ops:
            if op in mvs:
                return op
        
        return co.equal
    
    def build_expression(self, field_name, operation, value=None):
        """ 构建 peewee 表达式

        Args:
            field_name (str): 字段名
            operation (str): 操作符
            value (any): 值
        Returns:
            peewee.Expression: 返回生成的表达式
        """
        field = getattr(self.model_class, field_name, None)
        if not field:
            raise AttributeError(f"Field '{field_name}' does not exist in the model.")
        
        co = ConditionOperator
        operation = co.fix_not_equal(operation.lower())
        operations = {
            co.equal: lambda field, value: field == value,
            co.not_equal: lambda field, value: field != value,
            co.less: lambda field, value: field < value,
            co.less_equal: lambda field, value: field <= value,
            co.greater: lambda field, value: field > value,
            co.greater_equal: lambda field, value: field >= value,
            
            co.in_: lambda field, value: field.in_(value),
            co.not_in: lambda field, value: ~field.in_(value),
            co.is_null: lambda field, value: field.is_null(),
            co.is_not_null: lambda field, value: ~field.is_null(),
            
            co.contains: lambda field, value: field.contains(value),
            co.not_contains: lambda field, value: ~field.contains(value),
            co.startswith: lambda field, value: field.startswith(value),
            co.not_startswith: lambda field, value: ~field.startswith(value),
            co.endswith: lambda field, value: field.endswith(value),
            co.not_endswith: lambda field, value: ~field.endswith(value),
        }
        
        expr = None
        if field and operation in operations:
            expr = operations[operation](field, value)
            
        return expr
    
    def prepare_condition(self, query_conditions):
        """ 预处理条件集

        Args:
            query_conditions (list[dict] | dict): 条件集或单个条件，示例值：
                [
                    {'name':('&(contains','jerry1')},
                    {'name':('contains)|','jerry1')},
                    {'name':'jerry1'}
                ]
                键为字段名
                如果值不是一个元祖，只有一个值，那表示这个值就是数据库里存储的值
                值包含两部分，第一部分包含: 操作符、左右括号、连接符。第二部分为数据库里存储的值
        Returns:
            list[Condition]: 返回处理完的值
        """
        
        cs = []
        
        # 单个条件转为条件集，方便统一处理
        if isinstance(query_conditions, dict):
            query_conditions = [query_conditions]
        
        # 数组也是对象的一种，故要先判断是不是数组
        if not isinstance(query_conditions, list):
            if isinstance(query_conditions, object):
                query_conditions = [query_conditions]
        
        for qc in query_conditions:
            if isinstance(qc, object):
                qc = mu.obj_to_dict(qc)
            
            f, op, v, t, l, r = '', '=', None, 'and', 0, 0
            for key, value in qc.items():
                f = key
                
                # 说明只传了值
                if not isinstance(value, tuple) and  not isinstance(value, list):
                    
                    # 如果值为 is_null 或 is_not_null，则认为其是操作符
                    op = value.lower() if value and isinstance(value, str) and value.lower() in [ConditionOperator.is_null, ConditionOperator.is_not_null] else '='
                    v = value
                    
                else:
                    # 包含操作符、括号、连接符
                    oth = str(value[0])
                    
                    op = self.get_operation(oth)
                    v = value[1] if len(value) > 1 else None
                    t = 'or' if '|' in oth else 'and'
                    
                    l, r = self.remove_excess_bracket(oth.count('('), oth.count(')'))
                    
            expr = self.build_expression(f, op, v)
            cs.append(Condition(self.model_class, expr, f, op, v, t, l, r))
        
        return cs

    def find_condition_index(self, conditions):
        """ 将所有条件合并成一个条件, 先找到最右边的带左括号的条件进行合并, 如果没有则先合并最右侧的 and 条件
            找到最需要合并条件的序号
        Args:
            conditons (list[obj]): 条件集
        Returns:
            int: 返回符合项序号
        """
        # 只有两个条件，直接合并即可
        if len(conditions) <= 2:
            return 0
        
        # 找到最右边的包含左括号的条件（最后一项除外，因为左括号条件至少要有两项，和后面一个条件进行合并）
        for i in range(len(conditions) - 2, -1, -1):
            if conditions[i].left > 0:
                return i
        
        # 从左到右 或 从右到左 都是一样的效果，从左到右符合习惯
        # 找到最左边的 and 条件，（第一项除外，因为 and 是与前面一个条件进行合并）
        for i, c in enumerate(conditions[1:], 1):
            if c.type == 'and':
                return i - 1
        
        # 如果都没有，说明都为or条件，直接全部按顺序合并即可
        return -1
    
    def merge_condition(self, condition1, condition2):
        """ 将两个条件合并到一起

        Args:
            condition1 (obj): 条件1
            condition2 (obj): 条件2
        Returns:
            Condition: 返回条件
        """
        # 按第 2 项类别合并
        expr = condition1.expr & condition2.expr if condition2.type == 'and' else condition1.expr | condition2.expr
        # 保留第一项的类型和左括号，保留第二项的右括号
        c = Condition(self.model_class, expr, type=condition1.type, left=condition1.left, right=condition2.right)
        return c
    
    def handle_condition(self, conditions):
        """ 将所有条件合并成一个条件, 先找到最右边的带左括号的条件进行合并, 如果没有则先合并最右侧的 and 条件

        Args:
            conditons (list[obj]): 条件集
        Returns:
            list[Condition]: 返回处理完的值
        """
        
        # 一个条件直接返回
        if len(conditions) == 1:
            return conditions[0]
        
        # 两个条件直接合并即可，最后合并成一个条件后，类型和括号不影响查询结果
        if len(conditions) == 2:
            return self.merge_condition(conditions[0], conditions[1])
        
        # 找到要优先计算的那一项，优先级别与sql条件保持一致
        idx = self.find_condition_index(conditions)
        if idx == -1:
            # 合并所有的“或”条件
            exprs = [c.expr for c in conditions]
            return Condition(self.model_class, reduce(lambda x, y: x | y, exprs))
        
        # 按序号合并
        c = self.merge_condition(conditions[idx], conditions[idx + 1])
        
        # 移除老条件，插入新条件
        conditions.pop(idx)
        conditions.pop(idx)
        conditions.insert(idx, c)
        
        # 递归，继续处理剩余的条件
        return self.handle_condition(conditions)
    
    def to_sql(self, query_conditions):
        """ 将条件的sql输出到控制台，并返回合成后的条件

        Args:
            query_conditions (list[dict] | dict): 条件集或单个条件
        Returns:
            Condition: 返回处理完的值
        """
        # 打印条件表达式
        cs = self.prepare_condition(query_conditions)
        exp = ''
        for i, c in enumerate(cs):
            
            t = 'where' if i == 0 else c.type
            
            v = ''
            if c.operator not in [ConditionOperator.is_null, ConditionOperator.is_not_null]:
                v = "''" if str(c.value) == '' else str(c.value)
                
            exp += f"{t} {c.left * '('} {c.field_name} {c.operator} {v} {c.right * ')'}"
        # print(exp)
        
        # 打印 SQL
        sql = self.handle_condition(cs)
        # print(sql)
        
        return exp, sql
