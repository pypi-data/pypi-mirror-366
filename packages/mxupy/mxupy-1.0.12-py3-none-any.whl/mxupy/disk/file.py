import os
import time
import json
import stat
import requests
import mimetypes

import mxupy as mu
import uuid as uid

from mxupy import IM
from requests.exceptions import RequestException

from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi import FastAPI, HTTPException, UploadFile, File, Form

def removeFileList(filePathList,prefix=""):
    for filePath in filePathList:
        removeFile(filePath,prefix)

def removeFile(filePath,prefix=""):
    rpath = prefix + filePath
    if os.path.exists(rpath):
        os.chmod(rpath, stat.S_IWRITE)
        os.remove(rpath)

def existsFile(filePath):
    if os.path.exists(filePath):
        return True
    return False

def existsFileList(filePathList,prefix=""):
    exists = []
    not_exists = []

    for filePath in filePathList:
        epath = prefix + filePath
        if os.path.exists(epath):
            exists.append(filePath)
        else:
            not_exists.append(filePath)
    return exists,not_exists

def fileParts(filename):
    """
    拆分文件路径，获取文件路径、文件名和扩展名。

    参数:
        filename (str): 要处理的文件路径字符串。

    返回:
        tuple: 文件路径、文件名和小写的扩展名组成的元组。
    """
    (filepath, tempfilename) = os.path.split(filename)
    (shotname, extension) = os.path.splitext(tempfilename)
    return filepath, shotname, extension.lower()


def readAllText(filename):
    """读取文本文件全部内容，注意文件编码必须是 utf-8

    Args:
        filename (string): 文件路径

    Returns:
        string: 文件内容
    """
    r = ''
    f = None
    try:
        f = open(filename, 'r', encoding='utf-8')
        r = f.read()
    except Exception as e:
        print(e)
    finally:
        if f:
            f.close()
    return r


def writeAllText(filename, content, mode='w'):
    """
    将文本内容写入文件。

    参数:
        filename (str): 要写入的文件路径。
        content (str): 要写入的文本内容。
        mode (str, 可选): 文件打开模式，默认为 'w'（写入模式）。
            'r'：只读模式。这是默认的模式。如果文件不存在，会抛出一个FileNotFoundError。
            'w'：写入模式。如果文件存在，会被覆盖。如果文件不存在，会创建一个新文件。
            'a'：追加模式。如果文件存在，写入的内容会被追加到文件末尾。如果文件不存在，会创建一个新文件。
            'b'：二进制模式。用于读写二进制文件。
            't'：文本模式。用于读写文本文件（这是默认的，通常可以省略）。
            '+'：更新模式。用于读写文件。如果与'r'、'w'或'a'结合使用，会打开文件用于更新（读写）。
        结合使用的例子：
            'r+'：读写模式。文件必须存在。
            'w+'：读写模式。如果文件存在，会被覆盖。如果文件不存在，会创建一个新文件。
            'a+'：读写模式。如果文件存在，写入的内容会被追加到文件末尾。如果文件不存在，会创建一个新文件。
            'x'：独占创建模式。用于写入。如果文件已存在，会抛出一个FileExistsError。
            'r+b'：读写二进制模式。文件必须存在。
            'w+b'：读写二进制模式。如果文件存在，会被覆盖。如果文件不存在，会创建一个新文件。
            'a+b'：读写二进制模式。如果文件存在，写入的内容会被追加到文件末尾。如果文件不存在，会创建一个新文件。

    返回:
        str: 写入文件的字符数。
    """
    r = ''
    f = None
    try:
        f = open(filename, mode, encoding='utf-8')
        r = f.write(content)
    except Exception as e:
        print(e)
    finally:
        if f:
            f.close()
    return r

def readJSON(filename):
    f = None
    try:
        f = open(filename, 'r', encoding='utf-8')
        return json.load(f)
    except Exception as e:
        print(e)
    finally:
        if f:
            f.close()
            
def writeJSON(filename, obj, mode='w'):
    f = None
    try:
        obj = mu.toSerializable(obj)

        f = open(filename, mode, encoding='utf-8')
        json.dump(obj, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(e)
    finally:
        if f:
            f.close()


def writeStream(filename, content, mode='wb'):
    """
    将二进制内容写入文件。

    参数:
        filename (str): 要写入的文件路径。
        content (bytes): 要写入的二进制内容。
        mode (str, 可选): 文件打开模式，默认为 'wb'（二进制写入模式）。

    返回:
        str: 写入文件的字符数。
    """
    r = ''
    f = None
    try:
        f = open(filename, mode)
        r = f.write(content)
    except Exception as e:
        print(e)
    finally:
        if f:
            f.close()
    return r


def clearAllText(filename):
    """
    清空文件内容。

    参数:
        filename (str): 要清空内容的文件路径。
    """
    open(filename, 'w').close()


def appendSuffix(file_path, suffix):
    # 分离文件名和扩展名
    file_dir, file_name_ext = os.path.split(file_path)
    file_name, file_ext = os.path.splitext(file_name_ext)

    # 添加后缀并重新构建文件路径
    new_file_path = os.path.join(file_dir, file_name + suffix + file_ext)

    return new_file_path

def ext_dict():
    """ 文件类型与扩展名的对应关系


    Returns:
        dict: 文件类型与扩展名字典
    """
    ext_dict = {
        'image': ['jpg', 'jpeg', 'png', 'gif', 'tiff', 'tif', 'bmp', 'tga', 'ico'],
        'office': ['doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'],
        'video': ['mp4', 'avi', 'mkv'],
        'audio': ['mp3', 'wav', 'ogg'],
        'text': ['txt', 'html', 'htm', 'shtml'],
        'code': ['js', 'py', 'cs'],
        'archive': ['zip', 'rar', '7z', 'tar', 'gz'],
        'pdf': ['pdf'],
        'database': ['db', 'sqlite', 'sql'],
        'presentation': ['key'],
        'vector': ['ai', 'eps', 'svg'],
        '3dmodel': ['obj', 'fbx', 'stl'],
        'spreadsheet': ['csv'],
        'font': ['otf', 'ttf'],
        'executable': ['exe', 'bat', 'sh'],
        'config': ['ini', 'cfg', 'json', 'xml'],
        'virtualmachine': ['vdi', 'vmdk', 'vhd']
    }
    return ext_dict

def file_exts_by_type(file_type):
    """ 通过文件类型获取对应的扩展名集

    Args:
        file_type (string): image、video、office 等

    Returns:
        list[string]: 扩展名集
    """
    return ext_dict().get(file_type, None)

def file_type(filename):
    """获取文件类型

    Args:
        filename (str): 文件名、路径、扩展名(如 .txt)

    Returns:
        str: 类型 image/office/...
    """
    _, _, ext = fileParts(filename)
    if ext == '':
        return None
    ext = ext[1:]
    
    # 将字典的键和值互换
    type_dict = {ext: type for type, exts in ext_dict().items() for ext in exts}
    return type_dict.get(ext, None)
    
def file_exists(filename):
    """ 文件是否存在

    Args:
        file_path (文件路径): 文件路径

    Returns:
        bool: 存在否
    """
    return os.path.exists(filename)

def file_name(filename, type='user', user_id=-1, sub_dir=''):
    """ 获取用户文件完整路径

    Args:
        filename (str): 文件名
        type (str): sys:系统，web:网站，user:用户（需提供用户id）
        user_id (int): 用户id
        sub_dir (str): 子目录

    Returns:
        str: 完整路径
    """
    if not mu.file_dir(type, user_id, sub_dir):
        return ''
    return mu.file_dir(type, user_id, sub_dir) + '\\' + os.path.basename(filename)
    
def file_exists_with_type(filename, type='user', user_id=-1, sub_dir=''):
    """ 用户文件是否存在

    Args:
        filename (str): 文件名
        type (str): sys:系统，web:网站，user:用户（需提供用户id）
        user_id (int): 用户id
        sub_dir (str): 子目录

    Returns:
        bool: 存在否
    """
    ufn = file_name(filename, type, user_id, sub_dir)
    return file_exists(ufn)
    
def can_access_file_exts():
    """ 用户可访问哪些文件类型
    

    Returns:
        list[str]: 用户可访问的文件集，['*']表示可访问任意类型的文件
    """
    # # 读取配置信息
    # api_server = mu.read_config().get('api_server', {})
    # # 可访问哪些扩展名的文件
    # exts = api_server.get('can_access_file_exts', [''])
    # # 可访问哪些类型的文件
    # types = api_server.get('can_access_file_types', ['image','text'])
    
    exts = mu.ApiServer().can_access_file_exts
    types = mu.ApiServer().can_access_file_types
    
        
    if exts == ['*'] or types == ['*']:
        return ['*']
    if types:
        for ty in types:
            exs = mu.file_exts_by_type(ty)
            if exs:
                exts.extend(exs)
                
    return exts
    
def can_access_file(filename):
    """ 按设置的扩展名，用户是否能访问此文件

    Args:
        filename (str): 文件名

    Returns:
        bool: 能访问否
    """
    exts = can_access_file_exts()
    if exts != ['*']:
        _, _, ext = mu.fileParts(filename)
        if not ext or ext[1:] not in exts:
            return False
    return True



def media_type(ext):
    """ 获取媒体类型

    Args:
        ext (str): 扩展名

    Returns:
        str: 媒体类型
    """
    types_map = mimetypes.types_map
    types_map['.apk'] = 'application/vnd.android.package-archive'
    types_map['.ts'] = 'video/MP2T'
    return mimetypes.types_map.get(ext)

def read_file(filename, type='user', user_id=-1, sub_dir='', responseType='content'):
    """ 读取用户文件

    Args:
        filename (str): 文件名
        type (str): sys:系统，web:网站，user:用户（需提供用户id）
        user_id (int): 用户id
        sub_dir (str): 子目录,可以多级，如：'avatar'、'avatar/thumbnail'
        responseType (str): text：文本内容、content：文件内容、file：下载

    Raises:
        HTTPException: 错误信息

    Returns:
        FileResponse: 文件信息或错误信息
    """
    if responseType not in ['text', 'content', 'file']:
        responseType = 'content'
    
    ca = can_access_file(filename)
    if not ca:
        raise HTTPException(status_code=415, detail='The requested file format is not allowed.')
    
    _, _, ext = fileParts(filename)
    ufn = file_name(filename, type, user_id, sub_dir)
    exi = file_exists(ufn)
    if exi:
        mt, hs = None, None
        if responseType == 'file':
            mt = media_type(ext)
            hs = {"Content-Disposition": f"attachment; filename={filename}"}
            
        elif responseType == 'content':
            return FileResponse(ufn, headers=hs, media_type=mt)
        
        elif responseType == 'text':
            return readAllText(ufn)
    else:
        raise HTTPException(status_code=404, detail="File not found.")

def upload_user_file(file:UploadFile, keep = True, override = False, sub_dir = '', *, chunk_index = -1, total_chunks = 1, user_id, access_token):
    """ 上传用户文件

    Args:
        file (UploadFile): 上传的文件
        keep (True): 是否保持原文件名
        override (bool, optional): 是否覆盖
        sub_dir (str): 子目录
        chunk_index (int, optional): 分片序号
            如果大于0，说明是分片进行上传，保存的时候需要将序号放在文件名后，最后一片进行合并
        total_chunks (int, optional): 总片数
        user_id (int): 用户id
        access_token (str): 访问令牌，在装饰器中进行校验

    Returns:
        IM: 上传结果
    """

    filename = file.filename
    ca = can_access_file(filename)
    if not ca:
        raise HTTPException(status_code=415, detail='The requested file format is not allowed.')
    
    up = mu.file_dir('user', user_id, sub_dir)
    os.makedirs(up, exist_ok=True)
    
    # basename：文件名.扩展名
    bn = filename
    if not keep:
        _, _, ext = mu.fileParts(filename)
        bn = uid.uuid4().hex + ext
        
    try:
        fn = up + '/' + bn
        if chunk_index >= 0:
            fn = f"{fn}_{chunk_index}"
        
        # 已经存在，且不覆盖
        if file_exists(fn) and not override:
            return IM(True, 'The file already exists.', bn)

        # 保存
        with open(fn, "wb") as f:
            f.write(file.file.read())
            f.close()
            
        # 权重和索引文件特殊处理
        # if ext == '.pth':
        #     shutil.copy(fn, os.path.join(module_dir, './RVC/assets/weights/'))
        # if ext == '.index':
        #     shutil.copy(fn, os.path.join(module_dir, './RVC/assets/indexes/'))
        
        finish = chunk_index + 1 == total_chunks
        if finish:
            im = combin_upload_file(bn, chunk_index + 1, user_id, sub_dir)
            if im.error:
                return im
            
        msg = 'The all files uploaded successfully.' if finish else 'The file uploaded successfully.'
        data = {
            'filename':bn,
            'chunk_index':chunk_index + 1,
            'total_chunks':total_chunks,
            'upload_progress' : ((chunk_index + 1) / total_chunks) * 100
        }
        return IM(True, msg, data, type='all' if finish else 'part')
    
    except Exception as e:
        print('API:upload_file error.', str(e))
        return IM(False, mu.getErrorStackTrace(), bn)
    
def combin_upload_file(filename, chunks, user_id, sub_dir = ''):
    """ 合并上传文件

    Args:
        filename (str): 文件名
        chunks (int): 分片数量
        user_id (int): 用户id
        sub_dir (str): 子目录
    """
    up = mu.file_dir('user', user_id, sub_dir)
    file_path = f"{up}/{filename}"
    
    # 存在否
    for i in range(int(chunks)):
        if not os.path.exists(f"{file_path}_{i}"):
            return 'The combination file not exists.'
    
    # 合并
    with open(file_path, 'wb') as out_file:
        for i in range(int(chunks)):
            with open(f"{file_path}_{i}", 'rb') as in_file:
                out_file.write(in_file.read())
    
    # 删除原始文件
    for i in range(int(chunks)):
        os.remove(f"{file_path}_{i}")
        
    return IM(True, 'The file combination was successful.', filename)

def upload_file_to_server(url, file_path, keep = True, override = False, *, user_id, access_token, sub_dir = ''):
    """ 从本地上传文件到服务器

    Args:
        url (str): 服务器地址，如：http://www.excample888.com/file
        file_path (str): 文件路径 如：'F:/T/1/1732264770.mp3'
        keep (True): 是否保持原文件名
        override (bool, optional): 是否覆盖
        user_id (int): 用户id
        access_token (str): 访问令牌，在装饰器中进行校验
        sub_dir (str): 子目录
    """
    # path = mu.file_dir('user', user_id, sub_dir)
    # path += "\\" + file_path
    
    data = {
        'keep': keep,
        'override': override,
        'chunk_index': -1,
        'total_chunks': 1,
        'userId': -1,
        'access_token': access_token,
        'sub_dir': sub_dir
    }
    
    # 打开文件，准备上传
    with open(file_path, 'rb') as file:
        files = {'file': (file_path, file)}
        try:
            response = requests.post(url, files=files, data=data)
            if response.status_code == 200:
                return IM().from_dict(response.json())
            else:
                return IM(False, response.text, response.text, response.status_code)
        except Exception as e:
            return IM(False, '', e)

def download_file_from_server(url: str, save_path: str):
    """
    从服务器下载文件到本地，自动创建所需目录
    
    参数:
        url (str): 要下载的文件URL
        save_path (str): 本地保存路径（包含文件名）
    
    返回:
        IM对象: 包含操作结果（成功/失败）和相关信息
    """
    try:
        # 1. 自动创建目标目录
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # 2. 发起HTTP GET请求，stream=True启用流式下载
        with requests.get(url, stream=True) as response:
            # 检查HTTP状态码，如果是4XX/5XX会抛出HTTPError异常
            response.raise_for_status()  
            
            # 3. 以二进制写入模式打开文件
            with open(save_path, 'wb') as file:
                # 分块读取内容，chunk_size=8192表示每次读取8KB
                for chunk in response.iter_content(chunk_size=8192):
                    # 过滤掉空的chunk
                    if chunk:
                        file.write(chunk)
        
        # 返回成功结果
        return IM(True, 'Download completed.', save_path)
    
    # 异常处理部分
    except RequestException as e:
        # 处理网络相关错误（连接超时、DNS解析失败、HTTP错误等）
        return IM(False, f'Network error: {str(e)}')
    except IOError as e:
        # 处理文件IO错误（权限不足、磁盘空间不够等）
        return IM(False, f'File write error: {str(e)}')
    except Exception as e:
        # 处理其他未预料到的错误
        return IM(False, f'Unexpected error: {str(e)}')
