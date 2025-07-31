import pydantic
from pydantic import BaseModel
from typing import Any
import json
import mxupy as mu
from datetime import datetime, date

class IM(BaseModel):
    """ 一般函数执行后返回的结果类

    Args:
        BaseModel (pydantic.BaseModel): 用于前端调用后端时，对返回的结果类进行校验

    Raises:
        TypeError: 未知类型

    Returns:
        IM: 结果类
    """
    msg: str = pydantic.Field('', description="API message")
    data: Any = pydantic.Field(None, description="API data")
    code: int = pydantic.Field(200, description="API status code")
    type: str = pydantic.Field('', description="API status type")
    success: bool = pydantic.Field(True, description="API status")
    
    def __init__(self, success=True, msg='', data=None, code=200, type=''):
        """ 初始化结果

        Args:
            success (bool, optional): 成功否
            msg (str, optional): 消息
            data (any, optional): 数据
            code (int, optional): 编码，success时默认为200，反之默认为500
            type (str, optional): 用户自定义类型，比如：add|update
        """
        super().__init__()
        
        self.success = success
        self.msg = msg
        self.data = data
        self.type = type
        self.code = code if success and code == 200 else 500
        
    def __getstate__(self):
        return { 'type': self.type, 'msg': self.msg }
    
    def __str__(self):
        return self.to_string()
        
    @property
    def error(self):
        """ 失败否，与成功否相反

        Returns:
            bool: 失败否
        """
        return not self.success
    
    def set_error(self, msg=None, code=500, type=''):
        """ 设置为失败

        Args:
            msg (str, optional): 消息
            code (int, optional): 编码
            type (str, optional): 类型

        Returns:
            IM: 结果类
        """
        self.success = False
        self.msg = msg if msg else self.msg
        self.code = code
        self.type = type
        
        return self
        
    def datetime_handler(self, x):
        if isinstance(x, datetime) or isinstance(x, date):
            return x.isoformat()
        raise TypeError("Unknown type")

    def dumps(self):
        return json.dumps(mu.toSerializable(self), default=self.datetime_handler)
    
    def to_string(self) -> str:
        return f"{self.code}：{self.msg}-{self.data}" if self.success else f"{self.code}：{self.msg}"
    
    def from_dict(self, dict):
        self.success = dict.get('success')
        self.msg = dict.get('msg')
        self.data = dict.get('data')
        self.code = dict.get('code')
        self.type = dict.get('type')
        return self
    
    def to_dict(self):
        """将对象转换为字典，包含 error 属性"""
        return {
            'success': self.success,
            'msg': self.msg,
            'data': self.data,
            'type': self.type,
            'code': self.code,
            'error': self.error
        }
    