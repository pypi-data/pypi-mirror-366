import os
import hashlib
from pathlib import Path
import platform
import magic.magic


def list_files_in_folder(folder_path: str):
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            raise Exception(f"path {folder_path} is not a dir or does not exist")
    folder_path = os.path.abspath(folder_path)
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if not is_hidden(os.path.join(root, d))]
        for file in files:
            file_path = os.path.join(root, file)
            if not is_hidden(file_path):
                file_list.append(file_path)
    return file_list
            
        
    

def get_file_content(file_name):
    with open(file_name, encoding='utf-8') as f:
        content = f.read()
    return content


def sha256(file_path: str, buf_size: int = 131072):
    if not Path(file_path).is_file():
        raise Exception(f"file {file_path} does not exist")
    sha256_obj = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            data = f.read(buf_size)
            if not data:
                break
            sha256_obj.update(data)
    return sha256_obj.hexdigest()


def is_hidden(filepath):
    """
    跨平台判断文件是否为隐藏文件
    """
    path = Path(filepath)
    
    # Unix/Linux/macOS: 检查文件名是否以.开头
    if platform.system() != 'Windows':
        return path.name.startswith('.')
    
    # Windows: 检查文件属性
    else:
        try:
            import ctypes
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
            return attrs != -1 and bool(attrs & 2)  # FILE_ATTRIBUTE_HIDDEN = 2
        except (ImportError, AttributeError):
            # 如果无法使用Windows API，则回退到检查文件名
            return path.name.startswith('.')
        




def get_file_type_by_magic(file_path):
    import locale
    locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
    
    # 创建 magic 对象
    mime = magic.magic.Magic(mime=True)
    try:
        # 首先尝试直接使用文件路径
        file_type = mime.from_file(file_path)
        if 'cannot open' in file_type:
            raise Exception(f"magic 无法读取文件: {file_path}")
        return file_type
    except Exception as e:
        print(f"获取文件MIME出错: {e}")
        return "application/octet-stream"