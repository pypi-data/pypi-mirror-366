import hmac

from jose import jwt
from typing import Optional
from cachetools import TTLCache
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Request

from mxupy import IM, singleton, dict_to_obj

@singleton
class AccessToken:
    """ 令牌管理类
    """
    def __init__(self, config: dict = None):
        self.config = dict_to_obj(config)
        # print(config)
        
        self.check_token = True
        # 没配置，不校验令牌
        if not config:
            self.check_token = False
            return
        
        self.token_cache = TTLCache(maxsize=self.config.cache_max_size, ttl=self.config.cache_ttl)
    
    def create(self, user_id: int, roles: Optional[list] = None, rights: Optional[list] = None):
        """ 生成令牌

        Args:
            user_id (int): 用户id
            roles (Optional[list], optional): 角色列表. Defaults to None.
            rights (Optional[list], optional): 权限列表. Defaults to None.

        Returns:
            str: 令牌
        """
        if not self.check_token:
            return ''
        
        atc = self.config
        
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "exp": now + timedelta(seconds=atc.expire_seconds),
            "iat": now,
            "roles": roles or [],
            "rights": rights or [],
            "iss": atc.issuer,
            "aud": atc.audiences
        }
        t = jwt.encode(payload, atc.secret, algorithm=atc.algorithm)
        self.token_cache[user_id] = t
        
        return t
    
    def decode(self, token: str) -> IM:
        """ 解析令牌

        Args:
            token (str): 令牌

        Returns:
            int: 用户id
        """
        
        if not self.check_token:
            return IM()
        
        config = self.config
        
        try:
            payload = jwt.decode(
                token,
                config.secret,
                algorithms = [config.algorithm],
                issuer = config.issuer,
                # 老版本不支持数组
                audience = config.audiences[0] if len(config.audiences) >= 1 else None
            )
            
            # 从令牌中获取用户id、角色列表、权限列表
            user_id = payload.get("sub")
            user_roles = payload.get("roles")
            user_rights = payload.get("rights")
            
            data = {
                "user_id": int(user_id),
                "user_roles": user_roles,
                "user_rights": user_rights,
                "token": token
            }
            
            return IM(True, 'success', data)
        
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
        
    def check(self, request: Request) -> IM:


        """ 校验令牌

        Args:
            request (Request): 请求对象，包含令牌等信息

        Returns:
            IM: 结果类
        """
        
        if not self.check_token:
            return IM()

        # 获取token
        authorization = request.headers.get("Authorization")
        token = authorization[7:] if authorization and authorization.startswith("Bearer ") else None
        
        if not token:
            return IM(False, 'Missing or invalid token', None, status.HTTP_401_UNAUTHORIZED)
        
        # 解析令牌
        im = self.decode(token)
        if im.error:
            return im
        user_id = im.data.get('user_id')
        user_roles = im.data.get('user_roles')
        user_rights = im.data.get('user_rights')
        
        # 从缓存中获取令牌
        t = self.token_cache.get(int(user_id), '')
        if hmac.compare_digest(token, t):
            return IM(data={"user_id": user_id, "user_roles": user_roles, "user_rights": user_rights})
        
        if user_id is None:
            return IM(False, 'Invalid token payload', None, status.HTTP_401_UNAUTHORIZED)
        
        return IM(False, 'The token is invalid.', None, status.HTTP_401_UNAUTHORIZED)
        
    def remove(self, user_id: int) -> IM:
        """ 删除令牌

        Args:
            user_id (int): 用户id

        Returns:
            IM: 结果类
        """
        try:    
            self.token_cache.pop(user_id)
        except KeyError:
            pass
        
        return IM(True, '', {"user_id": user_id}, status.HTTP_200_OK)
        
    