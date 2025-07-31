import ast
import json
import asyncio
import uvicorn
import platform

import numpy as np
import mxupy as mu

from peewee import Model
from datetime import datetime

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from playhouse.shortcuts import model_to_dict
from starlette.middleware.base import BaseHTTPMiddleware

from mxupy import IM, get_method, get_attr, singleton


class RequestTimerMiddleware(BaseHTTPMiddleware):
    """ 打印访问开始时间和结束时间，以及访问时长

    Args:
        BaseHTTPMiddleware (StreamingResponse): 响应流
    """

    async def dispatch(self, request: Request, call_next):

        st = datetime.now()
        response = await call_next(request)
        et = datetime.now()

        # 调用信息
        start_time_str = str(st)[:-3]
        end_time_str = str(et)[:-3]
        duration_str = str(et - st)[:-3]
        status_code_str = str(response.status_code)
        url_str = str(request.url)
        method_str = str(request.method)
        path_params_str = str(request.path_params)
        query_params_str = str(request.query_params)

        access_info = f'access_info:: start: {start_time_str} end: {end_time_str} duration: {duration_str}ms ' \
                      f'status_code: {status_code_str} url: {url_str} method: {method_str} ' \
                      f'path_params: {path_params_str} query_params: {query_params_str}'

        print(access_info)

        return response

@singleton
class ApiServer:
    """ 配置服务器信息，并开启服务，通过 api 路由执行底层函数
    """

    def __init__(self, config: dict = None):
        
        api_server = config
        print(api_server)

        # 域名、端口、ssl 证书
        self.host = api_server.get('host', '0.0.0.0')
        self.port = int(api_server.get('port', '80'))
        self.ssl_keyfile = api_server.get('ssl_keyfile', '')
        self.ssl_certfile = api_server.get('ssl_certfile', '')

        # 是否允许浏览器发送凭证信息（如 cookies）到服务器
        # 这里可以指定允许访问的源，可以是具体的域名或 '*'（表示允许所有源）
        # 允许的 HTTP 方法，例如 'GET', 'POST', 'PUT', 'DELETE', 等
        # 允许的 HTTP 头部信息
        self.allow_credentials = api_server.get('allow_credentials', True)
        self.allow_origins = api_server.get('allow_origins', ['*'])
        self.allow_methods = api_server.get('allow_methods', ['*'])
        self.allow_headers = api_server.get('allow_headers', ['*'])

        # 配置 CORS 中间件
        self.app = FastAPI()
        self.app.add_middleware(
            CORSMiddleware,
            allow_credentials=self.allow_credentials,
            allow_origins=self.allow_origins,
            allow_methods=self.allow_methods,
            allow_headers=self.allow_headers,
        )

        # 调试模式会打印访问的时间等信息
        self.debug = api_server.get('debug', True)

        # 文件缓存时长，单位（秒）
        self.access_file_max_age = api_server.get('access_file_max_age', 31536000)
        self.headers = {
            'Cache-Control': 'max-age=' + str(self.access_file_max_age)
        }
        
        # 可访问哪些扩展名的文件
        self.can_access_file_exts = api_server.get('can_access_file_exts', [''])
        # 可访问哪些类型的文件
        self.can_access_file_types = api_server.get('can_access_file_types', ['image','text'])
        
        self.sys_file_path = api_server.get('sys_file_path', 'E://')
        self.web_file_path = api_server.get('web_file_path', 'E://')
        self.user_file_path = api_server.get('user_file_path', 'E://')

    def handle_data(self, result):
        """ 处理函数返回的结果，转成字典让前端以 json 形式接收
            # [1] 结果类
            # [2] 数组
            # [3] 简单类型
        Args:
            Pydantic 默认只能序列化以下类型：
                基本类型（str, int, bool, float, None）
                dict, list, tuple, set 等容器类型（包含可序列化的数据）
                Pydantic 自己的 BaseModel 及其子类
                其他标准库类型（如 datetime, UUID）
                所以peewee中的Model对象无法被序列化，需要转换成dict
            result (any): 执行函数后返回的结果
        """
        match result:
            # [1] 处理 IM 类型
            case IM(data=data):
                im = result
                if isinstance(data, Model):
                    im.data = model_to_dict(data, recurse=False)
                elif isinstance(data, list):
                    im.data = [model_to_dict(i, recurse=False) if isinstance(i, Model) else i for i in data]
                else:
                    im.data = data
                return im
            
            # [2] 处理 Peewee 模型，返回字典
            case _ if isinstance(result, Model):
                return model_to_dict(result, recurse=False)
            
            # [3] 处理 NumPy 数组，返回列表
            case _ if isinstance(result, np.ndarray):
                return result.tolist()
            
            # [4] 处理列表（递归处理元素）
            case _ if isinstance(result, list):
                return [model_to_dict(i, recurse=False) if isinstance(i, Model) else i for i in result]
            
            # [5] 其他类型直接返回
            case _:
                return result

    def third_party_api(self, name):

        """ 检查函数是否是第三方接口

        Args:
            name (str): 函数名

        Returns:
            bool: 是否为第三方接口
        """
        if not name:
            raise Exception(IM(True, 'Module or function cannot be empty.', code=422))

        try:
            # [1] 获取函数
            method = get_method(name)
            if not method:
                raise Exception(IM(False, f"Module or function '{name}' not found.", code=404))
            
            # [2] 检查装饰器，是否为第三方接口
            if hasattr(method, '_third_party_api'):
                return True
            
            return False
                
        except Exception as e:
            raise Exception(IM(False, f"An error occurred: {e}, {mu.getErrorStackTrace()}", code=400))
        
    def skip_check_accesstoken(self, name):

        """ 是否跳过检查访问令牌

        Args:
            name (str): 函数名

        Returns:
            bool: 是否为第三方接口
        """
        if not name:
            raise Exception(IM(True, 'Module or function cannot be empty.', code=422))

        try:
            # [1] 获取函数
            method = get_method(name)
            if not method:
                raise Exception(IM(False, f"Module or function '{name}' not found.", code=404))
            
            # [2] 检查装饰器，是否跳过检查访问令牌
            # 有些函数是不需要检查访问令牌的，比如登录接口、注册接口
            # 在这些函数调用时令牌还不存在，所以没法校验
            if hasattr(method, '_skip_check_accesstoken'):
                return True
            
            return False
                
        except Exception as e:
            raise Exception(IM(False, f"An error occurred: {e}, {mu.getErrorStackTrace()}", code=400))


    def check_access(self, name, params, user = -1):
        """ 通过 函数名 和 参数集 访问 函数

        Args:
            name (str): 函数名
            params (obj): 参数集
            user (obj): 包含用户id、角色码、权限码

        Returns:
            IM: 结果类
        """
        im = IM()
        
        if user is not None:
            im = self.call('bigOAINet.db.safe.RuleControl.check_access', { 
                'functionName':name, 'params': params, 
                'user_id':user.user_id, 'user_roles':user.user_roles, 'user_rights':user.user_rights 
            })
            if im.error:
                return im

        return im

    def call(self, name, params, user_id = -1):

        """ 通过 函数名 和 参数集 访问 函数

        Args:
            name (str): 函数名
            params (obj): 参数集
            user_id (int): 用户ID，访问令牌中的用户id

        Returns:
            IM: 结果类
        """
        im = IM()
        if not name:
            return IM(True, 'Module or function cannot be empty.', code=422)

        try:
            # [1] 获取函数
            method = get_method(name)
            if not method:
                return IM(False, f"Module or function '{name}' not found.", code=404)
            
            # [2] 检查装饰器，如果有则注入访问令牌用户id
            if hasattr(method, '_accesstoken_user_id'):
                params = (params or {}) | {'user_id': user_id}
                
            # [3] 调用函数
            result = method(**params) if params else method()

            # [4] 处理结果
            im = self.handle_data(result)
        except Exception as e:
            im = IM(False, f"An error occurred: {e}, {mu.getErrorStackTrace()}")
            print(im)
            return im

        return im
    
    def call_for_bcpost(self, params: dict, request: Request = None) -> IM:
        """ 根据前端传过来的函数信息，执行相应的函数
            分 3 步：[1] 获取函数、[2] 执行函数、[3] 处理函数返回结果

        Args:
            params (dict): 函数信息
            request (Request, optional): 请求对象. Defaults to None.
        Returns:
            IM: 结果类
        """
        # 函数名、令牌
        name = get_attr(params, '___functionName')
        
        # 校验访问令牌
        im = mu.AccessToken().check(name, request)
        if not im.success:
            return im

        # 参数，将字典参数转为对象
        ps = {}
        for k, v in params.items():
            if not k.startswith('___'):
                ps[k] = v

        if self.debug:
            print('api_info:: ' + name + ' ' + str(ps))

        obj = mu.param_to_obj(ps)
        return self.call(name, obj)

    def call_for_get(self, name: str = None, params: str = None, request: Request = None) -> IM:
        """ 根据前端传过来的函数信息，执行相应的函数
            分 3 步：[1] 获取函数、[2] 执行函数、[3] 处理函数返回结果

        Args:
            name (str): 函数名 
            params (str): 参数集
            request (Request): 请求对象，包含令牌等信息

        Returns:
            IM: 结果类
        """
        # 校验访问令牌
        if not (im := mu.AccessToken().check(name, request)).success:
            return im
        
        if self.debug:
            print('api_info:: ' + name + ' ' + str(params))

        # 参数
        ps = None
        obj = None
        if params:
            # 将字符串转为对象
            ps = params.replace("{", '{"').replace(":", '":').replace(",", ',"')
            ps = ast.literal_eval(ps)
            obj = mu.param_to_obj(ps)

        return self.call(name, obj)

    async def call_for_post(self, name:str = Form(None), params: str = Form(None), request: Request = None) -> IM:
        """处理POST请求，执行指定函数
    
            分3步处理：
            1. 检查是否为微信支付回调（特殊处理）
            2. 验证访问令牌
            3. 执行目标函数并返回结果

            Args:
                name (str): 要调用的函数名
                params (str): JSON格式的参数字符串
                request (Request): FastAPI 请求对象，访问令牌存在其中

        Returns:
            IM: 统一返回结果对象

        Raises:
            无显式抛出异常，但内部可能抛出JSON解析错误等
        """
        # [1] 无参数处理
        if params in ('null', 'undefined', '', None):
            params = None
        
        # [2] 处理路由回调
        if self.third_party_api(name):
            obj = mu.param_to_obj({ "params": params })
            return self.call(name, obj)
        
        # [3] XSS 攻击
        name = mu.sanitize(name)
        params = mu.sanitize(params)
            
        # [4] 验证访问令牌
        accesstoken_user = None
        if not self.skip_check_accesstoken(name):
            if (im := mu.AccessToken().check(request)).error:
                return im
            # 包含 user_id、user_roles、user_rights
            accesstoken_user = mu.dict_to_obj(im.data)
        
        try:
            # [5] 参数转对象
            params_dict = json.loads(params) if params else {}
            obj = mu.param_to_obj(params_dict)
            
            # [6] 校验安全性
            if (im := self.check_access(name, obj, accesstoken_user)).error:
                return im
            
            # [7] 执行函数
            return self.call(name, obj, accesstoken_user.user_id if accesstoken_user else -1)
        except json.JSONDecodeError as e:
            return IM(False, f"参数解析失败: {str(e)}", None, 400)
        except Exception as e:
            print(f"函数调用出错: {str(e)}")
            return IM(False, f"执行出错: {str(e)}", None, 500)

    # 读取文件/上传文件
    def read_file(self, filename:str, type:str='user', userId:int = -1, sub_dir:str = '', responseType='content'):
        return mu.read_file(filename, type, userId, sub_dir, responseType)
    def upload_file(self, file:UploadFile = File(...), keep:bool = Form(True), override:bool = Form(False), sub_dir:str = Form(''), 
                    *, chunk_index:int = Form(-1), total_chunks:int = Form(1), 
                    userId:int = Form(...), access_token:str = Form(...)) -> IM:
        return mu.upload_user_file(file, keep, override, sub_dir, chunk_index=chunk_index, total_chunks=total_chunks, 
                    user_id=userId, access_token=access_token)

    def run(self, startupHandler=None, shutdownHandler=None):
        """ 运行 FastAPI
        """
        # 在 Windows 上，asyncio 需要使用特定的事件循环策略来处理套接字操作，
        # 否则可能会遇到 ConnectionResetError: [WinError 10054] 这样的错误
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        # 打印日志
        if self.debug:
            self.app.add_middleware(RequestTimerMiddleware)

        if startupHandler is not None:
            self.app.add_event_handler("startup", startupHandler)

        if shutdownHandler is not None:
            self.app.add_event_handler("shutdown", shutdownHandler)

        # 添加路由
        self.app.get('/api', response_model=None)(self.call_for_get)
        # responses 是为了支持微信等回调模式
        responses = { 200: {"content": { "application/json": {}, "application/xml": {} }} }
        self.app.post('/api', response_model=None, responses=responses)(self.call_for_post)
        self.app.post('/bcapi', response_model=None)(self.call_for_bcpost)
        self.app.get('/file', response_model=None)(self.read_file)
        self.app.post('/file', response_model=None)(self.upload_file)
        
        uvicorn.run(self.app, host=self.host, port=self.port, ssl_certfile=self.ssl_certfile, ssl_keyfile=self.ssl_keyfile)

if __name__ == '__main__':
    ApiServer().run()
