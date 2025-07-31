import inspect
import importlib

from functools import lru_cache

# 提供一个所有类的可实例化的基类
class Obj(object):
    pass

def is_null(obj):
    """ 
        判断对象是否为空

    Args:
        obj (any): 需判断的对象

    Returns:
        bool: 为空否
    """
    import array
    import collections
    
    if obj is None:
        return True

    if isinstance(obj, str):
        return not obj.strip()

    if isinstance(obj, list) or isinstance(obj, tuple) or isinstance(obj, set):
        return len(obj) == 0

    if isinstance(obj, collections.abc.Iterable) and not isinstance(obj, (str, bytes, bytearray)):
        return not list(obj)

    if isinstance(obj, array.array):
        return len(obj) == 0

    if isinstance(obj, collections.abc.Collection):
        return not bool(obj)

    if hasattr(obj, '__iter__') and hasattr(obj, '__len__'):
        return len(obj) == 0

    # 对于自定义对象，假设它们有一个 isempty 属性或方法
    if hasattr(obj, 'isempty'):  
        return obj.isempty

    return False

def get_attr(obj, name, default=None):
    """ 
        支持多层获取属性

    Args:
        obj (cls|obj|dict): 类、对象、字典
        name (str): 名称 多层用“.”隔开，如：Meta.instance_name
        default (any): 如果属性不存在，则返回此默认值

    Returns:
        any: 属性值
    """
    ns = name.split('.')
    attr = obj.get(ns[0], default) if isinstance(obj, dict) else getattr(obj, ns[0], default)
    if len(ns) == 1:
        return attr
    
    # 中途没有直接返回
    if not attr:
        return default
    
    return get_attr(attr, ''.join(ns[1:]), default)

def set_attr(obj, name, value):
    """
    支持多层设置属性或键值

    Args:
        obj (cls|obj|dict): 类、对象、字典
        name (str): 名称 多层用“.”隔开，如：Meta.instance_name
        value (any): 要设置的值
    """
    ns = name.split('.')
    if len(ns) == 1:
        # 如果只有一层，直接设置
        if isinstance(obj, dict):
            obj[ns[0]] = value
        else:
            setattr(obj, ns[0], value)
    else:
        # 如果有多层，先递归获取到倒数第二层
        sub_name = '.'.join(ns[:-1])
        sub_obj = get_attr(obj, sub_name)
        if sub_obj is None:
            # 如果中间层不存在，根据类型动态创建
            if isinstance(obj, dict):
                for key in ns[:-1]:
                    if key not in obj:
                        obj[key] = {}
                    obj = obj[key]
            else:
                for key in ns[:-1]:
                    if not hasattr(obj, key):
                        setattr(obj, key, type(obj)())
                    obj = getattr(obj, key)
        # 最后一层直接设置
        if isinstance(obj, dict):
            obj[ns[-1]] = value
        else:
            setattr(obj, ns[-1], value)
    
def is_static_method(clazz, method_name = None):
    """ 通过类与函数名，判断一个函数是否为静态函数

    Args:
        clazz (class): 类
        method_name (string): 函数名
    
    Returns:
        bool: True 为静态函数，False 为成员函数
    """
    # 获取类中的方法，注意 clazz 一定要实例化后获取属性
    static_func = getattr(clazz, method_name)
    return not inspect.signature(static_func).parameters.get('self')

    # method = getattr(clazz(), method_name, None)
    # if method is None:
    #     raise AttributeError(f"'{clazz.__name__}' object has no attribute '{method_name}'")

    # return not inspect.ismethod(method)
    # 这种判断也行
    # return not hasattr(method, '__self__')

@lru_cache(maxsize=1000)
def get_method(module_path):
    """
    根据模块路径，获取函数信息
    通过 lru_cache 将结果缓存，避免重复导入
    参数为缓存key，返回值为缓存value
    缓存大小为 1000，超过 1000 个不同的模块路径，会自动删除最旧的缓存项。

    Args:
        module_path (str): 模块路径，末尾包含函数名称

    Returns:
        method: 函数或类的实例
    """
    # 将结构拆分为各个部分
    components = module_path.split('.')
    
    # 示例：'db.c.rbac.RightCategoryControl.get_one'
    # 包路径：db.c.rbac.RightCategoryControl
    package_path = '.'.join(components[:-1])  
    # 类名：RightCategoryControl
    class_name = components[-2]
    # 方法名：get_one
    method_name = components[-1]
    
    try:
        # 共 3 种情况
        # [1] 模块函数 ObjectUtil 中的 is_null 函数
        # [2] 静态函数 
        # [3] 成员函数 aliyun.ASR 中的 call 函数，以及实体控制器 RightCategoryControl 中的 get_one 函数
        
        # 可能是模块、类、类的实例
        var = None
        
        package = importlib.import_module(package_path)
        if not hasattr(package, class_name):
            # [1] 模块中的函数，没有类，直接从模块获取
            var = package
        else:
            clazz = getattr(package, class_name)
            if is_static_method(clazz, method_name):
                # [2] 静态函数，从类获取
                var = clazz
            else:
                # [3] 成员函数，从类的实例获取
                var = getattr(clazz, 'inst')()
            
        method = getattr(var, method_name)
        return method
    
    except (ImportError, AttributeError) as e:
        print(f"Failed to import {module_path}: {e}")
        return None
    
# 添加缓存清理方法
def clear_method_cache():
    """
    清理 get_method 函数的缓存
    """
    get_method.cache_clear()
    
def has_method(module_path):
    m = get_method(module_path)
    return True if m else False

def dict_to_obj(dic):
    """ 字典转对象

    Args:
        dict (dict): 字典
    
    Returns:
        obj: 对象
    """
    if isinstance(dic, dict):
        obj = Obj()
        { setattr(obj, k, dict_to_obj(v)) for k, v in dic.items() }
        return obj
    else:
        return dic
    
def param_to_obj(params):
    """ 将参数集中的每个字典转为对象
        params 本身还是 dict

    Args:
        params (list[any]): 参数集
    
    Returns:
        dict: 字典
    """
    if not params:
        return None
    
    for key, value in params.items():
        if isinstance(value, dict):
            params[key] = dict_to_obj(value)
    return params

def obj_to_dict(obj):
    """ 对象转字典

    Args:
        obj: 任意对象

    Returns:
        dict: 包含对象属性的字典
    """
    if isinstance(obj, dict):
        return {k: obj_to_dict(v) for k, v in obj.items()}
    elif hasattr(obj, '__dict__'):
        return {k: obj_to_dict(v) for k, v in obj.__dict__.items() if not k.startswith('__')}
    elif isinstance(obj, (list, tuple, set)):
        return [obj_to_dict(item) for item in obj]
    else:
        return obj
    
# def assign(target, *sources):
#     """ 合并对象

#     Args:
#         target (_type_): _description_

#     Raises:
#         AttributeError: _description_

#     Returns:
#         _type_: _description_
#     """
#     for source in sources:
#         for key, value in source.items():
#             if hasattr(target, key):
#                 setattr(target, key, value)
#             else:
#                 raise AttributeError(f"'{target.__class__.__name__}' object has no attribute '{key}'")
#     return target

if __name__ == '__main__':
    import array
    import collections
    
    # 使用示例
    print(is_null(None))  # True
    print(is_null(""))  # True
    print(is_null("   "))  # True
    print(is_null([]))  # True
    print(is_null(set()))  # True
    print(is_null(()))  # True
    print(is_null([1, 2, 3]))  # False
    print(is_null(array.array('i', [1, 2, 3])))  # False
    print(is_null({'a': 1}))  # False