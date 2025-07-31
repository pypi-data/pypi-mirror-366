from playhouse.shortcuts import model_to_dict
from peewee import (
    Model, Field, ForeignKeyField,
    IntegerField, CharField, BooleanField, AutoField, DeferredForeignKey
)

# CharField 最大长度为 255 字符
# FixedCharField： 固定长度的字符串，最大长度为 255 字符
# TextField：最大长度为 65,535 字节（64 KB）


class MediumTextField(Field):
    """ 中等长度字符类型
        最大长度为 16,777,215 字节（16 MB）

    Args:
        Field (peewee.Field): 字段
    """
    field_type = 'MEDIUMTEXT'


class LongTextField(Field):
    """ 中等长度字符类型
        最大长度为 4,294,967,295 字节（4 GB）

    Args:
        Field (peewee.Field): 字段
    """
    field_type = 'LONGTEXT'


class EntityX(Model):
    """ 实体类，继承于 peewee.Model 类，所有实体的父类
    """
    class Meta:
        database = None

    def __init__(self, *args, db=None, **kwargs):
        # 可以将某个实体映射到不同的数据库
        if db:
            self._meta.database = db
        super().__init__(*args, **kwargs)

    def to_dict(self):
        # 将模型实例转换为字典
        return model_to_dict(self, recurse=False)

    @property
    def key_name(self):
        return self.__class__._meta.primary_key.name

    @property
    def table_name(self):
        return self.__class__._meta.table_name


class TreeEntityX(EntityX):
    """ 树形实体类，继承于实体类，所有树形实体的父类
    """

    def __init__(self, *args, db=None, **kwargs):
        super().__init__(*args, db=db, **kwargs)
        
    # @classmethod
    # def _get_id_field_name(cls):
    #     for name, field in cls._meta.fields.items():
    #         if isinstance(field, AutoField):
    #             return name
    #     raise AttributeError("子类必须定义 AutoField 主键")

    # 排序、路径、深度、有子元素否
    sort = IntegerField(default=0, index=True)
    path = CharField(max_length=200, index=True)
    depth = IntegerField(index=True, default=1)
    hasChildren = BooleanField(default=False, index=True)
    
    parent = DeferredForeignKey('self', column_name='parentId', null=True, backref='children', default=None)
    # lastChat = DeferredForeignKey('Chat', backref='sessions', column_name='lastChatId', on_delete='CASCADE', null=True)
    
    @property
    def idAndName(self):
        return '[' + str(getattr(self, self.key_name)) + ']' + getattr(self, 'name')

    # @classmethod
    # def __init_subclass__(cls, **kwargs):
    #     # 检查子类是否定义了 AutoField 主键
    #     id_field = next(
    #         (name for name, field in cls._meta.fields.items() 
    #          if isinstance(field, AutoField)),
    #         None
    #     )
    #     if not id_field:
    #         raise AttributeError("子类必须定义 AutoField 主键")

    #     # 动态添加 parent 字段
    #     cls.parent = ForeignKeyField(
    #         'self',
    #         column_name='parentId',
    #         backref='children',
    #         on_delete='CASCADE',
    #         null=True,
    #         default=None,
    #         field=id_field
    #     )
    #     super().__init_subclass__(**kwargs)

    class Meta:
        abstract = True