# import importlib

# from peewee import ModelBase
# from playhouse.shortcuts import ReconnectMixin
# from playhouse.pool import PooledMySQLDatabase
# import mxupy as mu

import ast
from peewee import SqliteDatabase, ModelBase
from playhouse.shortcuts import ReconnectMixin
from playhouse.pool import PooledMySQLDatabase
import mxupy as mu


class ReconnectPooledMySQLDatabase(ReconnectMixin, PooledMySQLDatabase):
    """ 提供 MySql 数据库重连支持
        这是一个 mixin 类，用于提供自动重连功能。当数据库连接失败时，ReconnectMixin会尝试重新建立连接。
        这对于处理网络波动或数据库服务重启导致的连接中断非常有用。
        通过继承 ReconnectMixin，ReconnectPooledMySQLDatabase 类将获得自动重连的能力。

    Args:
        ReconnectMixin (ReconnectMixin): 
            这是一个 mixin 类，用于提供自动重连功能。当数据库连接失败时，ReconnectMixin会尝试重新建立连接。
            这对于处理网络波动或数据库服务重启导致的连接中断非常有用。
            通过继承 ReconnectMixin，ReconnectPooledMySQLDatabase 类将获得自动重连的能力。

        PooledMySQLDatabase (_type_): 
            这是peewee库中的一个类，用于创建一个连接池，管理对MySQL数据库的连接。
            使用连接池可以提高数据库操作的性能，因为它允许复用现有的数据库连接，而不是每次操作都创建新的连接。
            PooledMySQLDatabase接受数据库连接参数（如主机名、用户名、密码等），并管理一个连接池，使得应用程序可以高效地执行数据库查询。

    """
    pass

class DatabaseHelper:
    """ 数据库
    """

    @staticmethod
    def get_cache_size(config):
        """ 获取缓存大小
        """
        cache_str = str(config.get('cache_size', '-64 * 1024 * 1024'))
        
        if cache_str.lstrip('-').isdigit():
            return int(cache_str)
        
        # 否则尝试安全计算表达式
        try:
            return ast.literal_eval(cache_str)
        except (ValueError, SyntaxError):
            return -64 * 1024 * 1024
        
    @staticmethod
    def init():
        """Initialize DatabaseHelper from configuration dictionary
        
        Returns:
            tuple: (DatabaseHelper instance, database connection)
        """
        dh = None
        config = mu.read_config().get('database', {})
        db_type = config.get('type', 'mysql')
        
        if db_type.lower() == 'mysql':
            
            name = config.get('name', '')
            username = config.get('username', 'root')
            password = config.get('password', '')
            host = config.get('host', '127.0.0.1')
            port = int(config.get('port', '3306'))

            charset = config.get('charset', 'utf8')
            max_connections = int(config.get('max_connections', '100000'))
            stale_timeout = int(config.get('stale_timeout', '60'))
            timeout = int(config.get('timeout', '60'))
            auth_plugin_map = config.get('auth_plugin_map', 'caching_sha2_password')
            
            dh = DatabaseHelper(
                db_type=db_type,
                
                name=name,
                username=username,
                password=password,
                host=host,
                port=port,
                charset=charset,
                stale_timeout=stale_timeout,
                timeout=timeout,
                max_connections=max_connections,
                auth_plugin_map=auth_plugin_map
            )
            
        elif db_type.lower() == 'sqlite':
            
            path = config.get('path', ':memory:')
            journal_mode = config.get('journal_mode', 'wal')
            cache_size = DatabaseHelper.get_cache_size(config)
            
            foreign_keys = int(config.get('foreign_keys', '1'))
            ignore_check_constraints = int(config.get('ignore_check_constraints', '0'))
            synchronous = int(config.get('synchronous', '0'))
            
            pragmas = {
                'journal_mode': journal_mode,
                'cache_size': cache_size,
                'foreign_keys': foreign_keys,
                'ignore_check_constraints': ignore_check_constraints,
                'synchronous': synchronous,
            }
            
            dh = DatabaseHelper(
                db_type=db_type,
                path=path,
                pragmas=pragmas,
            )
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

        return dh.db, dh

    def __init__(self, name='', db_type = 'mysql', username = '', password = '', host='127.0.0.1', port=3306, 
                 charset='utf8', max_connections=100000, stale_timeout=60, timeout=60, auth_plugin_map='caching_sha2_password', 
                 path='', pragmas = None):
        """ 连接数据库
        Args:
            name (str): 库名,如果是 Sqlite 数据库,则是数据库文件路径
            db_type (str, optional): 数据库类型,默认 mysql
            username (str): 用户名
            password (str): 密码
            host (str, optional): 地址
            port (int, optional): 端口
            charset (str, optional): 编码
            max_connections (int, optional): 最大连接数
            stale_timeout (int, optional): 空闲时长（秒）
                这个参数定义了连接池中连接的最大空闲时间。
                如果一个连接在连接池中空闲超过这个时间，它将被认为是“陈旧的”（stale），并且会被自动关闭和从连接池中移除。
                stale_timeout有助于防止使用过时的连接，这些连接可能因为长时间空闲而变得不稳定或不再有效。
                如果stale_timeout设置为None，则连接不会自动因为空闲时间过长而被关闭。
            timeout (int, optional): 超时时长（秒）
                这个参数定义了从连接池请求一个连接时的超时时间。
                如果连接池中没有可用的连接，并且达到了最大连接数限制，那么请求者会等待直到超时。
                如果timeout设置为0，则表示请求者会无限期等待，直到连接池中有可用的连接。
                如果timeout设置为一个正数，那么在指定的时间内如果没有可用连接，请求者会收到一个超时异常。
            auth_plugin_map (str, optional): 认证插件映射
                特性	        mysql_native_password	caching_sha2_password	sha256_password
                加密算法	    SHA1	                SHA256	                SHA256
                默认版本	    MySQL≤5.7	            MySQL≥8.0	            无
                需要SSL	        否	                    可选	                是
                性能	        高	                    高(有缓存)	            较低
                推荐使用	    不推荐	                推荐	                特定场景
                通过 sql 脚本 SELECT user, host, plugin FROM mysql.user WHERE user = '你的用户名'; 可以查看当前用户的认证插件映射。
            pragmas (dict, optional): Sqlite 数据库连接参数
                journal_mode: 'wal'
                    作用：设置 SQLite 的日志模式（事务日志机制）
                        wal (Write-Ahead Logging)：写入前先写日志，支持读写并发，性能更好（推荐）
                        delete (默认)：事务提交后删除回滚日志
                        truncate：类似 delete 但用文件截断代替删除
                        persist：保留日志文件但清空内容
                        memory：日志仅存内存（不安全，崩溃可能丢数据）
                cache_size: -1024 * 64
                    作用：设置 SQLite 内存缓存大小（单位：字节）
                    -1024 * 64 = -65,536 → 表示 64KB 缓存
                    （负值表示字节数，会自动按页大小换算为页数）
                    建议：
                        普通应用推荐 -64 * 1024 * 1024（64MB）
                        嵌入式设备可设为 -1024 * 1024（1MB）
                foreign_keys: 1
                    作用：启用/禁用外键约束
                        1：启用外键约束（默认关闭，需显式开启！）
                        0：禁用外键约束
                ignore_check_constraints: 0
                    作用：忽略 CHECK 约束
                        1：忽略 CHECK 约束（默认关闭，需显式开启！）
                        0：不忽略 CHECK 约束
                synchronous: 0
                    0 (OFF)：完全不等待磁盘写入（最快，但崩溃可能丢数据)
                    1 (NORMAL)：关键操作同步（平衡模式，推荐大多数场景）
                    2 (FULL)：完全同步（最安全，但性能差）
                    
            # 没有找到下列参数
            reconnect_timeout (int, optional): 重连超时时间（秒）
            max_retries (int, optional): 最大重连次数
            initial_delay (int, optional): 初始延迟时间（秒）
            max_delay (int, optional): 最大延迟时间（秒）
            backoff (int, optional): 重连尝试之间的等待时间翻倍
            
        """
        self.db_type = db_type
        if db_type == 'mysql':
            self._db = ReconnectPooledMySQLDatabase(
                database=name,
                user=username,
                password=password,
                host=host,
                port=port,
                charset=charset,
                max_connections=max_connections,
                stale_timeout=stale_timeout,
                timeout=timeout,
                auth_plugin_map=auth_plugin_map
            )
        elif db_type == 'sqlite':
            self._db = SqliteDatabase(
                database=path,
                pragmas=pragmas
            )

    @property
    def db(self):
        """ 数据库实例

        Returns:
            ReconnectPooledMySQLDatabase: 拥有重连功能的数据库实例
        """
        return self._db

    def connect(self, reuse_if_open=False):
        """ 连接数据库

        Args:
            reuse_if_open (bool, optional): 
                True：当尝试建立新的数据库连接时，如果池中已经有一个打开的连接，那么这个打开的连接会被重用，而不是创建一个新的连接。
                False：即使池中已经有打开的连接，也会尝试创建一个新的连接。
                对于 MySQL 有效，SQLite 会忽略这个参数。
        """
        if self._db:
            if self.db_type == 'mysql':
                self._db.connect(reuse_if_open)
            elif self.db_type == 'sqlite':
                self._db.connect()

    def close(self):
        """ 关闭数据库连接

        """
        if self._db:
            self._db.close()

    def get_database_type(self):
        """ 获取当前数据库类型
        
        Returns:
            str: 'mysql' 或 'sqlite'
        """
        return self.db_type
    

        